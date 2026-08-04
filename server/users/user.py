from dataclasses import dataclass

from models.base.entity import Entity


@dataclass
class User(Entity()):
    user_name: str
    password: str
    email: str
    email_verified: bool = False
