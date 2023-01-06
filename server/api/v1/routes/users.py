

import logging

from api.decorators.authenticated import authenticated
from api.decorators.check_permissions import check_permission
from api.exceptions import NotFoundException
from api.router import Router
from api.v1 import base_route
from fastapi import Depends
from models.base.id import Id
from models.user.user import User
from service.inject import Injector
from service.session_service import SessionService
from service.user_service import CreateUserRequest, UserService

logger = logging.getLogger()

router = Router(
    prefix=base_route + "/users"
)

@router.post("")
def create_user(
    user_request: CreateUserRequest,
    user_service: UserService = Depends(Injector.inject(UserService))
) -> Id:
    user = user_service.create_user(user_request)
    return user._id

@router.get("")
def get_all_users(
    user_service: UserService = Depends(Injector.inject(UserService))
) -> list[User]:
    all_users = user_service.get_all_users()

    #Filter out all users the calling user doesn't have permission to see
    filtered = all_users

    return filtered

@router.get("/{user_id}")
@authenticated()
@check_permission("read/users/{user_id}")
def get_user(
    user_id: Id,
    user_service: UserService = Depends(Injector.inject(UserService))
) -> User:
    user = user_service.get_user(user_id)
    if not user:
        raise NotFoundException(f"User with id:{user_id} does not exist")

    return user

@router.delete("/{user_id}")
@authenticated()
@check_permission("delete/users/{user_id}")
def delete_user(
    user_id: str,
    user_service: UserService = Depends(Injector.inject(UserService)),
    session_service: SessionService = Depends(Injector.inject(SessionService))
) -> User:
    user = user_service.get_user(user_id)
    if not user:
        raise NotFoundException(f"User with id:{user_id} does not exist")

    # Find any sessions associated with the user and delete them
    session_service.end_sessions_for_user(user_id)

    user_service.delete_user(user)
