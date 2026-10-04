from dataclasses import dataclass

@dataclass
class Transaction_query_dto:
    Order_id: str
    Payment_id:str
    Amount_paid:str
    Payment_date:str
    Account_name:str
    Reason_for_refund:str
    Creator_id:str


@dataclass
class Transaction_response_dto:
    Order_id: str
    Payment_id:str
    Amount_paid:str
    Payment_date:str
    Account_name:str
    Reason_for_refund:str