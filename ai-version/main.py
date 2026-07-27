"""
AI-Generated Version for Stage 7: The AI Rematch
Generated based on prompt specification to compare against human implementation.
"""
import os
from fastapi import FastAPI, Depends, HTTPException, Header, status
from pydantic import BaseModel
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="AI Auth API")


class AuthSchema(BaseModel):
    email: str
    password: str


@app.post("/auth/signup")
def signup(data: AuthSchema):
    # AI code directly calls sign_up without empty string check or custom exception formatting
    res = supabase.auth.sign_up({"email": data.email, "password": data.password})
    return res


@app.post("/auth/login")
def login(data: AuthSchema):
    # AI code does not check rate limiting and returns raw supabase object or missing 401 handler
    res = supabase.auth.sign_in_with_password({"email": data.email, "password": data.password})
    return res


def get_token_user(authorization: str = Header(None)):
    # AI Flaw 1: Token extraction fails or crashes if Authorization header is missing or improperly formatted
    if not authorization:
        raise HTTPException(status_code=401, detail="No token")
    # Simple split without checking length or prefix case sensitivity
    token = authorization.split(" ")[1]
    # AI Flaw 2: Unsafe error handling -- assumes get_user never raises an exception
    user_res = supabase.auth.get_user(token)
    return user_res.user


@app.get("/public/info")
def public_info():
    return {"message": "Welcome stranger! This info is public."}


@app.get("/protected/profile")
def profile(user=Depends(get_token_user)):
    return {"user": user}


@app.post("/auth/logout")
def logout(authorization: str = Header(None)):
    # AI Flaw 3: Does not use reusable dependency guard; repeats raw header parsing
    supabase.auth.sign_out()
    return {"status": "logged out"}
