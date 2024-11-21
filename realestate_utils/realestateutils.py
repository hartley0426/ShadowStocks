import random
import datetime
from utilities import utils

class Property:

    cost: float
    location: str
    description: str
    image: str
    pay: float

    def __init__(self, cost: float, location: str, description: str, image: str, pay: float) -> None:
        self.cost = cost
        self.description = description
        self.location = location
        self.image = image
        self.pay = pay

    def GetLocation(self) -> str:
        return self.location
    
    def GetPay(self) -> float:
        return self.pay

    def GetCost(self) -> float:
        return self.cost
    
    def GetDesc(self) -> str:
        return self.description
    
    def GetImage(self) -> str:
        return self.image


        

Properties = {
    'house_1': Property(
        location="Bodie, United States",
        pay=517,
        description="A small miners shack in the historic ghost-town of Bodie.",
        cost=47000,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_4.jpg"
    ),
    'house_2': Property(
        location="Karwendelgebirge, Austria",
        pay=572,
        description="A small cabin in a private valley in Austria.",
        cost=52000,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_18.jpg"
    ),
    'house_3': Property(
        location="San Jose, United States",
        pay=1232,
        description="A suburan house in the middle of the city.",
        cost=112000,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_2.jpg"
    ),
    'house_4': Property(
        location="Lake Ullswater, United Kingdom",
        pay=2206.05,
        description="A house with an overview of the water. Previously a boathouse.",
        cost=200550,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_11.jpg"
    ),
    'house_5': Property(
        location="Pittson, United States",
        pay=2195,
        description="A house in the middle of Pittsburg",
        cost=219500,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_12.jpg"
    ),
    'house_6': Property(
        location="Indian Land, United States",
        pay=6239.20,
        description="A house on a large piece of land, has a pond.",
        cost=567200,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_5.jpg"
    ),
    'house_7': Property(
        location="Boligsalgsrapport, Norway",
        pay=7517.95,
        description="Peaceful house with a great view.",
        cost=683450,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_1.jpg"
    ),
    'house_8': Property(
        location="Coconut Creek, United States",
        pay=8626.86,
        description="A large house with quick access to the beach.",
        cost=784260,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_6.jpg"
    ),
    'house_9': Property(
        location="Flower Mound, United States",
        pay=15314.86,
        description="A large house with a large pool, and access to a large lake.",
        cost=1392260,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_8.jpg"
    ),
    'house_10': Property(
        location="Beaumont, United States",
        pay=19700.45,
        description="A large manor on a large plot of land.",
        cost=1790950,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_13.jpg"
    ),
    'house_11': Property(
        location="Ringgold, United States",
        pay=30747.97,
        description="A large mansion in a private complex",
        cost=2795270,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_17.jpg"
    ),
    'house_12': Property(
        location="Ware, United Kingdom",
        pay=43507.97,
        description="A large complex of a decomissioned hotel.",
        cost=3955270,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_10.jpg"
    ),
    'house_13': Property(
        location="Dresden, Germany",
        pay=58062.18,
        description="A refurnished castle",
        cost=5278380,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_15.jpg"
    ),
    'house_14': Property(
        location="Fulda, Germany",
        pay=71910.34,
        description="A refurnished royal mansion that was put out of use.",
        cost=6537340,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_9.jpg"
    ),
    'house_15': Property(
        location="Antholzertal, Italy",
        pay=85755.01,
        description="A mansion positioned on a private lake surrounded by mountains.",
        cost=7795910,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_7.jpg"
    ),
    'house_16': Property(
        location="Toulan, France",
        pay=99592.68,
        description="A mansion positioned on a private lake & a winery",
        cost=9053880,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_19.jpg"
    ),
    'house_17': Property(
        location="Loire Valley, France",
        pay=113452.35,
        description="An old royal palace positioned in the middle of town.",
        cost=10313850,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_3.jpg"
    ),
    'house_18': Property(
        location="Rhine Valley, Germany",
        pay=150076.97,
        description="An old royal palace positioned in the middle of a large field. ",
        cost=13643270,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_14.jpg"
    ),
    'house_19': Property(
        location="Bali, Indonesia",
        pay=175962.05,
        description="A large hotel with 5 pools, a parking garage, and 3 restaurants..",
        cost=15996550,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_16.jpg"
    ),
    'house_20': Property(
        location="Jodhpur, India",
        pay=417962.05,
        description="The largest, most magnificent, most dramatic, most otherworldly palace in the land.",
        cost=37996550,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_20.jpg"
    ),
    'house_22': Property(
        location="Boston, United States",
        pay=12059968.58,
        description="An entire airport. What else do you want?",
        cost=1096360780,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_22.jpg"
    ),
    'house_21': Property(
        location="New York, United States",
        pay=20796495.06,
        description="The empire state building. Can it get any bigger?.",
        cost=1890590460,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_21.jpg"
    ),
    
}
