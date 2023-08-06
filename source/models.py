import datetime
from typing import List
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]

    resumes: Mapped[List["Resume"]] = relationship()

class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    title: Mapped[str]
    description: Mapped[str]

    # as child
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # as parent
    educations: Mapped[List["Education"]] = relationship()
    conferences: Mapped[List["Conference"]] = relationship()

    # associations 
    skills: Mapped[List["ResumeSkillAssociation"]] = relationship()
    keywords: Mapped[List["ResumeKeywordAssociation"]] = relationship()

class Education(Base):
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    institution: Mapped[str]
    degree: Mapped[str]
    resume_id: Mapped["Resume"] = mapped_column(ForeignKey("resumes.id"))

class Conference(Base):
    __tablename__ = "conferences"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    year: Mapped[int]
    resume_id: Mapped["Resume"] = mapped_column(ForeignKey("resumes.id"))

class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[str]
    name: Mapped[str]

class ResumeSkillAssociation(Base):
    __tablename__ = "resume_skill_associations"

    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id"), primary_key=True)

    skills: Mapped["Skill"] = relationship()

class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]

class ResumeKeywordAssociation(Base):
    __tablename__ = "resume_keyword_associations"

    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), primary_key=True)
    keyword_id: Mapped[int] = mapped_column(ForeignKey("keywords.id"), primary_key=True)

    keyword: Mapped["Keyword"] = relationship()