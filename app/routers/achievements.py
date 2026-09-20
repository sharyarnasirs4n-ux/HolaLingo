from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    User,
    Achievement,
    UserAchievement,
    LessonCompletion,
)


router = APIRouter(
    prefix="/achievements",
    tags=["Achievements"],
)


@router.get("/")
def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    achievements = (
        db.query(Achievement)
        .order_by(Achievement.id.asc())
        .all()
    )

    user_achievements = (
        db.query(UserAchievement)
        .filter(
            UserAchievement.user_id == current_user.id
        )
        .all()
    )

    unlocked_map = {
        item.achievement_id: item
        for item in user_achievements
    }

    lesson_count = (
        db.query(LessonCompletion)
        .filter(
            LessonCompletion.user_id == current_user.id
        )
        .count()
    )

    xp = (
        current_user.progress.xp
        if current_user.progress
        else 0
    )

    streak = (
        current_user.progress.streak
        if current_user.progress
        else 0
    )

    result = []

    for achievement in achievements:

        unlocked = (
            achievement.id in unlocked_map
        )

        current = 0
        target = 1

        if achievement.code == "first_lesson":

            current = min(
                lesson_count,
                1
            )

            target = 1

        elif achievement.code == "five_lessons":

            current = min(
                lesson_count,
                5
            )

            target = 5

        elif achievement.code == "three_day_streak":

            current = min(
                streak,
                3
            )

            target = 3

        elif achievement.code == "seven_day_streak":

            current = min(
                streak,
                7
            )

            target = 7

        elif achievement.code == "five_hundred_xp":

            current = min(
                xp,
                500
            )

            target = 500

        elif achievement.code == "one_thousand_xp":

            current = min(
                xp,
                1000
            )

            target = 1000

        result.append({

            "code": achievement.code,

            "name": achievement.name,

            "description": achievement.description,

            "icon": achievement.icon,

            "unlocked": unlocked,

            "unlocked_at": (
                unlocked_map[
                    achievement.id
                ].unlocked_at.isoformat()
                if unlocked
                else None
            ),

            "progress": {
                "current": current,
                "target": target,
            },

        })

    return {
        "achievements": result
    }