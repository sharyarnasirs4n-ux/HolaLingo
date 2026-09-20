
from datetime import date
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import (
    User,
    UserLearnedWord,
    DailyChallenge,
    DailyChallengeQuestion,
    DailyChallengeCompletion,
)


router = APIRouter(
    prefix="/daily-challenge",
    tags=["Daily Challenge"],
)



@router.get("")
def get_daily_challenge(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()

    
    challenge = (
        db.query(DailyChallenge)
        .filter(
            DailyChallenge.user_id == current_user.id,
            DailyChallenge.challenge_date == today,
        )
        .first()
    )

    
    if not challenge:

        learned_words = (
            db.query(UserLearnedWord)
            .filter(
                UserLearnedWord.user_id == current_user.id
            )
            .all()
        )

        if len(learned_words) < 5:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Complete more lessons to unlock "
                    "today's challenge. "
                    f"You currently have {len(learned_words)} "
                    "learned words. You need at least 5."
                ),
            )

        
        selected_words = random.sample(
            learned_words,
            5,
        )

       
        challenge = DailyChallenge(
            user_id=current_user.id,
            challenge_date=today,
            title="Daily Spanish Challenge",
            description="Test your Spanish skills today",
            xp_reward=25,
        )

        db.add(challenge)
        db.flush()

        
        for learned_word in selected_words:

            other_words = [
                word
                for word in learned_words
                if word.word != learned_word.word
            ]

            wrong_words = random.sample(
                other_words,
                min(3, len(other_words)),
            )

            wrong_answers = [
                word.translation
                for word in wrong_words
            ]

            options = [
                learned_word.translation,
                *wrong_answers,
            ]

            random.shuffle(options)

            question = DailyChallengeQuestion(
                challenge_id=challenge.id,
                question=(
                    f'What does "{learned_word.word}" mean?'
                ),
                options=options,
                correct_answer=learned_word.translation,
            )

            db.add(question)

        db.commit()
        db.refresh(challenge)

    
    completion = (
        db.query(DailyChallengeCompletion)
        .filter(
            DailyChallengeCompletion.user_id == current_user.id,
            DailyChallengeCompletion.challenge_id == challenge.id,
        )
        .first()
    )

    
    questions = []

    for question in challenge.questions:
        questions.append(
            {
                "id": question.id,
                "question": question.question,
                "options": question.options,
            }
        )

    return {
        "id": challenge.id,
        "title": challenge.title,
        "description": challenge.description,
        "xp_reward": challenge.xp_reward,
        "completed": completion is not None,
        "questions": questions,
    }



@router.post("/complete")
def complete_daily_challenge(
    challenge_id: int,
    answers: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
   
    challenge = (
        db.query(DailyChallenge)
        .filter(
            DailyChallenge.id == challenge_id,
            DailyChallenge.user_id == current_user.id,
        )
        .first()
    )

    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="Daily challenge not found",
        )

    
    if challenge.challenge_date != date.today():
        raise HTTPException(
            status_code=400,
            detail="This challenge is not today's challenge",
        )

    
    existing_completion = (
        db.query(DailyChallengeCompletion)
        .filter(
            DailyChallengeCompletion.user_id == current_user.id,
            DailyChallengeCompletion.challenge_id == challenge.id,
        )
        .first()
    )

    if existing_completion:
        raise HTTPException(
            status_code=400,
            detail="Daily challenge already completed",
        )

    
    score = 0

    for question in challenge.questions:

        user_answer = answers.get(
            str(question.id)
        )

        if user_answer == question.correct_answer:
            score += 1

    total_questions = len(
        challenge.questions
    )

    
    completion = DailyChallengeCompletion(
        user_id=current_user.id,
        challenge_id=challenge.id,
        score=score,
    )

    db.add(completion)

    
    xp_earned = challenge.xp_reward

    if current_user.progress:
        current_user.progress.xp += xp_earned

    db.commit()

    return {
        "message": "Daily challenge completed",
        "score": score,
        "total_questions": total_questions,
        "xp_earned": xp_earned,
        "total_xp": (
            current_user.progress.xp
            if current_user.progress
            else 0
        ),
        "completed": True,
    }

