class Attribute:
    def __init__(self, level: float = 0.0, minimum: float = 0.0, maximum: float = 100.0) -> None:
        self.level = level
        self.minimum = minimum
        self.maximum = maximum

    def __str__(self) -> str:
        return f"{self.level / self.maximum * 100:.2f}%"

    def IncrLevel(self, amount: float) -> None:
        self.level += amount
        if self.level > self.maximum:
            self.level = self.maximum

    def DecrLevel(self, amount: float) -> None:
        self.level -= amount
        if self.level < self.minimum:
            self.level = self.minimum

    def IsMaxLevel(self) -> bool:
        return self.level >= self.maximum

    def IsMinLevel(self) -> bool:
        return self.level <= self.minimum

    def GetLevel(self) -> float:
        return self.level

    def GetLevelPercentage(self) -> float:
        return (self.level / self.maximum) * 100

    def SetLevel(self, level: float) -> None:
        self.level = level

    @staticmethod
    def from_dict(data: dict) -> "Attribute":
        return Attribute(level=data["level"], minimum=data["minimum"], maximum=data["maximum"])

    def to_dict(self) -> dict:
        return {"level": self.level, "minimum": self.minimum, "maximum": self.maximum}