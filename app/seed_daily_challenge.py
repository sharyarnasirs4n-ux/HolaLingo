from datetime import date

from app.database import SessionLocal
from app.models import (
    DailyChallenge,
    DailyChallengeQuestion,
)


def seed_daily_challenge():

    db = SessionLocal()

    try:

        challenge_date = date.today()

        existing = (
            db.query(DailyChallenge)
            .filter(
                DailyChallenge.challenge_date
                == challenge_date
            )
            .first()
        )

        if existing:

            print(
                f"Daily challenge already exists "
                f"for {challenge_date}"
            )

            return

        challenge = DailyChallenge(
            challenge_date=challenge_date,
            title="Daily Spanish Challenge",
            description="Test your Spanish skills today",
            xp_reward=25,
        )

        db.add(challenge)

        db.flush()

        questions = [

            DailyChallengeQuestion(
                challenge_id=challenge.id,
                question='What does "Hola" mean?',
                options=[
                    "Hello",
                    "Goodbye",
                    "Thank you",
                    "Please",
                ],
                correct_answer="Hello",
            ),

            DailyChallengeQuestion(
                challenge_id=challenge.id,
                question='What does "Gracias" mean?',
                options=[
                    "Please",
                    "Thank you",
                    "Sorry",
                    "Good morning",
                ],
                correct_answer="Thank you",
            ),

            DailyChallengeQuestion(
                challenge_id=challenge.id,
                question='What does "Adiós" mean?',
                options=[
                    "Hello",
                    "Goodbye",
                    "Welcome",
                    "Excuse me",
                ],
                correct_answer="Goodbye",
            ),

            DailyChallengeQuestion(
                challenge_id=challenge.id,
                question='What does "Por favor" mean?',
                options=[
                    "Thank you",
                    "Goodbye",
                    "Please",
                    "Sorry",
                ],
                correct_answer="Please",
            ),

            DailyChallengeQuestion(
                challenge_id=challenge.id,
                question='What does "Buenos días" mean?',
                options=[
                    "Good night",
                    "Good morning",
                    "Goodbye",
                    "See you later",
                ],
                correct_answer="Good morning",
            ),

        ]

        db.add_all(questions)

        db.commit()

        print(
            f"Daily challenge created for "
            f"{challenge_date}"
        )

        print(
            f"Challenge ID: {challenge.id}"
        )

        print(
            f"Questions added: {len(questions)}"
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


if __name__ == "__main__":
    seed_daily_challenge()