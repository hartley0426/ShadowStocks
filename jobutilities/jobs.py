import random
import datetime
from utilities import utils


listing = {}
last_updated = datetime.datetime.now()

class Job:

    name: str
    pay: float
    description: str
    requirements: dict[str, float]

    def __init__(self, name: str, pay: float, description: str, requirements: dict[str, float]) -> None:
        self.name = name
        self.pay = pay
        self.description = description
        self.requirements = requirements

    def GetName(self) -> str:
        return self.name
    
    def GetPay(self) -> float:
        return self.pay
    
    def GetDesc(self) -> str:
        return self.description
    
    def GetRequirements(self) -> dict[str, float]:
        return self.requirements

class Listing:

    def GenerateListings(self, guild_id) -> None:
        global listing
        if guild_id not in listing:
            listing[guild_id] = []

        available_jobs = [job_key for job_key in Jobs.keys() if job_key != "unemployed"]
        new_job = random.choice(available_jobs)
        listing[guild_id] = Jobs[new_job]

    def CheckUpdate(self, guild_id) -> bool:
        global last_updated
        time_since_update = utils.get_time_delta(initial_time=last_updated)
        if time_since_update["minutes"] > 5:
            self.GenerateListings(guild_id)
            last_updated = datetime.datetime.now()
            return True
        return False

    def GetListing(self, guild_id) -> list[Job]:
        if self.CheckUpdate(guild_id):
            return listing.get(guild_id, [])
        return listing.get(guild_id, [])
        
    def GetLastUpdated(self) -> datetime.datetime:
        global last_updated
        return last_updated

        

