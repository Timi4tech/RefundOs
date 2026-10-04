from enum import Enum
class Role(str, Enum):
    CUSTOMER = "CUSTOMER"
    DEVELOPER = "DEVELOPER"
    ADMIN = "ADMIN"
