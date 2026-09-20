
from datetime import datetime, date

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    level: Mapped[str] = mapped_column(
        String(10),
        default="A0",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    progress: Mapped["UserProgress | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    lesson_completions: Mapped[list["LessonCompletion"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    study_sessions: Mapped[list["StudySession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    auth_accounts: Mapped[list["AuthAccount"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    achievements: Mapped[list["UserAchievement"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    daily_challenge_completions: Mapped[
        list["DailyChallengeCompletion"]
    ] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )



class AuthAccount(Base):
    __tablename__ = "auth_accounts"

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_user_id",
            name="uq_auth_provider_user",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="auth_accounts",
    )



class UserProgress(Base):
    __tablename__ = "user_progress"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    xp: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    streak: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="progress",
    )



class LessonCompletion(Base):
    __tablename__ = "lesson_completions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    lesson_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    xp_earned: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="lesson_completions",
    )



class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    study_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="study_sessions",
    )



class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    icon: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    user_achievements: Mapped[
        list["UserAchievement"]
    ] = relationship(
        back_populates="achievement",
        cascade="all, delete-orphan",
    )



class DailyChallenge(Base):
    __tablename__ = "daily_challenges"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "challenge_date",
            name="uq_user_daily_challenge_date",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    challenge_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    xp_reward: Mapped[int] = mapped_column(
        Integer,
        default=25,
        nullable=False,
    )

    questions: Mapped[
        list["DailyChallengeQuestion"]
    ] = relationship(
        back_populates="challenge",
        cascade="all, delete-orphan",
    )

    completions: Mapped[
        list["DailyChallengeCompletion"]
    ] = relationship(
        back_populates="challenge",
        cascade="all, delete-orphan",
    )

    user: Mapped["User"] = relationship()



class DailyChallengeQuestion(Base):
    __tablename__ = "daily_challenge_questions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("daily_challenges.id"),
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    options: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    correct_answer: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    challenge: Mapped["DailyChallenge"] = relationship(
        back_populates="questions",
    )



class DailyChallengeCompletion(Base):
    __tablename__ = "daily_challenge_completions"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "challenge_id",
            name="uq_user_daily_challenge",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    challenge_id: Mapped[int] = mapped_column(
        ForeignKey("daily_challenges.id"),
        nullable=False,
    )

    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="daily_challenge_completions",
    )

    challenge: Mapped["DailyChallenge"] = relationship(
        back_populates="completions",
    )



class UserAchievement(Base):
    __tablename__ = "user_achievements"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "achievement_id",
            name="uq_user_achievement",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id"),
        nullable=False,
    )

    unlocked_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="achievements",
    )

    achievement: Mapped["Achievement"] = relationship(
        back_populates="user_achievements",
    )



class UserLearnedWord(Base):
    __tablename__ = "user_learned_words"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "word",
            name="uq_user_learned_word",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    word: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    translation: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    example: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    example_translation: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    level: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    learned_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship()




class UserFavoriteWord(Base):
    __tablename__ = "user_favorite_words"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "word",
            name="uq_user_favorite_word",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    word: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    translation: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    example_1: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    example_2: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    example_translation_1: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    example_translation_2: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    level: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    favorited_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship()