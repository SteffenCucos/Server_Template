from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from persistence.models import FOREIGN_KEY, INDEX, NOT_NULLABLE, UNIQUE, field
from models.base.entity import Entity
from models.base.id import Id


@dataclass
class Permission(Entity()):  # type: ignore[misc]
    key: str = field(NOT_NULLABLE | INDEX())
    description: Union[str, None] = None


@dataclass
class Role(Entity("name")):  # type: ignore[misc]
    name: str = field(NOT_NULLABLE | INDEX() | UNIQUE)
    description: Union[str, None] = None


@dataclass
class UserRole(Entity()):  # type: ignore[misc]
    user_id: Id = field(NOT_NULLABLE | FOREIGN_KEY("users.id"))
    role_id: Id = field(NOT_NULLABLE | FOREIGN_KEY("roles.id"))


@dataclass
class RolePermission(Entity()):  # type: ignore[misc]
    role_id: Id = field(NOT_NULLABLE | FOREIGN_KEY("roles.id"))
    permission_id: Id = field(NOT_NULLABLE | FOREIGN_KEY("permissions.id"))
