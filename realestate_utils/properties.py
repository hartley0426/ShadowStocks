import random
import datetime
from utilities import utils

class Property:

    cost: float
    location: str
    description: str
    image: str

    def __init__(self, cost: float, location: str, description: str, image: str) -> None:
        self.cost = cost
        self.description = description
        self.location = location
        self.image = image

    def GetLocation(self) -> str:
        return self.location
    
    def GetShortDesc(self) -> str:
        return self.location

    def GetCost(self) -> float:
        return self.cost
    
    def GetDesc(self) -> str:
        return self.description
    
    def GetImage(self) -> str:
        return self.image


        

Properties = {
    'house_1': Property(
        location="Bodie, United States",
        description="A small miners shack in the historic ghost-town of Bodie.",
        cost=47000,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_4.jpg"
    ),
    'house_2': Property(
        location="Karwendelgebirge, Austria",
        description="A small cabin in a private valley in Austria.",
        cost=52000,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_18.jpg"
    ),
    'house_3': Property(
        location="San Jose, United States",
        description="A suburan house in the middle of the city.",
        cost=112000,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_2.jpg"
    ),
    'house_4': Property(
        location="Lake Ullswater, United Kingdom",
        description="A house with an overview of the water. Previously a boathouse.",
        cost=200550,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_11.jpg"
    ),
    'house_5': Property(
        location="Pittson, United States",
        description="A house in the middle of Pittsburg",
        cost=219500,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_12.jpg"
    ),
    'house_6': Property(
        location="Indian Land, United States",
        description="A house on a large piece of land, has a pond.",
        cost=567200,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_5.jpg"
    ),
    'house_7': Property(
        location="Boligsalgsrapport, Norway",
        description="Peaceful house with a great view.",
        cost=683450,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_1.jpg"
    ),
    'house_8': Property(
        location="Coconut Creek, United States",
        description="A large house with quick access to the beach.",
        cost=784260,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_6.jpg"
    ),
    'house_9': Property(
        location="Flower Mound, United States",
        description="A large house with a large pool, and access to a large lake.",
        cost=1392260,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_8.jpg"
    ),
    'house_10': Property(
        location="Beaumont, United States",
        description="A large manor on a large plot of land.",
        cost=1790950,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_13.jpg"
    ),
    'house_11': Property(
        location="Ringgold, United States",
        description="A large mansion in a private complex",
        cost=2795270,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_17.jpg"
    ),
    'house_12': Property(
        location="Ware, United Kingdom",
        description="A large complex of a decomissioned hotel.",
        cost=3955270,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_10.jpg"
    ),
    'house_13': Property(
        location="Dresden, Germany",
        description="A refurnished castle",
        cost=5278380,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_15.jpg"
    ),
    'house_14': Property(
        location="Fulda, Germany",
        description="A refurnished royal mansion that was put out of use.",
        cost=6537340,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_9.jpg"
    ),
    'house_15': Property(
        location="Antholzertal, Italy",
        description="A mansion positioned on a private lake surrounded by mountains.",
        cost=7795910,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_7.jpg"
    ),
    'house_16': Property(
        location="Toulan, France",
        description="A mansion positioned on a private lake & a winery",
        cost=9053880,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_19.jpg"
    ),
    'house_17': Property(
        location="Loire Valley, France",
        description="An old royal palace positioned in the middle of town.",
        cost=10313850,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_3.jpg"
    ),
    'house_18': Property(
        location="Rhine Valley, Germany",
        description="An old royal palace positioned in the middle of a large field. ",
        cost=10313850,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_14.jpg"
    ),
    'house_19': Property(
        location="Bali, Indonesia",
        description="A large hotel with 5 pools, a parking garage, and 3 restaurants..",
        cost=15996550,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_16.jpg"
    ),
    'house_20': Property(
        location="Jodhpur, India",
        description="The largest, most magnificent, most dramatic, most otherworldly palace in the land.",
        cost=37996550,
        image="https://hartley0426.github.io/ShadowStocks/assets/propertyimages/house_20.jpg"
    ),
}
