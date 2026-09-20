from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, UserFavoriteWord
from app.schemas import FavoriteWordCreate, FavoriteWordResponse


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
)



@router.post(
    "",
    response_model=FavoriteWordResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_favorite(
    favorite: FavoriteWordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_favorite = (
        db.query(UserFavoriteWord)
        .filter(
            UserFavoriteWord.user_id == current_user.id,
            UserFavoriteWord.word == favorite.word,
        )
        .first()
    )

    if existing_favorite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Word is already in favorites",
        )

    new_favorite = UserFavoriteWord(
        user_id=current_user.id,
        word=favorite.word,
        translation=favorite.translation,
        example_1=favorite.example_1,
        example_2=favorite.example_2,
        example_translation_1=favorite.example_translation_1,
        example_translation_2=favorite.example_translation_2,
        level=favorite.level,
    )

    db.add(new_favorite)
    db.commit()
    db.refresh(new_favorite)

    return new_favorite



@router.get(
    "",
    response_model=list[FavoriteWordResponse],
)
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    favorites = (
        db.query(UserFavoriteWord)
        .filter(
            UserFavoriteWord.user_id == current_user.id
        )
        .order_by(
            UserFavoriteWord.favorited_at.desc()
        )
        .all()
    )

    return favorites


@router.delete(
    "/{favorite_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_favorite(
    favorite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    favorite = (
        db.query(UserFavoriteWord)
        .filter(
            UserFavoriteWord.id == favorite_id,
            UserFavoriteWord.user_id == current_user.id,
        )
        .first()
    )

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite word not found",
        )

    db.delete(favorite)
    db.commit()

    return None