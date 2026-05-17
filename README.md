# Bin Picking Cell Control

This project implements a simplified control system for a robotic bin picking cell.

The system includes:

- API communication between a Warehouse Management System (WMS) and a robotic cell
- ROS 2 nodes for barcode scanner, door state, emergency button, and stack-light
- A simple browser-based HMI to display the system state, request information, and response information

The implementation uses:

- Ubuntu 22.04
- ROS 2 Humble
- Python 3
- FastAPI
- Plain HTML/CSS/JavaScript

No real robot, camera, barcode scanner, or physical cell hardware is required. The robot picking process and hardware signals are simulated.

---

## 1. System Overview

The system simulates a robotic bin picking cell.

The Warehouse Management System sends a pick request to the robotic cell. The robotic cell checks whether the door is closed and whether the emergency button is pressed. If the system is safe, it reads the latest barcode from the barcode scanner node and returns a successful pick confirmation.

If the door is open or the emergency button is pressed, the pick request is rejected.

```text
HMI / Swagger
    |
    | Send pick request
    v
WMS API
    |
    | POST /pick
    v
Cell API
    |
    | Reads ROS 2 states:
    | - Door state
    | - Emergency button state
    | - Stack-light state
    |
    | Calls barcode service
    v
ROS 2 nodes
    |
    | Return barcode and safety states
    v
Cell API
    |
    | POST /confirmPick
    v
WMS API
```

---

## 2. Project Structure

```text
pick_cell_control/
├── api/
│   ├── api_cell.py
│   └── api_wms.py
│
├── hmi/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── ros_ws/
│   └── src/
│       └── cell_control/
│           ├── package.xml
│           ├── setup.py
│           └── cell_control/
│               ├── barcode_node.py
│               ├── door_node.py
│               ├── emergency_node.py
│               └── stack_light_node.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 3. Main Components

### 3.1 WMS API

File:

```text
api/api_wms.py
```

This simulates the Warehouse Management System.

Responsibilities:

- Sends pick requests to the Cell API
- Receives pick confirmations from the Cell API
- Stores the last request
- Stores the last confirmation

Endpoints:

```text
POST /sendPick
POST /confirmPick
GET  /lastRequest
GET  /lastConfirmation
```

Runs on:

```text
http://localhost:8081
```

Swagger:

```text
http://localhost:8081/docs
```

---

### 3.2 Cell API

File:

```text
api/api_cell.py
```

This simulates the robotic cell API.

Responsibilities:

- Receives pick requests from the WMS API
- Reads the latest door state from ROS 2
- Reads the latest emergency button state from ROS 2
- Reads the latest stack-light state from ROS 2
- Calls the barcode scanner ROS 2 service
- Decides whether the pick is successful
- Sends the confirmation back to the WMS API

Endpoints:

```text
POST /pick
GET  /state
```

Runs on:

```text
http://localhost:8080
```

Swagger:

```text
http://localhost:8080/docs
```

---

### 3.3 Barcode Scanner Node

File:

```text
ros_ws/src/cell_control/cell_control/barcode_node.py
```

This node simulates a barcode scanner.

It publishes a random 5-digit barcode every second.

ROS interface:

```text
Topic:   /barcode
Type:    std_msgs/msg/Int32

Service: /get_latest_barcode
Type:    std_srvs/srv/Trigger
```

The service returns the latest generated barcode.

---

### 3.4 Door Node

File:

```text
ros_ws/src/cell_control/cell_control/door_node.py
```

This node simulates the cell door.

ROS interface:

```text
Topic:   /door_closed
Type:    std_msgs/msg/Bool

Service: /toggle_door
Type:    std_srvs/srv/Trigger
```

Values:

```text
true  = door closed
false = door open
```

The `/toggle_door` service switches the door state between open and closed.

---

### 3.5 Emergency Button Node

File:

```text
ros_ws/src/cell_control/cell_control/emergency_node.py
```

This node simulates the emergency button.

ROS interface:

```text
Topic:    /emergency_pressed
Type:     std_msgs/msg/Bool

Service:  /press_emergency
Type:     std_srvs/srv/Trigger

