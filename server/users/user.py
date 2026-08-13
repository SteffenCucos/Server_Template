from dataclasses import dataclass

from models.base.entity import Entity


@dataclass
class User(Entity()):  # type: ignore[misc]
    user_name: str
    password_hash: str
    email: str
    email_verified: bool = False
