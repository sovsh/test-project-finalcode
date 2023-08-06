import datetime
from pydantic import BaseModel, ConfigDict
from typing import List

class Base(BaseModel):
    # read the data even if it is not a dict, but an ORM model
    model_config = ConfigDict(from_attributes=True)

class TokenCreate(BaseModel):
    email: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "CI6IkpXVCJ9.eyJzdWIikpvaG4gRG9lIiwiaWF0Ijo",
                    "token_type": "bearer"
                }
            ]
        }
    }

class UserCreate(Base):
    email: str
    password: str
    first_name: str
    last_name: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "cool_email@gmail.com",
                    "password": "supercoolpassword123",
                    "first_name": "Ryan",
                    "last_name": "Gosling",
                }
            ]
        }
    }

class UserAuth(Base):
    email: str
    password: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "cool_email@gmail.com",
                    "password": "supercoolpassword123",
                }
            ]
        }
    }

class UserResponse(Base):
    id: int
    email: str
    first_name: str
    last_name: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {   
                    "id": 23,
                    "email": "cool_email@gmail.com",
                    "first_name": "Ryan",
                    "last_name": "Gosling",
                }
            ]
        }
    }

class Education(Base):
    institution: str
    degree: str

class EducationResponse(Education):
    id: int

class Conference(Base):
    name: str
    year: int

class ConferenceResponse(Conference):
    id: int

class Skill(Base):
    type: str
    name: str

class SkillResponse(Skill):
    id: int

class Keyword(Base):
    name: str

class KeywordResponse(Keyword):
    id: int

class ResumeCreate(Base):
    user_id: int
    title: str
    description: str = ""
    educations: List[Education] = []
    conferences: List[Conference] = []
    skills: List[Skill] = []
    keywords: List[Keyword] = []   

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": 23,
                    "title": "My cool resume",
                    "description": "Cool resume for a cool company",
                    "educations": [
                        {
                            "institution": "Southern Federal University",
                            "degree": "Bachelor"
                        },
                        {
                            "institution": "Moscow State University",
                            "degree": "Master"
                        }
                    ],
                    "conferences": [
                        {
                            "name": "Spring for professionals",
                            "year": 2023
                        }
                    ],
                    "skills": [
                        {
                            "type": "Framework",
                            "name": "Spring"
                        },
                        {
                            "type": "Programming language",
                            "name": "Java"
                        }
                    ],
                    "keywords": [
                        {
                            "name": "Remote working"
                        }
                    ]
                }
            ]
        }
    }    
    
class ResumeUpdate(Base):
    title: str | None = ""
    description: str | None = ""
    educations: List[Education] | None = []
    conferences: List[Conference] | None = []
    skills: List[Skill] | None = []
    keywords: List[Keyword] | None = []    

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "My cool resume",
                    "description": "Cool resume for a cool company",
                    "educations": [
                        {
                            "institution": "Southern Federal University",
                            "degree": "Bachelor"
                        },
                        {
                            "institution": "Moscow State University",
                            "degree": "Master"
                        }
                    ],
                    "conferences": [
                        {
                            "name": "Spring for professionals",
                            "year": 2023
                        }
                    ],
                    "skills": [
                        {
                            "type": "Framework",
                            "name": "Spring"
                        },
                        {
                            "type": "Programming language",
                            "name": "Java"
                        }
                    ],
                    "keywords": [
                        {
                            "name": "Remote working"
                        }
                    ]
                }
            ]
        }
    } 

class ResumeResponse(Base):
    id: int
    user_id: int
    date: datetime.datetime
    title: str
    description: str
    educations: List[EducationResponse] = []
    conferences: List[ConferenceResponse] = []
    skills: List[SkillResponse] = []
    keywords: List[KeywordResponse] = [] 

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 28,
                    "user_id": 23,
                    "date": "2006-10-20T22:50:50.804565+03:00",
                    "title": "My cool resume",
                    "description": "Cool resume for a cool company",
                    "educations": [
                        {
                            "institution": "Southern Federal University",
                            "degree": "Bachelor"
                        },
                        {
                            "institution": "Moscow State University",
                            "degree": "Master"
                        }
                    ],
                    "conferences": [
                        {
                            "name": "Spring for professionals",
                            "year": 2023
                        }
                    ],
                    "skills": [
                        {
                            "type": "Framework",
                            "name": "Spring"
                        },
                        {
                            "type": "Programming language",
                            "name": "Java"
                        }
                    ],
                    "keywords": [
                        {
                            "name": "Remote working"
                        }
                    ]
                }
            ]
        }
    }    