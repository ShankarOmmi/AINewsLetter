from pydantic import BaseModel, EmailStr

class SubscribeRequest(BaseModel):
    email : EmailStr
