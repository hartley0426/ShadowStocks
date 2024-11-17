import random
import datetime
from utilities import utils

class Item:

    name: str
    cost: float
    short_description: str
    description: str
    image: str

    def __init__(self, name: str, cost: float, short_description: str, description: str, image: str) -> None:
        self.name = name
        self.cost = cost
        self.description = description
        self.short_description = short_description
        self.image = image

    def GetName(self) -> str:
        return self.name
    
    def GetShortDesc(self) -> str:
        return self.short_description

    def GetCost(self) -> float:
        return self.cost
    
    def GetDesc(self) -> str:
        return self.description
    
    def GetImage(self) -> str:
        return self.image


        

Items = {
    'apple': Item(
        name="Apple",
        short_description="A basic apple. What did you expect?",
        description="A basic apple bought from your local market. What were you expecting?",
        cost=1.00,
        image="https://hartley0426.github.io/ShadowStocks/assets/itemimages/apple-whole.png"
    ),
    'notebook': Item(
        name="Notebook",
        short_description="A notebook from your local supplies store.",
        description="A notebook that can be used in your everyday life. You may need it for school, or just to write some stuff down.",
        cost=4,
        image="https://hartley0426.github.io/ShadowStocks/assets/itemimages/journal.png"
    ),
    'car': Item(
        name="Car",
        short_description="Some random car",
        description="A basic car you found on the side of the road, needs some fixing",
        cost=1500,
        image="https://hartley0426.github.io/ShadowStocks/assets/itemimages/car-side.png"
    )
}
