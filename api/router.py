from fastapi import APIRouter, HTTPException
from api.schemas import SubscribeRequest
from db.models import add_subscriber, get_subscriber_by_email, unsubscribe

router = APIRouter()

@router.post("/subscribe")
def subscribe(data: SubscribeRequest):
    result = add_subscriber(data.email)

    if not result["success"]:
        # Handle duplicate gracefully
        if "UNIQUE constraint failed" in result["error"]:
            return {"message": "Email already subscribed"}

        raise HTTPException(status_code=400, detail=result["error"])

    return {"message": "Subscribed successfully"}

@router.get("/unsubscribe")
def unsubscribe_user(token:str):
    success = unsubscribe(token)

    if not success:
        raise HTTPException(status_code = 404, detail = "Invalid token")
    
    return {"message": "You have been unsubscribed"}
