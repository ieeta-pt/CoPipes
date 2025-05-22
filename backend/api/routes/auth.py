from fastapi import APIRouter
from database import SupabaseClient
from schemas.user import UserRegister, UserLogin, UserUpdate

router = APIRouter(
    prefix="/api/auth",
)

supabase = SupabaseClient()

@router.post("/signup")
async def signup(user_data: UserRegister):
    return supabase.sign_up(user_data)

@router.post("/signin")
async def signin(user_data: UserLogin):
    return supabase.sign_in(user_data)

@router.get("/signout")
async def signout():
    return supabase.sign_out()

@router.post("/resetpassword")
async def resetpassword(email: str):
    return supabase.reset_password(email)

@router.put("/updateprofile")
async def updateprofile(user_data: UserUpdate):
    return supabase.update_profile(user_data)