Jobs = {
    "unemployed": Job(
        name="Unemployed",
        pay=0.0,
        description=("No Job | Works Part-Time Gigs."),
        requirements={
            "strength": 0.0,
            "dexterity": 0.0,
            "intelligence": 0.0,
            "charisma": 0.0,
            "wisdom": 0.0,
        }
    ),
    "cashier": Job(
        name="Cashier",
        pay=8.0,
        description=("Works at a Grocery Store | Works at the Register."),
        requirements={
            "strength": 0.0,
            "dexterity": 10.0,
            "intelligence": 10.0,
            "charisma": 5.0,
            "wisdom": 0.0,
        }
    ),
    "bagger": Job(
        name="Bagger",
        pay=6.0,
        description=("Works at a Grocery Store | Bags peoples groceries."),
        requirements={
            "strength": 5.0,
            "dexterity": 10.0,
            "intelligence": 0.0,
            "charisma": 0.0,
            "wisdom": 0.0,
        }
    ),
    "stocker": Job(
        name="Stocker",
        pay=9.0,
        description=("Works at a Grocery Store | Stocks Shelfs."),
        requirements={
            "strength": 10.0,
            "dexterity": 10.0,
            "intelligence": 0.0,
            "charisma": 0.0,
            "wisdom": 0.0,
        }
    ),
    "gcsupervisor": Job(
        name="Grocery Store Supervsior",
        pay=13.0,
        description=("Works at a Grocery Store | Watches over on duty personel and handles supervisory duties."),
        requirements={
            "strength": 0.0,
            "dexterity": 0.0,
            "intelligence": 10.0,
            "charisma": 5.0,
            "wisdom": 10.0,
        }
    ),
    "gcmanager": Job(
        name="Grocery Store Manager",
        pay=15.0,
        description=("Works at a Grocery Store | Watches over an entire store."),
        requirements={
            "strength": 5.0,
            "dexterity": 5.0,
            "intelligence": 20.0,
            "charisma": 10.0,
            "wisdom": 15.0,
        }
    ),
    "nurse": Job(
        name="Nurse",
        pay=36.0,
        description=("Works at a Hospital | Helps everyone."),
        requirements={
            "strength": 10.0,
            "dexterity": 50.0,
            "intelligence": 50.0,
            "charisma": 15.0,
            "wisdom": 10.0,
        }
    ),
    "doctor": Job(
        name="Doctor",
        pay=73.0,
        description=("Works at a Hospital | Treats patients."),
        requirements={
            "strength": 10.0,
            "dexterity": 45.0,
            "intelligence": 55.0,
            "charisma": 20.0,
            "wisdom": 20.0,
        }
    ),
    "surgeon": Job(
        name="Surgeon",
        pay=166.0,
        description=("Works at a Hospital | Operates on patients."),
        requirements={
            "strength": 25.0,
            "dexterity": 55.0,
            "intelligence": 60.0,
            "charisma": 20.0,
            "wisdom": 30.0,
        }
    ),
    "headofmedicine": Job(
        name="Head of Medicine",
        pay=182.0,
        description=("Works at a Hospital | Watches over on duty personel and handles supervisory duties."),
        requirements={
            "strength": 20.0,
            "dexterity": 45.0,
            "intelligence": 68.0,
            "charisma": 25.0,
            "wisdom": 40.0,
        }
    ),
    "deanofthehospital": Job(
        name="Dean of the Hospital",
        pay=200.0,
        description=("Works at a Hospital | Watches over an entire store."),
        requirements={
            "strength": 15.0,
            "dexterity": 47.0,
            "intelligence": 75.0,
            "charisma": 40.0,
            "wisdom": 50.0,
        }
    ),
    "teachersassistant": Job(
        name="Teacher's Assistant",
        pay=5.0,
        description=("Works at a school | Helps Teachers."),
        requirements={
            "strength": 0.0,
            "dexterity": 5.0,
            "intelligence": 0.0,
            "charisma": 0.0,
            "wisdom": 0.0,
        }
    ),
    "schoolaid": Job(
        name="School Aid",
        pay=14.0,
        description=("Works at a school | Watches over children."),
        requirements={
            "strength": 10.0,
            "dexterity": 20.0,
            "intelligence": 0.0,
            "charisma": 0.0,
            "wisdom": 0.0,
        }
    ),
    "teacher": Job(
        name="Teacher",
        pay=25.0,
        description=("Works at a school | Helps students learn and prepare for careers."),
        requirements={
            "strength": 10.0,
            "dexterity": 20.0,
            "intelligence": 10.0,
            "charisma": 10.0,
            "wisdom": 5.0,
        }
    ),
    "principal": Job(
        name="Principal",
        pay=38.0,
        description=("Works at a school | Watches over an entire school."),
        requirements={
            "strength": 10.0,
            "dexterity": 20.0,
            "intelligence": 15.0,
            "charisma": 20.0,
            "wisdom": 15.0,
        }
    ),
    "superintendent": Job(
        name="Superindentent",
        pay=47.0,
        description=("Works at a school | Watches over an entire school district."),
        requirements={
            "strength": 5.0,
            "dexterity": 25.0,
            "intelligence": 20.0,
            "charisma": 20.0,
            "wisdom": 20.0,
        }
    ),
    "professor": Job(
        name="Professor",
        pay=45.0,
        description=("Works at a college | Teaches a college class."),
        requirements={
            "strength": 5.0,
            "dexterity": 20.0,
            "intelligence": 25.0,
            "charisma": 22.0,
            "wisdom": 25.0,
        }
    ),
    "deanofthecollege": Job(
        name="Dean of the College",
        pay=45.0,
        description=("Works at a college | Watches over an entire college."),
        requirements={
            "strength": 5.0,
            "dexterity": 25.0,
            "intelligence": 30.0,
            "charisma": 25.0,
            "wisdom": 30.0,
        }
    ),
    "mechanic": Job(
        name="Mechanic",
        pay=30.0,
        description=("Works at a mechanic shop | Works on cars."),
        requirements={
            "strength": 45.0,
            "dexterity": 45.0,
            "intelligence": 10.0,
            "charisma": 25.0,
            "wisdom": 5.0,
        }
    ),
    "flightattendent": Job(
        name="Flight Attendant",
        pay=32.0,
        description=("Works on an airplane | Serves passengers."),
        requirements={
            "strength": 10.0,
            "dexterity": 25.0,
            "intelligence": 10.0,
            "charisma": 40.0,
            "wisdom": 15.0,
        }
    ),
    "pilot": Job(
        name="Pilot",
        pay=50.0,
        description=("Works on an airplane | Flys plane."),
        requirements={
            "strength": 10.0,
            "dexterity": 25.0,
            "intelligence": 20.0,
            "charisma": 20.0,
            "wisdom": 25.0,
        }
    ),
    "itsupport": Job(
        name="IT Support Specialist",
        pay=27.0,
        description=("Works in a IR center | Assists with technical issues and provides support for computer systems and software."),
        requirements={
            "strength": 10.0,
            "dexterity": 35.0,
            "intelligence": 50.0,
            "charisma": 25.0,
            "wisdom": 25.0,
        }
    ),

}