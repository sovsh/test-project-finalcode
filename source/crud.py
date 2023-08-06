from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi.security import HTTPAuthorizationCredentials
from . import models, schemas
from .secret_variables import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# authentification functions

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str):
    return pwd_context.hash(password)

def find_user_email(db: Session, user_email: str):
    return db.query(models.User).filter(models.User.email == user_email).first()

def create_access_token(token_data: schemas.TokenCreate): 
    to_encode = token_data.model_dump().copy() 
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # exp ONLY!!!
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return schemas.TokenResponse(access_token=encoded_jwt)

def authenticate_user(db: Session, user: schemas.UserAuth):
    db_user = find_user_email(db=db, user_email=user.email)

    if db_user == None:
        return None
    if not verify_password(user.password, db_user.password):
        return None
    
    return schemas.TokenCreate(email=db_user.email)

def is_token_authorized(db: Session, token: HTTPAuthorizationCredentials):
    # expiration check works
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return False
    
    db_user = find_user_email(db=db, user_email=payload["email"])
    if db_user == None:
        return False
    
    return True
    
# create responses functions

def find_user_resumes(db: Session, user_id: int):
    return db.query(models.Resume).filter(models.Resume.user_id == user_id).all()

def create_user_response(db: Session, user: models.User):
    user_response = schemas.UserResponse(id=user.id, email=user.email, first_name=user.first_name, last_name=user.last_name)
    for resume in find_user_resumes(db=db, user_id=user.id):
        user_response.resume_ids.append(resume.id)

    return user_response

def create_resume_response(db: Session, resume_id: int):
    resume = find_resume_id(db=db, resume_id=resume_id)
    resume_response = schemas.ResumeResponse(id=resume.id, user_id=resume.user_id, date=resume.date, title=resume.title, description=resume.description)

    for education in find_resume_educations(db=db, resume_id=resume_id):
        resume_response.educations.append(schemas.EducationResponse(id=education.id, institution=education.institution, degree=education.degree))

    for conference in find_resume_conferences(db=db, resume_id=resume_id):
        resume_response.conferences.append(schemas.ConferenceResponse(id=conference.id, name=conference.name, year=conference.year))

    for skill in find_resume_skills(db=db, resume_id=resume_id):
        resume_response.skills.append(schemas.SkillResponse(id=skill.id, type=skill.type, name=skill.name))

    for keyword in find_resume_keywords(db=db, resume_id=resume_id):
        resume_response.keywords.append(schemas.KeywordResponse(id=keyword.id, name=keyword.name))

    return resume_response

# find by entity functions

def find_skill(db: Session, skill: schemas.Skill):
    return db.query(models.Skill).filter(models.Skill.type == skill.type, models.Skill.name == skill.name).first()

def find_keyword(db: Session, keyword: schemas.Keyword):
    keyword = db.query(models.Keyword).filter(models.Keyword.name == keyword.name).first()
    return keyword

# find entity by id functions

def find_user_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def find_resume_id(db: Session, resume_id: int):
    return db.query(models.Resume).filter(models.Resume.id == resume_id).first()

def find_skill_id(db: Session, skill_id: int):
    return db.query(models.Skill).filter(models.Skill.id == skill_id).first()

def find_keyword_id(db: Session, keyword_id: int):
    return db.query(models.Keyword).filter(models.Keyword.id == keyword_id).first()

# find associations by entity id functions

def find_skill_associations_id(db: Session, skill_id: int):
    return db.query(models.ResumeSkillAssociation).filter(models.ResumeSkillAssociation.skill_id == skill_id).all()

def find_keyword_associations_id(db: Session, keyword_id: int):
    return db.query(models.ResumeKeywordAssociation).filter(models.ResumeKeywordAssociation.keyword_id == keyword_id).all()

# find resume children by resume id functions

def find_resume_educations(db: Session, resume_id: int):
    return db.query(models.Education).filter(models.Education.resume_id == resume_id).all()

def find_resume_conferences(db: Session, resume_id: int):
    return db.query(models.Conference).filter(models.Conference.resume_id == resume_id).all()

