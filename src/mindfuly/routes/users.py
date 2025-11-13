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
    
@router.get("/{username}")
async def get_user(username: str, user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)):
    user = await user_repo.get_by_name(username)
    if not user:
        return {"detail": "User not found"}
    return UserSchema.from_db_model(user)

@router.get("/")
async def list_users(user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)):
    user_models = await user_repo.get_all()
    users = [UserSchema.from_db_model(m) for m in user_models]
    return {'users': users}

@router.delete("/{username}")
async def delete_user(username: str, user_repo: UserRepositoryV2 = Depends(get_user_repository_v2)):
    user = await user_repo.get_by_name(username)
    result = await user_repo.delete(user.id)
    if result:
        return {"detail": "User not found"}
    return {"detail": "User deleted successfully"}