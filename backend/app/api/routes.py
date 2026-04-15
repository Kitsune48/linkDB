from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.http import success_response
from app.core.rate_limit import login_rate_limiter
from app.db.session import get_db_session
from app.dependencies.auth import require_auth
from app.schemas.auth import AuthUserResponse, LoginBody
from app.services.categories import categories_service
from app.schemas.links import CreateLinkBody, ListLinksQuery, UpdateLinkBody
from app.security.session import create_session_token, session_cookie_options
from app.services.auth import auth_service
from app.services.links import links_service
from app.services.read_later import read_later_service


router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> Response:
    return success_response({"service": "linkdb-backend", "status": "ok"})


@router.post("/auth/login")
def login(
    input_data: LoginBody,
    _: Annotated[None, Depends(login_rate_limiter)],
    db: Annotated[Session, Depends(get_db_session)],
) -> Response:
    user = auth_service.login(db, input_data)
    token = create_session_token(user.id, user.username)
    response = success_response(
        AuthUserResponse(user=user).model_dump(mode="json", by_alias=True)
    )
    response.set_cookie(
        key=get_settings().auth_cookie_name,
        value=token,
        **session_cookie_options(),
    )
    return response


@router.post("/auth/logout")
def logout() -> Response:
    response = success_response({"message": "Logged out successfully."})
    response.delete_cookie(
        get_settings().auth_cookie_name,
        path="/",
        httponly=True,
        samesite="lax",
        secure=get_settings().is_production,
    )
    return response


@router.get("/auth/me")
def me(
    session_user: Annotated[object, Depends(require_auth)],
    db: Annotated[Session, Depends(get_db_session)],
) -> Response:
    user = auth_service.get_current_user(db, session_user)
    return success_response(
        AuthUserResponse(user=user).model_dump(mode="json", by_alias=True)
    )


@router.get("/categories")
def list_categories(
    db: Annotated[Session, Depends(get_db_session)],
    _: Annotated[object, Depends(require_auth)],
) -> Response:
    categories = categories_service.list_categories(db)
    return success_response([category.model_dump(mode="json", by_alias=True) for category in categories])


@router.get("/links")
def list_links(
    db: Annotated[Session, Depends(get_db_session)],
    session_user: Annotated[object, Depends(require_auth)],
    q: str | None = None,
    category: str | None = None,
    categories: list[str] | None = Query(default=None),
    status: str | None = None,
    addedBy: int | None = None,
    page: int = 1,
    limit: int = 20,
    sort: str = "updatedAt",
    order: str = "desc",
) -> Response:
    query = ListLinksQuery(
        q=q,
        category=category,
        categories=categories,
        status=status,
        addedBy=addedBy,
        page=page,
        limit=limit,
        sort=sort,
        order=order,
    )
    result = links_service.list_links(db, query, current_user_id=session_user.id)
    return success_response(result.model_dump(mode="json", by_alias=True))


@router.get("/links/{link_id}")
def get_link_by_id(
    link_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db_session)],
    session_user: Annotated[object, Depends(require_auth)],
) -> Response:
    result = links_service.get_link_by_id(db, link_id, current_user_id=session_user.id)
    return success_response(result.model_dump(mode="json", by_alias=True))


@router.post("/links")
def create_link(
    input_data: CreateLinkBody,
    db: Annotated[Session, Depends(get_db_session)],
    session_user: Annotated[object, Depends(require_auth)],
) -> Response:
    result = links_service.create_link(db, input_data, session_user.id)
    return success_response(result.model_dump(mode="json", by_alias=True), status_code=201)


@router.patch("/links/{link_id}")
def update_link(
    link_id: Annotated[int, Path(gt=0)],
    input_data: UpdateLinkBody,
    db: Annotated[Session, Depends(get_db_session)],
    session_user: Annotated[object, Depends(require_auth)],
) -> Response:
    result = links_service.update_link(db, link_id, input_data, session_user.id)
    return success_response(result.model_dump(mode="json", by_alias=True))


@router.delete("/links/{link_id}")
def delete_link(
    link_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db_session)],
    session_user: Annotated[object, Depends(require_auth)],
) -> Response:
    links_service.delete_link(db, link_id, session_user.id)
    return success_response({"message": "Link deleted successfully."})


@router.get("/read-later")
def list_read_later(
    db: Annotated[Session, Depends(get_db_session)],
    session_user: Annotated[object, Depends(require_auth)],
) -> Response:
    result = read_later_service.list_read_later_links(db, session_user.id)
    return success_response([item.model_dump(mode="json", by_alias=True) for item in result])


@router.post("/read-later/{link_id}")
def add_to_read_later(
    link_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db_session)],
    session_user: Annotated[object, Depends(require_auth)],
) -> Response:
    result = read_later_service.add_to_read_later(db, session_user.id, link_id)
    return success_response(result.model_dump(mode="json", by_alias=True), status_code=201)


@router.delete("/read-later/{link_id}")
def remove_from_read_later(
    link_id: Annotated[int, Path(gt=0)],
    db: Annotated[Session, Depends(get_db_session)],
    session_user: Annotated[object, Depends(require_auth)],
) -> Response:
    read_later_service.remove_from_read_later(db, session_user.id, link_id)
    return success_response({"message": "Removed from read later."})
