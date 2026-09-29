from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_current_user
from app.database import get_db
from app.models import (
    User,
    UserProgress,
    AuthAccount,
    LessonCompletion,
    StudySession,
    UserAchievement,
    DailyChallenge,
    DailyChallengeQuestion,
    DailyChallengeCompletion,
    UserLearnedWord,
    UserFavoriteWord,
)
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse,GoogleLogin, AppleLogin,ProfileUpdate
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_google_token,
    verify_apple_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        level=user_data.level,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    progress = UserProgress(
        user_id=user.id,
        xp=0,
        streak=0,
    )

    db.add(progress)
    db.commit()

    return user



@router.post("/login", response_model=TokenResponse)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not user.password_hash:
        raise HTTPException(
            status_code=401,
            detail="This account does not use password login",
        )

    if not verify_password(
        user_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/google", response_model=TokenResponse)
def google_login(
    google_data: GoogleLogin,
    db: Session = Depends(get_db),
):
    idinfo = verify_google_token(google_data.id_token)

    google_user_id = idinfo["sub"]
    email = idinfo.get("email")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Google account does not have an email",
        )

    if not idinfo.get("email_verified"):
        raise HTTPException(
            status_code=400,
            detail="Google email is not verified",
        )

    auth_account = (
        db.query(AuthAccount)
        .filter(
            AuthAccount.provider == "google",
            AuthAccount.provider_user_id == google_user_id,
        )
        .first()
    )

    if auth_account:
        user = auth_account.user

    else:
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            user = User(
    email=email,
    name=idinfo.get("name"),
    password_hash=None,
    level="A0",
)

            db.add(user)
            db.commit()
            db.refresh(user)

            progress = UserProgress(
                user_id=user.id,
                xp=0,
                streak=0,
            )

            db.add(progress)
            db.commit()

        auth_account = AuthAccount(
            user_id=user.id,
            provider="google",
            provider_user_id=google_user_id,
        )

        db.add(auth_account)
        db.commit()

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/apple", response_model=TokenResponse)
def apple_login(
    apple_data: AppleLogin,
    db: Session = Depends(get_db),
):
    claims = verify_apple_token(
        apple_data.identity_token,
        apple_data.nonce,
    )

    apple_user_id = claims.get("sub")

    if not apple_user_id:
        raise HTTPException(
            status_code=401,
            detail="Apple user ID not found",
        )

    email = claims.get("email")

   
    if not email:
        email = apple_data.email

    auth_account = (
        db.query(AuthAccount)
        .filter(
            AuthAccount.provider == "apple",
            AuthAccount.provider_user_id == apple_user_id,
        )
        .first()
    )

   
    if auth_account:
        user = auth_account.user

   
    else:

        user = None

        if email:
            user = (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

     
        if not user:

            if not email:
                raise HTTPException(
                    status_code=400,
                    detail="Apple account did not provide an email",
                )

            user = User(
    email=email,
    name=apple_data.name,
    password_hash=None,
    level="A0",
)

            db.add(user)
            db.commit()
            db.refresh(user)

            progress = UserProgress(
                user_id=user.id,
                xp=0,
                streak=0,
            )

            db.add(progress)
            db.commit()

      
        auth_account = AuthAccount(
            user_id=user.id,
            provider="apple",
            provider_user_id=apple_user_id,
        )

        db.add(auth_account)
        db.commit()

   
    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.put("/profile", response_model=UserResponse)
def update_profile(
    profile_data: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if profile_data.name is not None:
        current_user.name = profile_data.name.strip()

    if profile_data.level is not None:
        current_user.level = profile_data.level

    db.commit()
    db.refresh(current_user)

    return current_user


@router.delete("/account")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id

    db.query(UserLearnedWord).filter(
        UserLearnedWord.user_id == user_id
    ).delete(synchronize_session=False)

    db.query(UserFavoriteWord).filter(
        UserFavoriteWord.user_id == user_id
    ).delete(synchronize_session=False)

    db.query(DailyChallengeCompletion).filter(
        DailyChallengeCompletion.user_id == user_id
    ).delete(synchronize_session=False)

    challenges = (
        db.query(DailyChallenge)
        .filter(DailyChallenge.user_id == user_id)
        .all()
    )

    for challenge in challenges:
        db.delete(challenge)

    db.delete(current_user)

    db.commit()

    return {
        "message": "Account permanently deleted"
    }