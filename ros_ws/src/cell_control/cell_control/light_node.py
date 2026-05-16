import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from std_msgs.msg import Int32
from std_srvs.srv import Trigger


class stackLightNode(Node):
    def __init__(self):
        super().__init__("stack_light_node")

       
        self.stack_light_state = 0             # 0: operational, 2: paused because of door, 2: yellow, 3: because of emergency button
        self.door_closed = True                #door is closed
        self.emergency_pressed = False         #emergency button is not pressed

        self.door_subscriber = self.create_subscription(
            Bool,
            "/door_close",   #topic name
            self.door_callback,
            10,
        )

        self.e_button_subscriber = self.create_subscription(
            Bool,
            "/emergency_pressed",   #topic name
            self.e_button_callback,
            10,
        )

        self.publisher = self.create_publisher(
            Int32,
            "/stack_light_state",   #topic name
            10,
        )


        self.timer = self.create_timer(
            1.0,
            self.publish_stack_light_state,
        )

        self.get_logger().info("Stack light node started.")


    def door_callback(self, msg):
        self.door_closed = msg.data

    def e_button_callback(self, msg):
        self.emergency_pressed = msg.data       

    def publish_stack_light_state(self):
        
        message = Int32()
    
        if self.emergency_pressed : 
            self.stack_light_state = -1 #emergency button is pressed
        elif self.door_closed == False:
            self.stack_light_state = 1 #door is open
        else:
            self.stack_light_state = 0 #operational

        message.data = self.stack_light_state

        self.publisher.publish(message)

        if self.stack_light_state == -1:
            state_text = "emergency"
        elif self.stack_light_state == 1:
            state_text = "paused"
        else:
            state_text = "operational"

        self.get_logger().info(
            f"Stack-light state: {self.stack_light_state} ({state_text})"
        )









def main(args=None):
    rclpy.init(args=args)

    node = stackLightNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()