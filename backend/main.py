import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_all, Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/dbname")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    nickname = Column(String, primary_key=True, index=True)
    count = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRequest(BaseModel):
    nickname: str

@app.post("/increment")
async def increment_counter(user_req: UserRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.nickname == user_req.nickname).first()
        if not user:
            user = User(nickname=user_req.nickname, count=1)
            db.add(user)
        else:
            user.count += 1
        
        db.commit()
        db.refresh(user)
        return {"nickname": user.nickname, "count": user.count}
    finally:
        db.close()
