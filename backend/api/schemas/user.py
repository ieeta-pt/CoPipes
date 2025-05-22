from pydantic import BaseModel, EmailStr

class BaseUser(BaseModel):
    id: str | None = None
    email: EmailStr
    
class UserRegister(BaseUser):
    full_name: str
    password: str

class UserLogin(BaseUser):
    password: str

class UserProfile(BaseUser):
    full_name: str
    avatar_url: str | None = None

class UserUpdate(BaseUser):
    full_name: str | None = None
    avatar_url: str | None = None
    password: str | None = None
    email: EmailStr | None = None
    