from fastapi.testclient import TestClient
from .main import app
from . import schemas

client = TestClient(app)

db_user_id = -1
db_resume_id = -1
access_token = ""

def update_user_id(id: int):
    global db_user_id 
    db_user_id = id
    resume.user_id = id

def update_resume_id(id: int):
    global db_resume_id
    db_resume_id = id

def update_access_token(token: str):
    global access_token
    access_token = "Bearer " + token

# tests

def test_home():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == "it's a homepage"

def test_sign_up():
    response = client.post(
        "/api/signup",
        json=user.model_dump())

    assert response.json()["first_name"] == user.first_name
    assert response.json()["last_name"] == user.last_name

    assert response.status_code == 200

    update_user_id(response.json()["id"])

def test_sign_up_with_existing_email():
    response = client.post(
        "/api/signup",
        json=user.model_dump())
    
    assert response.status_code == 400

def test_post_resume():
    # test for first resume

    response = client.post(
            "/api/resumes/",
            json=resume.model_dump(exclude_unset=True)
        )
    
    assert response.json()["user_id"] == resume.user_id
    assert response.json()["title"] == resume.title
    assert response.json()["description"] == resume.description

    assert len(resume.educations) == len(response.json()["educations"])
    for education in response.json()["educations"]:
        assert schemas.Education(institution=education["institution"], degree=education["degree"]) in resume.educations

    assert len(resume.conferences) == len(response.json()["conferences"])
    for conference in response.json()["conferences"]:
        assert schemas.Conference(name=conference["name"], year=conference["year"]) in resume.conferences

    assert len(resume.skills) == len(response.json()["skills"])
    for skill in response.json()["skills"]:
        assert schemas.Skill(type=skill["type"], name=skill["name"]) in resume.skills

    assert len(resume.keywords) == len(response.json()["keywords"])
    for keyword in response.json()["keywords"]:
        assert schemas.Keyword(name=keyword["name"]) in resume.keywords

    assert response.status_code == 200

    update_resume_id(response.json()["id"])

def test_put_resume():
    response = client.put(
        f"/api/resumes/{db_resume_id}/",
        json=resume_upd.model_dump(exclude_unset=True)
    )

    assert response.json()["id"] == db_resume_id
    assert response.json()["user_id"] == db_user_id
    assert response.json()["title"] == resume_upd.title
    assert response.json()["description"] == resume_upd.description

    assert len(resume_upd.educations) == len(response.json()["educations"])
    for education in response.json()["educations"]:
        assert schemas.Education(institution=education["institution"], degree=education["degree"]) in resume_upd.educations

    assert len(resume_upd.conferences) == len(response.json()["conferences"])
    for conference in response.json()["conferences"]:
        assert schemas.Conference(name=conference["name"], year=conference["year"]) in resume_upd.conferences

    assert len(resume_upd.skills) == len(response.json()["skills"])
    for skill in response.json()["skills"]:
        assert schemas.Skill(type=skill["type"], name=skill["name"]) in resume_upd.skills

    assert len(resume_upd.keywords) == len(response.json()["keywords"])
    for keyword in response.json()["keywords"]:
        assert schemas.Keyword(name=keyword["name"]) in resume_upd.keywords
    
    assert response.status_code == 200

def test_patch_resume():
    response = client.patch(
        f"/api/resumes/{db_resume_id}/",
        json=resume_part_upd.model_dump(exclude_unset=True)
    )

    # change title and keywords

    assert response.json()["id"] == db_resume_id
    assert response.json()["user_id"] == db_user_id
    assert response.json()["title"] == resume_upd.title 
    assert response.json()["description"] == resume_part_upd.description # !!!

    assert len(resume_upd.educations) == len(response.json()["educations"])
    for education in response.json()["educations"]:
        assert schemas.Education(institution=education["institution"], degree=education["degree"]) in resume_upd.educations

    assert len(resume_upd.conferences) == len(response.json()["conferences"])
    for conference in response.json()["conferences"]:
        assert schemas.Conference(name=conference["name"], year=conference["year"]) in resume_upd.conferences

    assert len(resume_upd.skills) == len(response.json()["skills"])
    for skill in response.json()["skills"]:
        assert schemas.Skill(type=skill["type"], name=skill["name"]) in resume_upd.skills

    # !!!
    assert len(resume_part_upd.keywords) == len(response.json()["keywords"])
    for keyword in response.json()["keywords"]:
        assert schemas.Keyword(name=keyword["name"]) in resume_part_upd.keywords

    assert response.status_code == 200

