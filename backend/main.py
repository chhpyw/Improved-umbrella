import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine # FIXED: removed create_all
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True)
    count = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # FIXED: allow all for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRequest(BaseModel):
    nickname: str

@app.post("/increment")
def increment_counter(user_req: UserRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.nickname == user_req.nickname).first()
    if not user:
        user = User(nickname=user_req.nickname, count=1)
        db.add(user)
    else:
        user.count += 1
    db.commit()
    db.refresh(user)
    db.close()
    return {"nickname": user.nickname, "count": user.count}