def find_resume_skill_associations(db: Session, resume_id: int):
    return db.query(models.ResumeSkillAssociation).filter(models.ResumeSkillAssociation.resume_id == resume_id).all()

def find_resume_skills(db: Session, resume_id: int):
    skills = []
    for resume_skill in find_resume_skill_associations(db=db, resume_id=resume_id):
        skills.append(find_skill_id(db=db, skill_id=resume_skill.skill_id))

    return skills

def find_resume_keyword_associations(db: Session, resume_id: int):
    return db.query(models.ResumeKeywordAssociation).filter(models.ResumeKeywordAssociation.resume_id == resume_id).all()

def find_resume_keywords(db: Session, resume_id: int):
    keywords = []
    for resume_keyword in find_resume_keyword_associations(db=db, resume_id=resume_id):
        keywords.append(find_keyword_id(db=db, keyword_id=resume_keyword.keyword_id))

    return keywords

# get entity functions

def get_resume(db: Session, resume_id: int):
    return create_resume_response(db=db, resume_id=resume_id)

# create entity functions

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hash_password(user.password)
    # **user.dict() can be used
    db_user = models.User(email = user.email, password = hashed_password, first_name = user.first_name, last_name = user.last_name)
    db.add(db_user)
    db.commit()
    # refresh your instance (so that it contains any new data from the database, like the generated ID)
    db.refresh(db_user) 
    
    return create_user_response(db=db, user=db_user)

def create_resume(db: Session, resume: schemas.ResumeCreate):
    db_resume = models.Resume(title=resume.title, description=resume.description, user_id=resume.user_id)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)

    for education in resume.educations:
        create_education(db=db, education=education, resume_id=db_resume.id)
    for conference in resume.conferences:
        create_conference(db=db, conference=conference, resume_id=db_resume.id)
    for skill in resume.skills:
        create_skill(db=db, skill=skill, resume_id=db_resume.id)
    for keyword in resume.keywords:
        create_keyword(db=db, keyword=keyword, resume_id=db_resume.id)

    return create_resume_response(db=db, resume_id=db_resume.id)

def create_education(db: Session, education: schemas.Education, resume_id: int):
    db_education = models.Education(institution=education.institution, degree=education.degree, resume_id=resume_id)
    db.add(db_education)
    db.commit()
    db.refresh(db_education)

def create_conference(db: Session, conference: schemas.Conference, resume_id: int):
    db_conference = models.Conference(name=conference.name, year=conference.year, resume_id=resume_id)
    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)

def create_skill(db: Session, skill: schemas.Skill, resume_id: int):
    db_skill = find_skill(db=db, skill=skill)

    if db_skill == None:
        db_skill = models.Skill(type=skill.type, name=skill.name)
        db.add(db_skill)
        db.commit()
        db.refresh(db_skill)

    db_resume_skill = models.ResumeSkillAssociation(resume_id=resume_id, skill_id=db_skill.id)
    db.add(db_resume_skill)
    db.commit()
    db.refresh(db_resume_skill)

def create_keyword(db: Session, keyword: schemas.Keyword, resume_id: int):
    db_keyword = find_keyword(db=db, keyword=keyword)

    if db_keyword == None:
        db_keyword = models.Keyword(name=keyword.name)
        db.add(db_keyword)
        db.commit()
        db.refresh(db_keyword)

    db_resume_keyword = models.ResumeKeywordAssociation(resume_id=resume_id, keyword=db_keyword)
    db.add(db_resume_keyword)
    db.commit()
    db.refresh(db_resume_keyword)

# update entity functions

def update_resume_educations(db: Session, resume_id: int, resume: schemas.ResumeUpdate):
    delete_resume_educations(db=db, resume_id=resume_id)
    for education in resume.educations:
        create_education(db=db, education=education, resume_id=resume_id)

def update_resume_conferences(db: Session, resume_id: int, resume: schemas.ResumeUpdate):
    delete_resume_conferences(db=db, resume_id=resume_id)
    for conference in resume.conferences:
        create_conference(db=db, conference=conference, resume_id=resume_id)

def update_resume_skills(db: Session, resume_id: int, resume: schemas.ResumeUpdate):
    delete_resume_skills(db=db, resume_id=resume_id)
    for skill in resume.skills:
        create_skill(db=db, skill=skill, resume_id=resume_id)

