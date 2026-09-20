from sqlalchemy.orm import Session

from app.models import (
    Achievement,
    User,
    UserAchievement,
    LessonCompletion,
)


def unlock_achievement(
    db: Session,
    user: User,
    code: str,
):
    """
    Unlock an achievement for a user
    if they have not already unlocked it.
    """

    achievement = (
        db.query(Achievement)
        .filter(
            Achievement.code == code
        )
        .first()
    )

    if not achievement:
        return None

    existing = (
        db.query(UserAchievement)
        .filter(
            UserAchievement.user_id == user.id,
            UserAchievement.achievement_id
            == achievement.id,
        )
        .first()
    )

    if existing:
        return None

    user_achievement = UserAchievement(
        user_id=user.id,
        achievement_id=achievement.id,
    )

    db.add(user_achievement)

    return achievement


def check_achievements(
    db: Session,
    user: User,
):
    """
    Check all achievement rules for the user.
    Unlock any achievements that have been earned.
    """

    unlocked = []

    
    lesson_count = (
        db.query(LessonCompletion)
        .filter(
            LessonCompletion.user_id == user.id
        )
        .count()
    )

    if lesson_count >= 1:

        achievement = unlock_achievement(
            db,
            user,
            "first_lesson",
        )

        if achievement:
            unlocked.append(achievement)

    if lesson_count >= 5:

        achievement = unlock_achievement(
            db,
            user,
            "five_lessons",
        )

        if achievement:
            unlocked.append(achievement)

    
    streak = (
        user.progress.streak
        if user.progress
        else 0
    )

    if streak >= 3:

        achievement = unlock_achievement(
            db,
            user,
            "three_day_streak",
        )

        if achievement:
            unlocked.append(achievement)

    if streak >= 7:

        achievement = unlock_achievement(
            db,
            user,
            "seven_day_streak",
        )

        if achievement:
            unlocked.append(achievement)

    # ========================================================
    # XP ACHIEVEMENTS
    # ========================================================

    xp = (
        user.progress.xp
        if user.progress
        else 0
    )

    if xp >= 500:

        achievement = unlock_achievement(
            db,
            user,
            "five_hundred_xp",
        )

        if achievement:
            unlocked.append(achievement)

    if xp >= 1000:

        achievement = unlock_achievement(
            db,
            user,
            "one_thousand_xp",
        )

        if achievement:
            unlocked.append(achievement)

    return unlocked