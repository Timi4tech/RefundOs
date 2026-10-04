from dataclasses import dataclass
from app.domain.enums.refund import Refund_status

@dataclass
class Refund:
    id:str
    Order_id: str
    Payment_id:str
    Amount_paid:float
    Payment_date:str
    Account_name:str
    Reason_for_refund:str
    Refund_status:Refund_status
    Refund_decision: str
    Creator_id:str
    Created_date:str
    Created_time:str

