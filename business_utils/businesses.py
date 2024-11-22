class Business:
    name: str
    cost: float
    pay: float
    description: str

    def __init__(self, name:str, cost: float, pay: float, description: str):
        self.name = name
        self.cost = cost
        self.pay = pay
        self.description = description

    def get_name(self) -> str:
        return self.name
    
    def get_cost(self) -> float:
        return self.cost
    
    def get_pay(self) -> float:
        return self.pay
    
    def get_description(self) -> str:
        return self.description
    
Businesses = {
    "sshop": Business(
        name="Small Shop",
        description="A small hometown shop. Maybe you sell hobby stuff",
        cost=40000,
        pay=440
    ),
    "mshop": Business(
        name="Medium Shop",
        description="A small regional shop chain. Pretty Stable",
        cost=493824,
        pay=5432
    ),
    "lshop": Business(
        name="Large Shop",
        description="A large statewide shop. Very useful",
        cost=6096553,
        pay=67062
    ),
    "mshop": Business(
        name="Megastore Chain",
        description="A large national chain. You are known worldwide.",
        cost=75265604,
        pay=827921
    ),
}