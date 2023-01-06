
import re as regex
from dataclasses import dataclass, field

from models.base.entity import Entity


@dataclass
class User(Entity()):
    user_name: str
    password: str
    email: str
    email_verified: bool = False
    permissions: list[str] = field(default_factory=lambda: [])

    def has_permission(self, permission: str) -> bool:
        for user_permission in self.permissions:
            if regex.match(user_permission, permission):
                return True
        return False
