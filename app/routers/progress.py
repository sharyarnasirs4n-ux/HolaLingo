from datetime import date, timedelta
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    User,
    UserProgress,
    LessonCompletion,
    StudySession,
    UserLearnedWord
)

from app.services.achievements import (
    check_achievements,
)

router = APIRouter(
    prefix="/progress",
    tags=["Progress"],
)



@router.get("")
def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id)
        .first()
    )

    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            xp=0,
            streak=0,
        )

        db.add(progress)
        db.commit()
        db.refresh(progress)

    return {
        "xp": progress.xp,
        "streak": progress.streak,
    }



class LearnedWord(BaseModel):
    word: str
    translation: str
    example: str | None = None
    example_translation: str | None = None
    level: str | None = None



@router.post("/lesson")
def complete_lesson(
    lesson_id: str,
    xp_earned: int,
    learned_words: list[LearnedWord],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    print(
    "LEARNED WORDS RECEIVED:",
    learned_words
)


    print(
    "TOTAL LEARNED WORDS RECEIVED:",
    len(learned_words)
)
    if xp_earned < 0:
        raise HTTPException(
            status_code=400,
            detail="XP cannot be negative",
        )

    
    existing_completion = (
        db.query(LessonCompletion)
        .filter(
            LessonCompletion.user_id == current_user.id,
            LessonCompletion.lesson_id == lesson_id,
        )
        .first()
    )

    if existing_completion:
        return {
            "message": "Lesson already completed",
            "xp": db.query(UserProgress)
            .filter(UserProgress.user_id == current_user.id)
            .first()
            .xp,
        }

    
    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id)
        .first()
    )

    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            xp=0,
            streak=0,
        )

        db.add(progress)
        db.flush()

    
    progress.xp += xp_earned

    
    completion = LessonCompletion(
        user_id=current_user.id,
        lesson_id=lesson_id,
        xp_earned=xp_earned,
    )

    db.add(completion)

   
    for learned_word in learned_words:

        print(
            "PROCESSING LEARNED WORD:",
            learned_word.word
        )

        existing_word = (
            db.query(UserLearnedWord)
            .filter(
                UserLearnedWord.user_id == current_user.id,
                UserLearnedWord.word == learned_word.word,
            )
            .first()
        )

        if existing_word:
            print(
                "WORD ALREADY EXISTS:",
                learned_word.word,
                "ID:",
                existing_word.id,
                "USER:",
                existing_word.user_id,
            )
            continue

        new_word = UserLearnedWord(
            user_id=current_user.id,
            word=learned_word.word,
            translation=learned_word.translation,
            example=learned_word.example,
            example_translation=learned_word.example_translation,
            level=learned_word.level,
        )

        db.add(new_word)

        print(
            "WORD ADDED TO SESSION:",
            learned_word.word
        )

    
    today = date.today()

    latest_session = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == current_user.id,
            StudySession.study_date < today,
        )
        .order_by(StudySession.study_date.desc())
        .first()
    )

    today_session = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == current_user.id,
            StudySession.study_date == today,
        )
        .first()
    )

    if not today_session:

        today_session = StudySession(
            user_id=current_user.id,
            study_date=today,
        )

        db.add(today_session)

        if latest_session:
            yesterday = today - timedelta(days=1)

            if latest_session.study_date == yesterday:
                progress.streak += 1
            else:
                progress.streak = 1

        else:
            progress.streak = 1

  
    unlocked_achievements = check_achievements(
        db,
        current_user,
)


    db.commit()
    db.refresh(progress)

    return {
    "message": "Lesson completed",
    "lesson_id": lesson_id,
    "xp_earned": xp_earned,
    "xp": progress.xp,
    "streak": progress.streak,
    "new_achievements": [
        {
            "code": achievement.code,
            "name": achievement.name,
            "description": achievement.description,
            "icon": achievement.icon,
        }
        for achievement in unlocked_achievements
    ],
}


@router.get("/lessons")
def get_completed_lessons(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    completions = (
        db.query(LessonCompletion)
        .filter(
            LessonCompletion.user_id == current_user.id
        )
        .order_by(
            LessonCompletion.completed_at.asc()
        )
        .all()
    )

    return {
        "completed_lessons": [
            completion.lesson_id
            for completion in completions
        ]
    }


@router.get("/study-dates")
def get_study_dates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == current_user.id
        )
        .order_by(
            StudySession.study_date.asc()
        )
        .all()
    )

    return {
        "study_dates": [
            session.study_date.isoformat()
            for session in sessions
        ]
    }




@router.delete("/reset")
def reset_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(LessonCompletion).filter(
        LessonCompletion.user_id == current_user.id
    ).delete(synchronize_session=False)

    db.query(StudySession).filter(
        StudySession.user_id == current_user.id
    ).delete(synchronize_session=False)

    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id)
        .first()
    )

    if progress:
        progress.xp = 0
        progress.streak = 0

    db.commit()

    return {
        "message": "Progress reset successfully",
        "xp": 0,
        "streak": 0,
        "completed_lessons": [],
        "study_dates": [],
    }


class GuestProgress(BaseModel):
    xp: int = 0
    completed_lessons: list[str] = []
    study_dates: list[str] = []


@router.post("/migrate")
def migrate_guest_progress(
    guest_progress: GuestProgress,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    
    progress = (
        db.query(UserProgress)
        .filter(
            UserProgress.user_id == current_user.id
        )
        .first()
    )

    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            xp=0,
            streak=0,
        )

        db.add(progress)
        db.flush()

    
    if guest_progress.xp < 0:
        raise HTTPException(
            status_code=400,
            detail="XP cannot be negative",
        )

    progress.xp += guest_progress.xp

    
    for lesson_id in guest_progress.completed_lessons:

        if not lesson_id:
            continue

        existing_completion = (
            db.query(LessonCompletion)
            .filter(
                LessonCompletion.user_id == current_user.id,
                LessonCompletion.lesson_id == lesson_id,
            )
            .first()
        )

        if existing_completion:
            continue

        completion = LessonCompletion(
            user_id=current_user.id,
            lesson_id=lesson_id,
            xp_earned=0,
        )

        db.add(completion)

    
    for study_date_string in guest_progress.study_dates:

        try:
            study_date = date.fromisoformat(
                study_date_string
            )
        except ValueError:
            continue

        existing_session = (
            db.query(StudySession)
            .filter(
                StudySession.user_id == current_user.id,
                StudySession.study_date == study_date,
            )
            .first()
        )

        if existing_session:
            continue

        session = StudySession(
            user_id=current_user.id,
            study_date=study_date,
        )

        db.add(session)

    db.flush()

    
    sessions = (
        db.query(StudySession)
        .filter(
            StudySession.user_id == current_user.id
        )
        .order_by(
            StudySession.study_date.desc()
        )
        .all()
    )

    if not sessions:
        progress.streak = 0

    else:
        dates = [
            session.study_date
            for session in sessions
        ]

        today = date.today()

        latest_date = dates[0]

        difference = (
            today - latest_date
        ).days

        if difference > 1:
            progress.streak = 0

        else:
            current_streak = 1
            expected_date = latest_date - timedelta(days=1)

            for study_date in dates[1:]:

                if study_date == expected_date:
                    current_streak += 1
                    expected_date -= timedelta(days=1)

                elif study_date < expected_date:
                    break

            progress.streak = current_streak

    db.commit()
    db.refresh(progress)

    return {
        "message": "Guest progress migrated successfully",
        "xp": progress.xp,
        "streak": progress.streak,
    }