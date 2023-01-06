

import logging
from dataclasses import dataclass

from api.decorators.authenticated import authenticated
from api.exceptions import UnauthorizedException
from api.router import Router
from api.v1 import base_route
from auth.session.session import Session
from fastapi import Depends
from fastapi.responses import HTMLResponse
from models.request_context import RequestContext
from service.inject import Injector
from service.session_service import SessionService
from service.user_service import UserService

logger = logging.getLogger(__name__)

router = Router(
    prefix=base_route + "/sessions"
)

@router.get("")
def get_sessions(
    user_service: UserService = Depends(Injector.inject(UserService)),
    session_service: SessionService = Depends(Injector.inject(SessionService))
):
    sessions = session_service.get_all()
    def session_li(session: Session) -> str:
        user = user_service.get_user(session.user_id)
        user_name = user.user_name if user else "User DNE"
        return "<li>" + session._id + ": " + user_name + "</li>"

    session_li = "\n".join([session_li(session) for session in sessions])

    html_content = """
    <html>
        <body>
            <h1>Sessions</h1>
            <ul>
    """ + session_li + """
            </ul>
        </body>
    </html>
    """
    
    return HTMLResponse(content=html_content, status_code=200)

@dataclass
class LoginBody:
    user_name: str
    password: str


@router.post("/login")
def login(
    credentials: LoginBody,
    user_service: UserService = Depends(Injector.inject(UserService)),
    session_service: SessionService = Depends(Injector.inject(SessionService))
):
    user = user_service.get_user_by_name(credentials.user_name)

    if not user or user.password != credentials.password:
        raise UnauthorizedException("Incorrect user name or password")

    session = session_service.create_session(user)

    # response = RedirectResponse(url='/')
    # response.set_cookie('Authorization', value=session['session_id'], httponly=True)
    # return response

    return session._id

@router.get("/logout")
@authenticated()
def logout(
    session_service: SessionService = Depends(Injector.inject(SessionService))
):
    session_id = RequestContext.get_context().session_id
    session_service.end_session(session_id)