def update_resume_keywords(db: Session, resume_id: int, resume: schemas.ResumeUpdate):
    delete_resume_keywords(db=db, resume_id=resume_id)
    for keyword in resume.keywords:
        create_keyword(db=db, keyword=keyword, resume_id=resume_id)

def update_resume(db: Session, resume_id: int, resume: schemas.ResumeUpdate):
    db_resume = find_resume_id(db=db, resume_id=resume_id)
    updatable_keys = ["title", "description"]
    resume_data = resume.model_dump(exclude_unset=False)
    
    for key, value in resume_data.items():
            if key in updatable_keys:
                setattr(db_resume, key, value)
    db.commit()
    db.refresh(db_resume)
    
    update_resume_educations(db=db, resume_id=resume_id, resume=resume)
    update_resume_conferences(db=db, resume_id=resume_id, resume=resume)
    update_resume_skills(db=db, resume_id=resume_id, resume=resume)
    update_resume_keywords(db=db, resume_id=resume_id, resume=resume)

    return create_resume_response(db=db, resume_id=db_resume.id)

def partial_update_resume(db: Session, resume_id: int, resume: schemas.ResumeUpdate):
    db_resume = find_resume_id(db=db, resume_id=resume_id)
    updatable_keys = ["title", "description"]
    resume_data = resume.model_dump(exclude_unset=True)

    for key, value in resume_data.items():
            if key in updatable_keys:
                setattr(db_resume, key, value)
    db.commit()
    db.refresh(db_resume)

    if resume.educations != []:
        update_resume_educations(db=db, resume_id=resume_id, resume=resume)
    if resume.conferences != []:
        update_resume_conferences(db=db, resume_id=resume_id, resume=resume)
    if resume.skills != []:
        update_resume_skills(db=db, resume_id=resume_id, resume=resume)
    if resume.keywords != []:
        update_resume_keywords(db=db, resume_id=resume_id, resume=resume)

    return create_resume_response(db=db, resume_id=db_resume.id)

# delete entity functions

def delete_resume_educations(db: Session, resume_id: int):
    for education in find_resume_educations(db=db, resume_id=resume_id):
        db.delete(education)
        db.commit()

def delete_resume_conferences(db: Session, resume_id: int):
    for conference in find_resume_conferences(db=db, resume_id=resume_id):
        db.delete(conference)
        db.commit()

def delete_resume_skills(db: Session, resume_id: int):
    resume_skills = find_resume_skill_associations(db=db, resume_id=resume_id)
    for resume_skill in resume_skills:
        db.delete(resume_skill)
        db.commit()
        if find_skill_associations_id(db=db, skill_id=resume_skill.skill_id) == []:
            skill = find_skill_id(db=db, skill_id=resume_skill.skill_id) # skill
            db.delete(skill)
            db.commit()

def delete_resume_keywords(db: Session, resume_id: int):
    resume_keywords = find_resume_keyword_associations(db=db, resume_id=resume_id) # assocs
    for resume_keyword in resume_keywords:
        db.delete(resume_keyword)
        db.commit()
        if find_keyword_associations_id(db=db, keyword_id=resume_keyword.keyword_id) == []:
            keyword = find_keyword_id(db=db, keyword_id=resume_keyword.keyword_id) # keyword
            db.delete(keyword)
            db.commit()

def delete_resume(db: Session, resume_id: int):
    resume_response = create_resume_response(db=db, resume_id=resume_id)

    delete_resume_educations(db=db, resume_id=resume_id)
    delete_resume_conferences(db=db, resume_id=resume_id)
    delete_resume_skills(db=db, resume_id=resume_id)
    delete_resume_keywords(db=db, resume_id=resume_id)

    db_resume = find_resume_id(db=db, resume_id=resume_id)
    db.delete(db_resume)
    db.commit()

    return resume_response

# function to delete user for testing only

def delete_user(db: Session, user_id: int):
    db_user = find_user_id(db=db, user_id=user_id)

    for resume in db_user.resumes:
        delete_resume(db=db, resume_id=resume.id)
    
    db.delete(db_user)
    db.commit()