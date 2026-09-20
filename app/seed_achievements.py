from app.database import SessionLocal
from app.models import Achievement


ACHIEVEMENTS = [
    {
        "code": "first_lesson",
        "name": "First Step",
        "description": "Complete your first lesson",
        "icon": "🌱",
    },
    {
        "code": "five_lessons",
        "name": "Getting Started",
        "description": "Complete 5 lessons",
        "icon": "📚",
    },
    {
        "code": "three_day_streak",
        "name": "3-Day Streak",
        "description": "Study for 3 consecutive days",
        "icon": "🔥",
    },
    {
        "code": "seven_day_streak",
        "name": "Week Warrior",
        "description": "Study for 7 consecutive days",
        "icon": "🔥",
    },
    {
        "code": "five_hundred_xp",
        "name": "XP Hunter",
        "description": "Earn 500 XP",
        "icon": "⭐",
    },
    {
        "code": "one_thousand_xp",
        "name": "XP Master",
        "description": "Earn 1,000 XP",
        "icon": "🏆",
    },
]


def seed_achievements():
    db = SessionLocal()

    try:
        for achievement_data in ACHIEVEMENTS:

            existing = (
                db.query(Achievement)
                .filter(
                    Achievement.code
                    == achievement_data["code"]
                )
                .first()
            )

            if existing:
                print(
                    f"Already exists: "
                    f"{achievement_data['name']}"
                )
                continue

            achievement = Achievement(
                **achievement_data
            )

            db.add(achievement)

            print(
                f"Added: "
                f"{achievement_data['name']}"
            )

        db.commit()

        print("Achievement seeding complete!")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_achievements()