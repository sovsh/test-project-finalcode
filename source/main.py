from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Annotated
from . import crud, models, schemas
from .database import SessionLocal, engine
from fastapi.openapi.utils import get_openapi

# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)
 
app = FastAPI()

# schema will be generated only once, and then the same cached schema will be used for the next requests
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Test Task",
        version="1.0.0",
        summary="Resume storage application",
        description="Documentation with **examples** of requests and successful server responses",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

security = HTTPBearer()

# response is a json as defualt

# the dependency will create a new SQLAlchemy SessionLocal that will be used in a single request, 
# and then close it once the request is finished;
# the code following the yield statement is executed after the response has been delivered

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return JSONResponse("it's a homepage")

@app.post("/api/signup", response_model=schemas.UserResponse)
def sign_up(user: schemas.UserCreate, db: Session = Depends(get_db)): # db is a default argument
    if crud.find_user_email(db=db, user_email=user.email) != None:
        raise HTTPException(status_code=400, detail="The email is already used")
    
    return crud.create_user(db=db, user=user)

@app.post("/api/signin", response_model=schemas.TokenResponse)
def sign_in(user: schemas.UserAuth, db: Session = Depends(get_db)):
    response = crud.authenticate_user(db=db, user=user)
    if response == None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return crud.create_access_token(token_data=response)

@app.post("/api/resumes", response_model=schemas.ResumeResponse)
def post_resume(resume: schemas.ResumeCreate, db: Session = Depends(get_db)):
    if crud.find_user_id(db=db, user_id=resume.user_id) == None:
        raise HTTPException(status_code=404, detail="User is not found")

    return crud.create_resume(db=db, resume=resume)

@app.get("/api/resumes/{resume_id}", response_model=schemas.ResumeResponse) 
def get_resume(resume_id: int, db: Session = Depends(get_db)): 
    if crud.find_resume_id(db=db, resume_id=resume_id) == None:
        raise HTTPException(status_code=404, detail="Resume is not found")
    
    return crud.get_resume(db=db, resume_id=resume_id)

@app.put("/api/resumes/{resume_id}", response_model=schemas.ResumeResponse)
def put_resume(resume_id: int, resume: schemas.ResumeUpdate, db: Session = Depends(get_db)):
    if crud.find_resume_id(db=db, resume_id=resume_id) == None:
        raise HTTPException(status_code=404, detail="Resume is not found")
    
    return crud.update_resume(db=db, resume_id=resume_id, resume=resume)

@app.patch("/api/resumes/{resume_id}", response_model=schemas.ResumeResponse)
def patch_resume(resume_id: int, resume: schemas.ResumeUpdate, db: Session = Depends(get_db)):
    if crud.find_resume_id(db=db, resume_id=resume_id) == None:
        raise HTTPException(status_code=404, detail="Resume is not found")
    
    return crud.partial_update_resume(db=db, resume_id=resume_id, resume=resume)

# https://stackoverflow.com/questions/3297048/403-forbidden-vs-401-unauthorized-http-responses

@app.delete("/api/resumes/{resume_id}", response_model=schemas.ResumeResponse) 
def delete_resume(resume_id: int, Authorization: Annotated[str, Depends(security)], db: Session = Depends(get_db)): 
    if not crud.is_token_authorized(db=db, token=Authorization):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    if crud.find_resume_id(db=db, resume_id=resume_id) == None:
        raise HTTPException(status_code=404, detail="Resume is not found")
    
    return crud.delete_resume(db=db, resume_id=resume_id)
    
# rout to delete user for testing only for testing

@app.delete("/api/users/{user_id}", include_in_schema=False) 
def delete_resume(user_id: int, Authorization: Annotated[str, Depends(security)], db: Session = Depends(get_db)): 
    if not crud.is_token_authorized(db=db, token=Authorization):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    
    if crud.find_user_id(db=db, user_id=user_id) == None:
        raise HTTPException(status_code=404, detail="User is not found")
    
    return crud.delete_user(db=db, user_id=user_id)
    