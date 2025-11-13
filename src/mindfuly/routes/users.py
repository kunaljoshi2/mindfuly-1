from fastapi import (
    APIRouter,
    Depends,
    Response
    )
from user_service_v2.models.user import (
    UserRepositoryV2,
    UserSchema,
    get_user_repository_v2
)
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/test")
def test():
    return {"status": "ok"}

@router.post("/create_user", status_code=201)
async def create_user(user: UserSchema, response: Response, user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)):
    try:
        tier = getattr(user, "tier", 1)
        new_user = await user_repo.create(user.name, user.email, user.hashed_password, tier=tier)
        if not new_user:
            response.status_code = 409
            return {"detail": "User already exists"}
        return {"user": UserSchema.from_db_model(new_user)}
    except (IntegrityError, AttributeError):
        response.status_code = 409
        return {"detail": "Something went wrong"}
