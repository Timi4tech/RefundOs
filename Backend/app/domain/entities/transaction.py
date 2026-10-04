from dataclasses import dataclass
from app.domain.enums.transaction import Transaction_status

@dataclass
class Transaction:
    id:str
    Order_id: str
    Payment_id:str
    Amount_paid:float
    Account_name:str
    Transaction_status:Transaction_status
    Creator_id:str

