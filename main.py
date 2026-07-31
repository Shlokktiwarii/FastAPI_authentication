from fastapi import FastAPI, HTTPException ,Header ,Depends
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

@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }
def verify_token(authorization:str=Header(default=None)):
    if (
            authorization is None
            or not authorization.startswith("Bearer ")
            or len(authorization.split(" ")) < 2
        ):
            raise HTTPException(
                status_code=401,
                detail={"error": "Access token required"}
            )
    
    token = authorization.split(" ")[1]
    
    try:
        response= supabase.auth.get_user(token)
        return response.user
    except Exception as e:
        raise HTTPException (
           status_code=401,detail=str(e))
        
@app.get("/protected/profile")
def protected_profile(user=Depends(verify_token)):

    return {
        "message": "Protected route accessed.",
        "user": user
    }
@app.post("/auth/signup")
def signup(user: UserAuth):
    try:
        response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password
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
                "password": user.password
            }
        )
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/auth/logout",status_code=200)
def logout(token: str=Depends(verify_token)):
    try:
        supabase.auth.sign_out()

        return {
            "message":"Logged out successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400,detail=str(e))