def test_delete_resume_without_auth():
    response = client.delete(
        f"/api/resumes/{db_resume_id}/",
        headers={"Authorization": access_token},
    )

    assert response.status_code == 403

def test_sign_in():
    response = client.post(
        "/api/signin",
        json=user_auth.model_dump(exclude_unset=True)
    )

    assert response.json()["token_type"] == "bearer"
    assert response.status_code == 200

    update_access_token(response.json()["access_token"])

def test_delete_resume_with_auth():
    response = client.delete(
        f"/api/resumes/{db_resume_id}/",
        headers={"Authorization": access_token},
    )

    assert response.json()["id"] == db_resume_id
    assert response.json()["user_id"] == db_user_id
    assert response.json()["title"] == resume_upd.title
    assert response.json()["description"] == resume_part_upd.description

    assert len(resume_upd.educations) == len(response.json()["educations"])
    for education in response.json()["educations"]:
        assert schemas.Education(institution=education["institution"], degree=education["degree"]) in resume_upd.educations

    assert len(resume_upd.conferences) == len(response.json()["conferences"])
    for conference in response.json()["conferences"]:
        assert schemas.Conference(name=conference["name"], year=conference["year"]) in resume_upd.conferences

    assert len(resume_upd.skills) == len(response.json()["skills"])
    for skill in response.json()["skills"]:
        assert schemas.Skill(type=skill["type"], name=skill["name"]) in resume_upd.skills

    assert len(resume_part_upd.keywords) == len(response.json()["keywords"])
    for keyword in response.json()["keywords"]:
        assert schemas.Keyword(name=keyword["name"]) in resume_part_upd.keywords

    assert response.status_code == 200

# for sign up test only

def test_delete_user():
    response = client.delete(
        f"/api/users/{db_user_id}",
        headers={"Authorization": access_token},
    )

    assert response.status_code == 200

user = schemas.UserCreate(
        email="working_email@yandex.ru", 
        password="123secretpassword456", 
        first_name="Willy", 
        last_name="Wonka"
    )

user_auth = schemas.UserAuth(
    email=user.email,
    password=user.password
)

education_1 = schemas.Education(
    institution="Southern Federal University",
    degree="Bachelor"
)
education_2 = schemas.Education(
    institution="Berkeley University",
    degree="Master"
)

conference_1 = schemas.Conference(
    name="C# for everyone",
    year="2017"
)
conference_2 = schemas.Conference(
    name="Data Science for everyone",
    year="2019"
)

skill_1 = schemas.Skill(
    type="Programming language",
    name="C#"
)
skill_2 = schemas.Skill(
    type="English level",
    name="Upper Intermediate"
)
skill_3 = schemas.Skill(
    type="Programming language",
    name="Python"
)
skill_4 = schemas.Skill(
    type="English level",
    name="Advanced"
)

keyword_1 = schemas.Keyword(
    name="IT"
)
keyword_2 = schemas.Keyword(
    name="Full time"
)
keyword_3 = schemas.Keyword(
    name="Big salary"
)

resume = schemas.ResumeCreate(
    user_id=-1,
    title="Just a resume",
    description="Resume of a cool developer",
    educations=[education_1, education_2],
    conferences=[conference_1],
    skills=[skill_1, skill_2],
    keywords=[keyword_1, keyword_2]
)

resume_upd = schemas.ResumeUpdate(
    title="Just my resume",
    educations=[education_1, education_2],
    conferences=[conference_2],
    skills=[skill_3, skill_4],
    keywords=[keyword_1, keyword_2]
)

resume_part_upd = schemas.ResumeUpdate(
    description="Resume of a cool data scientist",
    keywords=[keyword_3]
)