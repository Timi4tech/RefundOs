from dataclasses import dataclass
from app.domain.enums.user import Role

@dataclass
class User:
    id: str
    email:str
    name:str
    role:Role
    password: str

