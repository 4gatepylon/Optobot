from dynio import *

from arm_lib import PA3400, Gripper

# TODO is this being used?
def init_dynamixel():
    dxl_io = dxl.DynamixelIO('/dev/ttyUSB0', baud_rate=115200)
    return dxl_io.new_mx28(1, 2)


if __name__ == "__main__":
    precise_address = {'host': '10.10.10.40', 'port': 10100}
    robot = PA3400(precise_address['host'], precise_address['port'])
    gripper = Gripper()

    robot.connect()
    robot.enable()
    robot.set_linear_motion()

    # Uncomment the following lines to test the pick and place function
    # Add positions using the get_positions.py script
    # The get position script allows you to move the robot arm and get coordinates accordingly
    
    # pick_position = [0, 0, 0, 0, 0, 0]
    # place_position = #insert here
    # intermediate_position = #insert here
    # home_position = #insert here

    # robot.pick_and_place(pick_position, place_position, intermediate_position, gripper)

    robot.disable()
    robot.disconnect()
