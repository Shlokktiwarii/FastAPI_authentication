from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

class UserAuth(BaseModel):
    email: str
    password: str

@app.get("/")
def home():
    return {"message": "Connected to Supabase successfully!"}

@app.post("/auth/signup")
def signup(user: UserAuth):
    try:
        response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password,
            }
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/auth/login",status_code=200)
def login(user: UserAuth):
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": user.email,
                "password": user.password,
            }
        )
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
