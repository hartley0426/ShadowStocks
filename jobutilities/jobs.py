import random
from utilities import utils
import datetime

last_updated = {}
listings = {}

class Job:
    def __init__(self, name: str, pay: float, description: str, requirements: dict[str, float], education: dict[str]) -> None:
        self.name = name
        self.pay = pay
        self.description = description
        self.requirements = requirements
        self.education = education

    def GetName(self) -> str:
        return self.name

    def GetPay(self) -> float:
        return self.pay

    def GetDesc(self) -> str:
        return self.description

    def GetRequirements(self) -> dict[str, float]:
        return self.requirements

    def GetEducation(self) -> dict[str]:
        return self.education


class Listing:


    def GenerateListings(self, guild_id):
        try:
            if guild_id not in listings:
                listings[guild_id] = []
            available_jobs = [job_key for job_key in Jobs.keys() if job_key != "unemployed"]
            listings[guild_id] = random.choice(available_jobs)
        except Exception as e:
            print(f"Error during listing generation: {e}")

    def CheckUpdate(self, guild_id):
        try:
            last_update_time = last_updated.get(guild_id, None)

            if last_update_time is None:
                self.GenerateListings(guild_id)
                last_updated[guild_id] = datetime.datetime.now()
                return True
            else:
                time_since_update = utils.get_time_delta(initial_time=last_update_time)
                if time_since_update.get("Hours", 0) > 5:
                    self.GenerateListings(guild_id)
                    last_updated[guild_id] = datetime.datetime.now()
                    return True
                else:
                    return False
        except Exception as e:
            print(f"Error during listing check for guild {guild_id}: {e}")

    def GetListing(self, guild_id):
        return listings.get(guild_id, None)

    def ForceListing(self, guild_id, job_key):
        if job_key in Jobs:
            listings[guild_id] = job_key
            last_updated[guild_id] = datetime.datetime.now()
            print(f"Forced listing for guild {guild_id} to {job_key}")
            return True
        print(f"Invalid job key: {job_key}")
        return False


        

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
        },
        education={}
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
        },
        education={}
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
        },
        education={}
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
        },
        education={}
    ),
    "gcsupervisor": Job(
        name="Grocery Store Supervsior",
        pay=23.0,
        description=("Works at a Grocery Store | Watches over on duty personel and handles supervisory duties."),
        requirements={
            "strength": 0.0,
            "dexterity": 0.0,
            "intelligence": 10.0,
            "charisma": 5.0,
            "wisdom": 10.0,
        },
        education={}
    ),
    "gcmanager": Job(
        name="Grocery Store Manager",
        pay=39.0,
        description=("Works at a Grocery Store | Watches over an entire store."),
        requirements={
            "strength": 5.0,
            "dexterity": 5.0,
            "intelligence": 20.0,
            "charisma": 10.0,
            "wisdom": 15.0,
        },
        education={"a_businessmanagement"}
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
        },
        education={"a_medicine"}
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
        },
        education={"b_medicine"}
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
        },
        education={"m_medicine"}
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
        },
        education={"b_medicine", "b_businessmanagement"}
    ),
    "deanofthehospital": Job(
        name="Dean of the Hospital",
        pay=400.0,
        description=("Works at a Hospital | Watches over an entire hospital."),
        requirements={
            "strength": 15.0,
            "dexterity": 47.0,
            "intelligence": 75.0,
            "charisma": 40.0,
            "wisdom": 50.0,
        },
        education={"m_medicine", "m_businessmanagement"}
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
        },
        education={}
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
        },
        education={}
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
        },
        education={"a_education"}
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
        },
        education={"b_education", "a_businessmanagement"}
    ),
    "superintendent": Job(
        name="Superindentent",
        pay=57.0,
        description=("Works at a school | Watches over an entire school district."),
        requirements={
            "strength": 5.0,
            "dexterity": 25.0,
            "intelligence": 20.0,
            "charisma": 20.0,
            "wisdom": 20.0,
        },
        education={"b_education", "b_businessmanagement"}
    ),
    "professor": Job(
        name="Professor",
        pay=68.0,
        description=("Works at a college | Teaches a college class."),
        requirements={
            "strength": 5.0,
            "dexterity": 20.0,
            "intelligence": 25.0,
            "charisma": 22.0,
            "wisdom": 25.0,
        },
        education={"m_education"}
    ),
    "deanofthecollege": Job(
        name="Dean of the College",
        pay=279.0,
        description=("Works at a college | Watches over an entire college."),
        requirements={
            "strength": 5.0,
            "dexterity": 25.0,
            "intelligence": 30.0,
            "charisma": 25.0,
            "wisdom": 30.0,
        },
        education={"m_education", "m_businessmanagement"}
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
        },
        education={}
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
        },
        education={}
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
        },
        education={}
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
        },
        education={"m_computer_science"}
    ),

}