Service:  /reset_emergency
Type:     std_srvs/srv/Trigger
```

Values:

```text
true  = emergency button pressed
false = emergency button not pressed
```

---

### 3.6 Stack-light Node

File:

```text
ros_ws/src/cell_control/cell_control/stack_light_node.py
```

This node simulates the stack-light.

It subscribes to the door and emergency topics and publishes the current stack-light state.

ROS interface:

```text
Subscribes: /door_closed
Type:       std_msgs/msg/Bool

Subscribes: /emergency_pressed
Type:       std_msgs/msg/Bool

Publishes:  /stack_light_state
Type:       std_msgs/msg/Int32
```

Stack-light values:

```text
0  = operational / green
1  = paused / yellow
-1 = emergency / red
```

Emergency has priority over door state.

---

### 3.7 HMI

Files:

```text
hmi/index.html
hmi/style.css
hmi/app.js
```

The HMI is a browser-based interface.

It displays:

- Pick request information
- Pick response information
- Door state
- Emergency button state
- Stack-light state
- Stack-light color

The HMI uses JavaScript `fetch()` calls to communicate with the APIs.

Runs on:

```text
http://localhost:3000
```

---

## 4. Requirements

Tested with:

```text
Ubuntu 22.04
ROS 2 Humble
Python 3.10
```

Python packages:

```text
fastapi
uvicorn
requests
```

ROS 2 packages:

```text
rclpy
std_msgs
std_srvs
```

Frontend:

```text
Plain HTML/CSS/JavaScript
```

---

## 5. Installation

### 5.1 Install ROS 2 Humble

Install ROS 2 Humble on Ubuntu 22.04.

After installation, verify that ROS 2 works:

```bash
ros2 --help
```

### 5.2 Open the project folder

```bash
cd ~/pick_cell_control
```

### 5.3 Create Python virtual environment

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

### 5.4 Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5.5 Build the ROS 2 workspace

```bash
cd ~/pick_cell_control/ros_ws
colcon build
source install/setup.bash
```

---

## 6. How to Run the Full System

The full system is started using separate terminals.

### Terminal 1: Barcode Node

```bash
cd ~/pick_cell_control/ros_ws
source install/setup.bash
ros2 run cell_control barcode_node
```

### Terminal 2: Door Node

```bash
cd ~/pick_cell_control/ros_ws
source install/setup.bash
ros2 run cell_control door_node
```

### Terminal 3: Emergency Button Node

```bash
cd ~/pick_cell_control/ros_ws
source install/setup.bash
ros2 run cell_control emergency_node
```

### Terminal 4: Stack-light Node

```bash
cd ~/pick_cell_control/ros_ws
source install/setup.bash
ros2 run cell_control stack_light_node
```

### Terminal 5: Cell API

```bash
cd ~/pick_cell_control
source /opt/ros/humble/setup.bash
source ros_ws/install/setup.bash
source venv/bin/activate
uvicorn api.api_cell:app --host 0.0.0.0 --port 8080
```

### Terminal 6: WMS API

```bash
cd ~/pick_cell_control
source venv/bin/activate
uvicorn api.api_wms:app --host 0.0.0.0 --port 8081
```

### Terminal 7: HMI

```bash
cd ~/pick_cell_control/hmi
python3 -m http.server 3000
```

Open the HMI in a browser:

```text
http://localhost:3000
```

---

## 7. API Usage

### 7.1 Send Pick Request

Use the WMS API:

```text
POST http://localhost:8081/sendPick
```

Example request:

```json
{
  "pickId": 101,
  "quantity": 2
}
```

Example successful response:

```json
{
  "pickId": 101,
  "pickSuccessful": true,
  "errorMessage": null,
  "itemBarcode": 12345
}
```

The `itemBarcode` value comes from the ROS 2 barcode scanner node.

---

### 7.2 Cell API State

```text
GET http://localhost:8080/state
```

Example response:

```json
{
  "doorClosed": true,
  "emergencyPressed": false,
  "stackLight": 0
}
```

---

### 7.3 Last Request

```text
GET http://localhost:8081/lastRequest
```

---

### 7.4 Last Confirmation

```text
GET http://localhost:8081/lastConfirmation
```

---

## 8. ROS 2 Testing Commands

### Check all topics

```bash
ros2 topic list
```

Expected topics include:

```text
/barcode
/door_closed
/emergency_pressed
/stack_light_state
```

### Check all services

```bash
ros2 service list
```

Expected services include:

```text
/get_latest_barcode
/toggle_door
/press_emergency
/reset_emergency
```

### Echo barcode

```bash
ros2 topic echo /barcode
```

### Get latest barcode

```bash
ros2 service call /get_latest_barcode std_srvs/srv/Trigger
```

### Echo door state

```bash
ros2 topic echo /door_closed
```

### Toggle door

```bash
ros2 service call /toggle_door std_srvs/srv/Trigger
```

### Echo emergency state

```bash
ros2 topic echo /emergency_pressed
```

### Press emergency

```bash
ros2 service call /press_emergency std_srvs/srv/Trigger
```

### Reset emergency

```bash
ros2 service call /reset_emergency std_srvs/srv/Trigger
```

### Echo stack-light state

```bash
ros2 topic echo /stack_light_state
```

---

## 9. Demo Scenario

### 9.1 Normal Picking

Initial state:

```text
Door closed
Emergency not pressed
Stack-light = 0 / green
```

Send request from the HMI or Swagger:

```json
{
  "pickId": 101,
  "quantity": 2
}
```

Expected response:

```json
{
  "pickId": 101,
  "pickSuccessful": true,
  "errorMessage": null,
  "itemBarcode": 12345
}
```

The barcode value will be different because it is randomly generated by the barcode node.

---

### 9.2 Door Open

Call:

```bash
ros2 service call /toggle_door std_srvs/srv/Trigger
```

Expected state:

```text
Door open
Stack-light = 1 / yellow
```

Send another pick request.

Expected response:

```json
{
  "pickSuccessful": false,
  "errorMessage": "Door is open. Robot movement is not allowed.",
  "itemBarcode": null
}
```

---

### 9.3 Emergency Pressed

Call:

```bash
ros2 service call /press_emergency std_srvs/srv/Trigger
```

Expected state:

```text
Emergency pressed
Stack-light = -1 / red
```

Send another pick request.

Expected response:

```json
{
  "pickSuccessful": false,
  "errorMessage": "Emergency button is pressed. Robot movement is not allowed.",
  "itemBarcode": null
}
```

Reset emergency:

```bash
ros2 service call /reset_emergency std_srvs/srv/Trigger
```

---

## 10. Design Decisions and Assumptions

### ROS 2 Humble

ROS 2 Humble was used because it is the recommended ROS 2 version for Ubuntu 22.04.

### API Framework

FastAPI was used because it provides a simple way to create HTTP endpoints and automatically creates Swagger documentation.

### HMI

The HMI was implemented with plain HTML, CSS, and JavaScript. No external frontend framework was used.

### Barcode Scanner

The barcode scanner is simulated by generating a random 5-digit number every second.

### Door

The door is simulated with a boolean state.

```text
true  = door closed
false = door open
```

The state can be changed using the `/toggle_door` ROS 2 service.

### Emergency Button

The emergency button is simulated with a boolean state.

```text
true  = emergency button pressed
false = emergency button not pressed
```

The state can be changed using the `/press_emergency` and `/reset_emergency` ROS 2 services.

### Stack-light

The stack-light is calculated based on the door and emergency states.

```text
0  = operational / green
1  = paused / yellow
-1 = emergency / red
```

Emergency has priority over the door state.

### HMI Control Buttons

The HMI only displays the required system information and sends pick requests. It does not include door or emergency control buttons because this was not explicitly required. Door and emergency state changes are demonstrated using ROS 2 service calls.

---

## 11. Docker

Docker support is not included in the current version.

The project was developed and tested directly on Ubuntu 22.04 with ROS 2 Humble.

Docker can be added later as an optional improvement.

---

## 12. Notes

- The robot picking process is simulated.
- No real robot hardware is used.
- No real barcode scanner is used.
- The barcode is randomly generated.
- The HMI updates the displayed state repeatedly by polling the APIs.
- The project should be run on Ubuntu 22.04 with ROS 2 Humble.
