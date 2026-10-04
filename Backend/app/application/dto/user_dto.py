from dataclasses import dataclass

@dataclass
class User_query_dto:
    email:str
    name:str
    password:str

@dataclass
class User_response_dto:
    id:str
    name:str
    email:str
