import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from std_srvs.srv import Trigger


class DoorCheckNode(Node):
    def __init__(self):
        super().__init__("door_check_node")

        self.status_door = True # True means closed, False means open

        self.publisher = self.create_publisher(
            Bool,
            "/door_close",   #topic name
            10,
        )

        self.service = self.create_service(
            Trigger,
            "/toggle_door",   #service name
            self.toggle_door_close_callback,
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_door_close,
        )

        self.get_logger().info("Door check node started.")


    def publish_door_close(self):
        
        message = Bool()
        message.data = self.status_door

        self.publisher.publish(message)

        self.get_logger().info(
            f"Published door closed status: {self.status_door}"
        )

    def toggle_door_close_callback(self, request, response):
        self.status_door = not self.status_door
        if self.status_door: 
            response.message = "Door is now closed."
            self.get_logger().info(
                "Door is now closed."
            )
        else:
            response.message = "Door is now open."
            self.get_logger().info(
                "Door is now open."
            )
        response.success = True

        return response


def main(args=None):
    rclpy.init(args=args)

    node = DoorCheckNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()