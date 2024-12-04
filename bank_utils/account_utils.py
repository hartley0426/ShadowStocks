from datetime import datetime

class AccountType:
    SAVINGS = "savings"
    CHECKING = "checking"

class Account:
    def __init__(self, name: str, balance: float, type: str, last_action: datetime) -> None:
        self.name = name
        self.balance = balance
        self.type = type
        self.last_action = last_action

    def get_name(self) -> str:
        return self.name
    
    def get_balance(self) -> float:
        return self.balance
    
    def get_type(self) -> str:
        return self.type

    def set_balance(self, balance: int) -> None:
        self.balance = balance 

    def get_action(self) -> datetime:
        return self.last_action

    @staticmethod
    def from_dict(data: dict) -> "Account":
        return Account(
            name=data["name"],
            balance=data["balance"],
            type=data["type"],
            last_action=datetime.fromisoformat(data["last_action"])
        )
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "balance": self.balance,
            "type": self.type,
            "last_action": self.last_action.isoformat() 
        }
    
    def set_last_action(self, dt: datetime) -> None:
        self.last_action = dt