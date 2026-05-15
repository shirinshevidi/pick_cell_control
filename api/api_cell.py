from fastapi import FastAPI
from pydantic import BaseModel
import requests
import random
import time


app = FastAPI(title="Robotic Cell API")


class PickRequest(BaseModel):
    pickId: int
    quantity: int


class PickConfirmation(BaseModel):
    pickId: int
    pickSuccessful: bool
    errorMessage: str | None
    itemBarcode: int | None


# Temporary fake states.
# Later these will come from ROS 2 nodes.
door_closed = True
emergency_pressed = False


@app.post("/pick")
def receive_pick_request(request: PickRequest):
    print("Received pick request:")
    print(request)

    if emergency_pressed:
        confirmation = PickConfirmation(
            pickId=request.pickId,
            pickSuccessful=False,
            errorMessage="Emergency button is pressed. Robot movement is not allowed.",
            itemBarcode=None,
        )

    elif not door_closed:
        confirmation = PickConfirmation(
            pickId=request.pickId,
            pickSuccessful=False,
            errorMessage="Door is open. Robot movement is not allowed.",
            itemBarcode=None,
        )

    else:
        print(f"Fake picking {request.quantity} item(s)...")
        time.sleep(1)

        fake_barcode = random.randint(10000, 99999)

        confirmation = PickConfirmation(
            pickId=request.pickId,
            pickSuccessful=True,
            errorMessage=None,
            itemBarcode=fake_barcode,
        )

    try:
        response = requests.post(
            "http://localhost:8081/confirmPick",
            json=confirmation.model_dump(),
            timeout=5,
        )
        print("Confirmation sent to WMS.")
        print(response.status_code)

    except requests.exceptions.RequestException as error:
        print("Could not send confirmation to WMS:")
        print(error)

    return confirmation


@app.get("/state")
def get_state():
    return {
        "doorClosed": door_closed,
        "emergencyPressed": emergency_pressed,
        "stackLight": get_stack_light_state(),
    }


@app.post("/toggleDoor")
def toggle_door():
    global door_closed
    door_closed = not door_closed

    return {
        "doorClosed": door_closed,
        "message": "Door is now closed." if door_closed else "Door is now open.",
    }


@app.post("/pressEmergency")
def press_emergency():
    global emergency_pressed
    emergency_pressed = True

    return {
        "emergencyPressed": emergency_pressed,
        "message": "Emergency button has been pressed.",
    }


@app.post("/resetEmergency")
def reset_emergency():
    global emergency_pressed
    emergency_pressed = False

    return {
        "emergencyPressed": emergency_pressed,
        "message": "Emergency button has been reset.",
    }


def get_stack_light_state():
    if emergency_pressed:
        return -1

    if not door_closed:
        return 1

    return 0