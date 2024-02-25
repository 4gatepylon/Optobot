import socket
import time
import numpy
from dynio import *

def init_dynamixel():
    dxl_io = dxl.DynamixelIO('/dev/ttyUSB0', baud_rate=115200)
    return dxl_io.new_mx28(1, 2)

class PA3400:
    def __init__(self, address, port):
        self.host = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.curpos = []
        self.rapid = 10

    def connect(self):
        try:
            self.sock.connect((self.host, self.port))
            print('Connected to robot')
        except socket.error as msg:
            print('Socket Error: ', msg)

    def enable(self):
        self.sendcmd('mode 0')
        self.sendcmd('hp 1')
        time.sleep(4)
        self.sendcmd('attach 1')
        time.sleep(1)
        self.sendcmd('home')
        time.sleep(5)

    def disable(self):
        self.sendcmd('hp 0')

    def disconnect(self):
        self.sock.close()

    def set_linear_motion(self, speed=10):
        # Only allows linear motion
        self.sendcmd(f'Straight 1 1')
        self.sendcmd(f'Speed 1 {speed}')

    def movec(self, pos, speed=10):
        # Move cartisian
        cmd = 'movec 1 ' + ' '.join(str(n) for n in pos)
        self.sendcmd(cmd)

    def gohome(self):
        self.movec([0, 0, 0, 0, 0, 0], speed=10)

    def sendcmd(self, cmd):
        cmd += '\n'
        self.sock.send(cmd.encode())
        print('Send command: ' + cmd)
        ack = self.sock.recv(1024)
        print(ack.decode())

    def pick_from_position(self, pick_position, gripper, speed=5):
        # modify to be above the pick position
        # self.movec(, speed)
        time.sleep(1)
        self.movec(pick_position, speed)  # Move to pick position
        time.sleep(3)  # Wait for the robot to reach the pick position
        gripper.close_gripper()  # Close the gripper to pick the object

    def place_to_position(self, place_position, gripper, speed=5):
        # modify to be above the place position
        # self.movec(, speed)
        # time.sleep(1)
        self.movec(place_position, speed)  # Move to place position
        time.sleep(3)  # Wait for the robot to reach the place position
        gripper.open_gripper()  # Open the gripper to place the object

    def intermediate_position(self, intermediate_position, speed=5):
        self.movec(intermediate_position, speed)

    def pick_and_place(self, pick_position, place_position, intermediate_position, gripper):
        self.intermediate_position(intermediate_position)  # Move to an intermediate position
        self.pick_from_position(pick_position, gripper)  # Move to pick position and close the gripper
        self.intermediate_position(intermediate_position)  # Move back to intermediate position
        self.place_to_position(place_position, gripper)  # Move to place position and open the gripper
        self.intermediate_position(intermediate_position)  # Move back to intermediate position


class Gripper:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=115200, gripper_id=1):
        self.dxl_io = dxl.DynamixelIO(port, baud_rate=baud_rate)
        self.gripper_id = gripper_id

    def open_gripper(self):
        self.dxl_io.set_goal_position(self.gripper_id, 200)  # Open position
        time.sleep(1)  # Wait for the gripper to open

    def close_gripper(self):
        self.dxl_io.set_goal_position(self.gripper_id, 70)  # Closed position
        time.sleep(1)  # Wait for the gripper to close

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
