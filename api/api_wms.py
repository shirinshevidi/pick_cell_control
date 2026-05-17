from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests


app = FastAPI(title="Warehouse Management System API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],        
    allow_headers=["*"],
)


class PickRequest(BaseModel):
    pickId: int
    quantity: int


class PickConfirmation(BaseModel):
    pickId: int
    pickSuccessful: bool
    errorMessage: str | None
    itemBarcode: int | None


last_request = None
last_confirmation = None


@app.post("/sendPick")
def send_pick_request(request: PickRequest):
    global last_request

    last_request = request.model_dump()

    print("Sending pick request to robotic cell:")
    print(last_request)

    response = requests.post(
        "http://localhost:8080/pick",
        json=last_request,
        timeout=20,
    )

    return response.json()


@app.post("/confirmPick")
def confirm_pick(confirmation: PickConfirmation):
    global last_confirmation

    last_confirmation = confirmation.model_dump()

    print("Received confirmation from robotic cell:")
    print(last_confirmation)

    return {
        "message": "Confirmation received by WMS.",
        "confirmation": last_confirmation,
    }


@app.get("/lastRequest")
def get_last_request():
    return last_request


@app.get("/lastConfirmation")
def get_last_confirmation():
    return last_confirmation