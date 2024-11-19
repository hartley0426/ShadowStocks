class EducationType:
    OTHER = "other"
    MEDICAL = "Medical"
    BUSINESSADMINSTRATION = "Business Administration"
    EDUCATION = "Education"
    OPERATIONS = "Operations"
    COMPUTERSCIENCE = "Computer Science"

class Education:
    name: str
    description: str
    requirements: dict[str, float]
    type: str = EducationType.OTHER
    cost: int

    def __init__(self, name: str, description: str, requirements: dict[str, float], type: str, cost: int) -> None:
        self.name = name
        self.description = description
        self.requirements = requirements
        self.type = type
        self.cost = cost

    def get_name(self) -> str:
        return self.name
    
    def get_description(self) -> str:
        return self.description
    
    def get_requirements(self) -> dict[str, float]:
        return self.requirements

    def get_type(self) -> str:
        return self.type

    def get_cost(self) -> int:
        return self.cost
    
    @staticmethod
    def from_dict(data: dict) -> "Education":
        return Education(name=data["name"], description=data["description"], requirements=data["requirement"], type=data["type"], cost=data["cost"])

    def to_dict(self) -> dict:
        return {"name": self.name, "description": self.description, "requirements": self.requirements, "type": self.type, "cost": self.cost}

Degrees = {
    "a_computer_science": Education(
        name="Associates Degree of Computer Science",
        description="A entry level degree for all computer science nerds.",
        type=EducationType.COMPUTERSCIENCE,
        cost=10000.0,
        requirements={
            "strength": 5.0,
            "dexterity": 20.0,
            "intelligence": 40.0,
            "charisma": 5.0,
            "wisdom": 25.0,
        }
    ),
    "b_computer_science": Education(
        name="Bachelors Degree of Computer Science",
        description="A higher level degree for all computer science nerds.",
        type=EducationType.COMPUTERSCIENCE,
        cost=15000.0,
        requirements={
            "strength": 5.0,
            "dexterity": 25.0,
            "intelligence": 50.0,
            "charisma": 5.0,
            "wisdom": 35.0,
        }
    ),
    "m_computer_science": Education(
        name="Masters Degree of Computer Science",
        description="A High level degree for all computer science nerds.",
        type=EducationType.COMPUTERSCIENCE,
        cost=20000.0,
        requirements={
            "strength": 5.0,
            "dexterity": 30.0,
            "intelligence": 60.0,
            "charisma": 5.0,
            "wisdom": 45.0,
        }
    ),
    "a_medicine": Education(
        name="Associates Degree of Medicine",
        description="A entry level degree for all doctors & nurses.",
        type=EducationType.MEDICAL,
        cost=100000.0,
        requirements={
            "strength": 10.0,
            "dexterity": 30.0,
            "intelligence": 60.0,
            "charisma": 5.0,
            "wisdom": 20.0,
        }
    ),
    "b_medicine": Education(
        name="Bachelors Degree of Medicine",
        description="A higher level degree for all doctors & nurses.",
        type=EducationType.MEDICAL,
        cost=150000.0,
        requirements={
            "strength": 10.0,
            "dexterity": 35.0,
            "intelligence": 65.0,
            "charisma": 5.0,
            "wisdom": 35.0,
        }
    ),
    "m_medicine": Education(
        name="Masters Degree of Medicine",
        description="A High level degree for all doctors & nurses.",
        type=EducationType.MEDICAL,
        cost=200000.0,
        requirements={
            "strength": 10.0,
            "dexterity": 30.0,
            "intelligence": 70.0,
            "charisma": 5.0,
            "wisdom": 45.0,
        }
    ),
    "a_businessmanagement": Education(
        name="Associates Degree of Business Management",
        description="A entry level degree for any person to be able to run their own business.",
        type=EducationType.BUSINESSADMINSTRATION,
        cost=10000.0,
        requirements={
            "strength": 0.0,
            "dexterity": 0.0,
            "intelligence": 45.0,
            "charisma": 15.0,
            "wisdom": 20.0,
        }
    ),
    "b_businessmanagement": Education(
        name="Bachelors Degree of Business Management",
        description="A higher level degree for any person to be able to run their own business.",
        type=EducationType.BUSINESSADMINSTRATION,
        cost=15000.0,
        requirements={
            "strength": 0.0,
            "dexterity": 0.0,
            "intelligence": 55.0,
            "charisma": 15.0,
            "wisdom": 30.0,
        }
    ),
    "m_businessmanagement": Education(
        name="Masters Degree of Business Management",
        description="A High level degree for any person to be able to run their own business.",
        type=EducationType.MEDICAL,
        cost=20000.0,
        requirements={
            "strength": 0.0,
            "dexterity": 0.0,
            "intelligence": 60.0,
            "charisma": 15.0,
            "wisdom": 45.0,
        }
    ),
    "a_education": Education(
        name="Associates Degree of Education",
        description="A entry level degree for any teacher.",
        type=EducationType.EDUCATION,
        cost=15000.0,
        requirements={
            "strength": 5.0,
            "dexterity": 15.0,
            "intelligence": 45.0,
            "charisma": 25.0,
            "wisdom": 20.0,
        }
    ),
    "b_education": Education(
        name="Bachelors Degree of Education",
        description="A higher level degree for any teacher.",
        type=EducationType.EDUCATION,
        cost=20000.0,
        requirements={
            "strength": 5.0,
            "dexterity": 20.0,
            "intelligence": 55.0,
            "charisma": 30.0,
            "wisdom": 30.0,
        }
    ),
    "m_education": Education(
        name="Masters Degree of Education",
        description="A High level degree for any teacher.",
        type=EducationType.EDUCATION,
        cost=30000.0,
        requirements={
            "strength": 10.0,
            "dexterity": 30.0,
            "intelligence": 60.0,
            "charisma": 30.0,
            "wisdom": 45.0,
        }
    ),
}
    