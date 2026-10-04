import json
from aio_pika.abc import AbstractIncomingMessage
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.infrastructure.database import AsyncSessionLocal, Refund, Transaction, AuditLog
from app.infrastructure.messaging.rabbitmq import rabbitmq_client
from app.domain.Policies.refund_policy import RefundPolicy
from app.domain.enums.refund import RefundStatus
from app.application.dto.ai_dto import RefundWorkerDecision, RefundWorkerRequest

class RefundConsumer:
    async def start(self):
        await rabbitmq_client.connect()
        await rabbitmq_client.consume(self.handle_message)

    async def handle_message(self, message: AbstractIncomingMessage):
        payload: dict = {}
        try:
            payload=json.loads(message.body.decode("utf-8"))
            reply_to=str(payload.get("reply_to","")).strip()
            if not reply_to: raise ValueError("Invalid refund request payload: reply_to is required.")
            request=RefundWorkerRequest.model_validate(payload)
            async with AsyncSessionLocal() as session:
                # Lock the transaction while checking for duplicate/refund state so two
                # simultaneous messages cannot both create an automatic refund.
                transaction=await session.scalar(
                    select(Transaction).where(Transaction.id==request.transaction_id).with_for_update()
                )
                if transaction is None or transaction.user_id != request.user_id:
                    result=RefundWorkerDecision(request_id=request.request_id,decision="REJECT",status="REJECTED",message_context="The transaction could not be found for the authenticated customer.",transaction_status=None,requested_amount=request.amount,policy_note="Transaction not found or ownership could not be verified.")
                else:
                    existing=await session.scalar(select(Refund).options(selectinload(Refund.transaction)).where(Refund.request_id==request.request_id))
                    if existing:
                        decision=self._decision_from_existing(existing)
                        result=RefundWorkerDecision(request_id=request.request_id,decision=decision,status=existing.status.value,message_context="An existing refund request was found for this request ID.",refund_id=existing.id,ticket_created=True,transaction_status=transaction.status.value,requested_amount=existing.amount,approved_amount=existing.amount if decision=="APPROVE" else None,policy_note=existing.decision)
                    else:
                        amount=request.amount if request.amount is not None else transaction.amount
                        if amount <= 0: raise ValueError("Refund amount must be greater than zero.")
                        if amount > transaction.amount:
                            result=RefundWorkerDecision(request_id=request.request_id,decision="REJECT",status="REJECTED",message_context="The requested refund amount is greater than the transaction amount.",transaction_status=transaction.status.value,requested_amount=amount,policy_note="Requested amount exceeds transaction amount.")
                        elif transaction.refunded:
                            result=RefundWorkerDecision(request_id=request.request_id,decision="REJECT",status="REJECTED",message_context="This transaction has already been refunded.",transaction_status=transaction.status.value,requested_amount=amount,policy_note="Transaction already refunded.")
                        else:
                            active=await session.scalar(select(Refund).where(Refund.transaction_id==transaction.id,Refund.status.in_([RefundStatus.PENDING,RefundStatus.PROCESSING,RefundStatus.APPROVED,RefundStatus.REQUIRES_REVIEW])).order_by(Refund.created_at.desc()).limit(1))
                            if active:
                                result=RefundWorkerDecision(request_id=request.request_id,decision="REVIEW",status=active.status.value,message_context="An active refund request already exists for this transaction.",refund_id=active.id,ticket_created=True,transaction_status=transaction.status.value,requested_amount=active.amount,policy_note="Duplicate active refund request.")
                            else:
                                refund=Refund(request_id=request.request_id,order_id=transaction.order_id,account_name=transaction.account_name,user_id=request.user_id,transaction_id=transaction.id,amount=amount,reason=request.reason.strip(),status=RefundStatus.PROCESSING)
                                session.add(refund); await session.flush()
                                session.add(AuditLog(refund_id=refund.id,actor_type="SYSTEM",action="REFUND_TICKET_CREATED",note="Refund ticket created by the refund worker before deterministic policy evaluation.",metadata_json={"request_id":request.request_id,"transaction_status":transaction.status.value,"amount":str(amount)}))
                                policy_result=RefundPolicy.evaluate(amount,transaction.status,request.reason.strip(),transaction_created_at=transaction.created_at,final_sale=bool(transaction.final_sale))
                                refund.status=policy_result.status
                                refund.decision=policy_result.decision
                                if policy_result.decision=="APPROVE": transaction.refunded=True
                                session.add(AuditLog(refund_id=refund.id,actor_type="SYSTEM",action="REFUND_PROCESSED",note=policy_result.note,metadata_json={"decision":policy_result.decision,"request_id":request.request_id,"final_sale":bool(transaction.final_sale),"transaction_created_at":transaction.created_at.isoformat()}))
                                await session.commit()
                                result=RefundWorkerDecision(request_id=request.request_id,decision=policy_result.decision,status=policy_result.status.value,message_context=policy_result.note,refund_id=refund.id,ticket_created=True,transaction_status=transaction.status.value,requested_amount=amount,approved_amount=amount if policy_result.decision=="APPROVE" else None,policy_note=policy_result.note)
                if not session.in_transaction():
                    pass
                else:
                    await session.commit()
            await rabbitmq_client.publish_refund_decision(reply_to,result.model_dump(mode="json"))
            await message.ack()
        except ValueError as exc:
            await self._safe_error_response(message,payload,str(exc),decision="ERROR",status="FAILED")
            await message.reject(requeue=False)
        except Exception:
            await message.reject(requeue=True)

    @staticmethod
    def _decision_from_existing(refund: Refund) -> str:
        explicit=str(refund.decision or "").upper().strip()
        if explicit in {"APPROVE","REJECT","REVIEW"}: return explicit
        if refund.status in {RefundStatus.APPROVED,RefundStatus.COMPLETED}: return "APPROVE"
        if refund.status==RefundStatus.REJECTED: return "REJECT"
        return "REVIEW"

    async def _safe_error_response(self,message,payload,note,*,decision,status):
        reply_to=str(payload.get("reply_to","")).strip(); request_id=str(payload.get("request_id","")).strip()
        if not reply_to or not request_id: return
        result=RefundWorkerDecision(request_id=request_id,decision=decision,status=status,message_context=note,policy_note=note)
        await rabbitmq_client.publish_refund_decision(reply_to,result.model_dump(mode="json"))
