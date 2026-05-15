import random

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32
from std_srvs.srv import Trigger


class BarcodeScannerNode(Node):
    def __init__(self):
        super().__init__("barcode_scanner_node")

        self.latest_barcode = 0

        self.publisher = self.create_publisher(
            Int32,
            "/barcode",
            10,
        )

        self.service = self.create_service(
            Trigger,
            "/get_latest_barcode",
            self.get_latest_barcode_callback,
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_barcode,
        )

        self.get_logger().info("Barcode scanner node started.")


    def publish_barcode(self):
        
        self.latest_barcode = random.randint(10000, 99999)

        message = Int32()
        message.data = self.latest_barcode

        self.publisher.publish(message)

        self.get_logger().info(
            f"Published barcode: {self.latest_barcode}"
        )

    def get_latest_barcode_callback(self, request, response):
        response.success = True
        response.message = str(self.latest_barcode)

        self.get_logger().info(
            f"Service requested. Returning latest barcode: {self.latest_barcode}"
        )

        return response


def main(args=None):
    rclpy.init(args=args)

    node = BarcodeScannerNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()