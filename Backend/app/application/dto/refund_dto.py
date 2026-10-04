from dataclasses import dataclass
from app.domain.enums.refund import Refund_status

@dataclass
class Refund_ticket_query_dto:
    Order_id: str
    Payment_id:str
    Amount_paid:str
    Payment_date:str
    Account_name:str
    Reason_for_refund:str
    Refund_status:Refund_status
    Creator_id:str


@dataclass
class Refund_ticket_response_dto:
    Order_id: str
    Payment_id:str
    Amount_paid:str
    Payment_date:str
    Account_name:str
    Refund_status:Refund_status
    Reason_for_refund:str