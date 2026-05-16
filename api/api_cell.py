from threading import Thread, Lock
import time

from fastapi import FastAPI
from pydantic import BaseModel
import requests

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int32
from std_srvs.srv import Trigger


app = FastAPI(title="Robotic Cell API")


class PickRequest(BaseModel):
    pickId: int
    quantity: int


class PickConfirmation(BaseModel):
    pickId: int
    pickSuccessful: bool
    errorMessage: str | None
    itemBarcode: int | None


class RosStateBridge(Node):
    def __init__(self):
        super().__init__("api_ros_state_bridge")

        self.lock = Lock()

        self.door_closed = True
        self.emergency_pressed = False
        self.stack_light_state = 0

        self.create_subscription(
            Bool,
            "/door_close",
            self.door_callback,
            10,
        )

        self.create_subscription(
            Bool,
            "/emergency_pressed",
            self.emergency_callback,
            10,
        )

        self.create_subscription(
            Int32,
            "/stack_light_state",
            self.stack_light_callback,
            10,
        )

        self.barcode_client = self.create_client(
            Trigger,
            "/get_latest_barcode",
        )

        self.get_logger().info("API ROS state bridge started.")

    def door_callback(self, msg):
        with self.lock:
            self.door_closed = msg.data

    def emergency_callback(self, msg):
        with self.lock:
            self.emergency_pressed = msg.data

    def stack_light_callback(self, msg):
        with self.lock:
            self.stack_light_state = msg.data

    def get_current_state(self):
        with self.lock:
            return {
                "doorClosed": self.door_closed,
                "emergencyPressed": self.emergency_pressed,
                "stackLight": self.stack_light_state,
            }

    def get_latest_barcode(self, timeout_seconds=3.0):
        """
        if not self.barcode_client.wait_for_service(timeout_sec=timeout_seconds):
            return None
            """

        request = Trigger.Request()
        future = self.barcode_client.call_async(request)

        start_time = time.time()

        while not future.done():
            if time.time() - start_time > timeout_seconds:
                return None
            time.sleep(0.05)

        response = future.result()

        if response is None or not response.success:
            return None

        try:
            return int(response.message)
        except ValueError:
            return None


ros_bridge = None
ros_thread = None


@app.on_event("startup")
def startup_event():
    global ros_bridge
    global ros_thread

    if not rclpy.ok():
        rclpy.init()

    ros_bridge = RosStateBridge()

    ros_thread = Thread(
        target=rclpy.spin,
        args=(ros_bridge,),
        daemon=True,
    )
    ros_thread.start()


@app.on_event("shutdown")
def shutdown_event():
    global ros_bridge

    if ros_bridge is not None:
        ros_bridge.destroy_node()

    if rclpy.ok():
        rclpy.shutdown()


@app.post("/pick")
def receive_pick_request(request: PickRequest):
    print("Received pick request:")
    print(request)

    state = ros_bridge.get_current_state()

    door_closed = state["doorClosed"]
    emergency_pressed = state["emergencyPressed"]

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

        latest_barcode = ros_bridge.get_latest_barcode()

        if latest_barcode is None:
            confirmation = PickConfirmation(
                pickId=request.pickId,
                pickSuccessful=False,
                errorMessage="Could not read latest barcode from ROS2 scanner.",
                itemBarcode=None,
            )
        else:
            confirmation = PickConfirmation(
                pickId=request.pickId,
                pickSuccessful=True,
                errorMessage=None,
                itemBarcode=latest_barcode,
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
    return ros_bridge.get_current_state()