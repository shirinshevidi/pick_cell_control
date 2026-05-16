import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from std_srvs.srv import Trigger


class eButtonNode(Node):
    def __init__(self):
        super().__init__("emergency_button_node")

        self.e_button_state = False # True means button is pressed, false means button is not pressed

        self.publisher = self.create_publisher(
            Bool,
            "/emergency_pressed",   #topic name
            10,
        )

        self.press_service = self.create_service(
            Trigger,
            "/press_emergency",   #service name
            self.press_emergency_callback,
        )

        self.reset_service = self.create_service(
            Trigger,
            "/reset_emergency",   #service name
            self.reset_emergency_callback,
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_emergency_pressed,
        )

        self.get_logger().info("Emergency button node started.")


    def publish_emergency_pressed(self):
        
        message = Bool()
        message.data = self.e_button_state

        self.publisher.publish(message)

        self.get_logger().info(
            f"emergenc button pressed status: {self.e_button_state}"
        )

    def press_emergency_callback(self, request, response):
        self.e_button_state = True
        response.message = "Emergency button pressed."
        self.get_logger().info(
            "Emergency button pressed."
        )
        response.success = True
        return response

    def reset_emergency_callback(self, request, response):
        self.e_button_state = False
        response.message = "Emergency button released."
        self.get_logger().info(
            "Emergency button released."
        )
        response.success = True
        return response


def main(args=None):
    rclpy.init(args=args)

    node = eButtonNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()