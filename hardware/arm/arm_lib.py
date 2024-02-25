from __future__ import annotations

import socket
import time
import numpy
import re
from typing import Union

from dynio import *

class PA3400_ZeroTorque:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.sock.connect((self.address, self.port))
            print("Connected to robot")
        except socket.error as e:
            print(f"Connection error: {e}")

    def disconnect(self):
        self.sock.close()
        print("Disconnected from robot")

    def send_command(self, command):
        if self.sock:
            self.sock.sendall((command + '\n').encode())
            response = self.sock.recv(1024).decode().strip()
            print(f"Response: {response}")
            return response
        else:
            print("Not connected to robot")
            return None

    def disable_zero_torque(self):
        self.send_command("zeroTorque 1 15")

    def query_cartesian_position(self):
        return self.send_command("wherec")

    def query_joint_position(self):
        return self.send_command("wherej")

class PA3400:
    def __init__(self, address, port):
        self.host = address
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Current position
        self.curpos = []

        # Maximum speed
        self.rapid = 10

        # Home position joint angles
        # self.homej = [750, 0, 180, -180]
        # self.homej = [675, 0, 180, 0]
        self.homej = [0, 0, 0, 0, 0, 0]

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

    def __move(self, pos: list[Union[int, float]], command_suffix: str):
        assert command_suffix in ["j", "c", "a"]
        cmd = f"move{command_suffix} 1 " + ' '.join(str(n) for n in pos)
        self.sendcmd(cmd)

    def movec(self, pos, speed=10):
        # Move cartisian
        return self.__move(pos, "c")

    def movej(self, pos):
        # Move robot to specified joint positions
        # pos = [H, A1, A2, A3, A4]
        # movej <profile#> <height> <angle2> <angle3> <angle4>
        return self.__move(pos, "j")
    # Unclear what movea is for
    # def movea(self, pos1, pos2):
    #     # Move robot to specified cartesian position, computing all joint
    #     # inverse kinematics.
    #     # pos = [X, Y, Z, Y, P, R]
    #     #
    #     # movec <profile#> <X> <Y> <Z> <Yaw> <pitch> <roll> [<handedness>]
    #     return self.__move(pos, "a")

    def gohome(self, speed: int = 10):
        self.movec(self.homej, speed=speed)

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

    # Not clear if this works
    # def parsegc(self, line):
    #     # Attempt to convert gcode block to PA command
    #     #

    #     blocks = line.split()

    #     if not len(blocks):
    #         return None

    #     # cmd = blocks[0]
    #     #

    #     # Extract letter coordinates
    #     blockchars = ['G','M','F','X','Y','Z','I','J','K']
    #     blockvals = dict.fromkeys(blockchars, 0)

    #     for letter in blockvals:
    #         block = re.search('(?<!\((?:(?!\))[\s\S\r])*?)' + letter + '-?\d*\.?\d*', line.upper())
    #         if block:
    #             if letter in ['G', 'M']:
    #                 blockvals[letter] = int(block.group()[1:])
    #             else:
    #                 blockvals[letter] = float(block.group()[1:])

    #     xyz = [blockvals['X'], blockvals['Y'], blockvals['Z']]
    #     ijk = [blockvals['I'], blockvals['J'], blockvals['K']]
    #     ypr = [90, -180, 1] # HACK
    #     g = blockvals['G']

    #     # bail if it's not a G command
    #     if not re.search('(?<!\((?:(?!\))[\s\S\r])*?)' + 'G' + '-?\d*\.?\d*', line.upper()):
    #         return None

    #     if g is 0:
    #         self.maxSpeed = 100
    #         pos = xyz + ypr
    #         self.movec(pos)

    #     elif g is 1:
    #         self.maxSpeed = 10
    #         pos = xyz + ijk
    #         self.movec(pos)

    #     elif g is 2:
    #         self.maxSpeed = 10

    #         # Convert center point arc to 3 point arc
    #         end = numpy.array(tuple(xyz))
    #         cur = numpy.array(tuple(self.curpos[:3]))
    #         cen = cur + numpy.array(tuple(ijk))
    #         midchord = cur + ((end - cur ) / 2)
    #         midarc = cen + ((midchord - cen) * numpy.linalg.norm(cur - cen) / numpy.linalg.norm(midchord - cen))

    #         pos1 = midarc + ypr
    #         pos2 = xyz + ypr
    #         self.movea(pos1, pos2)


    #     elif g is 3:
    #         self.maxSpeed = 10
    #         end = numpy.array(tuple(xyz))
    #         cur = numpy.array(tuple(self.curpos[:3]))
    #         cen = cur + numpy.array(tuple(ijk))
    #         midchord = cur + ((end - cur ) / 2)
    #         midarc = cen + ((midchord - cen) * numpy.linalg.norm(cur - cen) / numpy.linalg.norm(midchord - cen))
    #         pos1 = midarc + ypr
    #         pos2 = xyz + ypr
    #         self.movea(pos1, pos2)

    #     else:
    #         return

    @property
    def maxSpeed(self):
        return self.rapid

    @maxSpeed.setter
    def maxSpeed(self, speed):
        self.sendcmd('mspeed ' + str(speed))
        self.rapid = speed

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
