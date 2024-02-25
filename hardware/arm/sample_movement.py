import socket
import time
import re
import numpy

# Demo

DEFAULT_HOST = "10.10.10.40"
DEFAULT_PORT = 10100

class PA3400:
    # Network interface with Precise Automation PF3400 SCARA arm
    # Requires "Tcp_cmd_server" to be running on arm to accept TCP connections
    # and accept Guidance Programming Language (GPL) commands

    def __init__(self, address):
        self.host = address['host']
        self.port = address['port']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Home position joint angles
#        self.homej = [750, 0, 180, -180]
        self.homej = [675, 0, 180, 0]
        self.curpos = []

        # Maximum speed limit %
        self.rapid = 20

    def connect(self):
        # Attempt to open TCP stream with robot
        try:
            self.sock.connect((self.host, self.port))
            print('Success')
        except socket.error as msg:
            print('Socket Error: ', msg)

    def enable(self):
        # Enable high power, attach robot 1 (local addr)
        self.sendcmd('mode 0')
        self.sendcmd('hp 1')
        time.sleep(4)
        self.sendcmd('attach 1')
        time.sleep(1)
        self.sendcmd('home')
        time.sleep(5)

    def disable(self):
        # Disable robot high power
        self.sendcmd('hp 0')

    def disconnect(self):
        # Close TCP stream with robot
        self.sock.close()

    def movej(self, pos):
        # Move robot to specified joint positions
        # pos = [H, A1, A2, A3, A4]
        # movej <profile#> <height> <angle2> <angle3> <angle4>
        cmd = 'movej 1 ' + ' '.join(str(n) for n in pos)
        self.sendcmd(cmd)

    def movec(self, pos):
        # Move robot to specified cartesian position, computing all joint
        # inverse kinematics.
        # pos = [X, Y, Z, Y, P, R]
        #
        # movec <profile#> <X> <Y> <Z> <Yaw> <pitch> <roll> [<handedness>]
        self.curpos = pos
        cmd = 'movec 1 ' + ' '.join(str(n) for n in pos)
        self.sendcmd(cmd)

    # TODO wtf is this?
    def movea(self, pos1, pos2):
        # Move robot to specified cartesian position, computing all joint
        # inverse kinematics.
        # pos = [X, Y, Z, Y, P, R]
        #
        # movec <profile#> <X> <Y> <Z> <Yaw> <pitch> <roll> [<handedness>]
        self.curpos = pos # Not sure w
        cmd = 'movea 1 ' + ' '.join(str(n) for n in pos1) + ' '.join(str(n) for n in pos2)
        self.sendcmd(cmd)

    def gohome(self):
        self.movej(self.homej)

    def sendcmd(self, cmd):
        # Attempt to send command on socket
        #
        # TODO add error handling
        cmd += '\n'
        self.sock.send(cmd.encode())
        print('Send command: ' + cmd)
        ack = self.sock.recv(1024)
        print(ack.decode())

    def parsegc(self, line):
        # Attempt to convert gcode block to PA command
        #

        blocks = line.split()

        if not len(blocks):
            return None

        # cmd = blocks[0]
        #

        # Extract letter coordinates
        blockchars = ['G','M','F','X','Y','Z','I','J','K']
        blockvals = dict.fromkeys(blockchars, 0)

        for letter in blockvals:
            block = re.search('(?<!\((?:(?!\))[\s\S\r])*?)' + letter + '-?\d*\.?\d*', line.upper())
            if block:
                if letter in ['G', 'M']:
                    blockvals[letter] = int(block.group()[1:])
                else:
                    blockvals[letter] = float(block.group()[1:])

        xyz = [blockvals['X'], blockvals['Y'], blockvals['Z']]
        ijk = [blockvals['I'], blockvals['J'], blockvals['K']]
        ypr = [90, -180, 1] # HACK
        g = blockvals['G']

        # bail if it's not a G command
        if not re.search('(?<!\((?:(?!\))[\s\S\r])*?)' + 'G' + '-?\d*\.?\d*', line.upper()):
            return None

        if g is 0:
            self.maxSpeed = 100
            pos = xyz + ypr
            self.movec(pos)

        elif g is 1:
            self.maxSpeed = 10
            pos = xyz + ijk
            self.movec(pos)

        elif g is 2:
            self.maxSpeed = 10

            # Convert center point arc to 3 point arc
            end = numpy.array(tuple(xyz))
            cur = numpy.array(tuple(self.curpos[:3]))
            cen = cur + numpy.array(tuple(ijk))
            midchord = cur + ((end - cur ) / 2)
            midarc = cen + ((midchord - cen) * numpy.linalg.norm(cur - cen) / numpy.linalg.norm(midchord - cen))

            pos1 = midarc + ypr
            pos2 = xyz + ypr
            self.movea(pos1, pos2)


        elif g is 3:
            self.maxSpeed = 10
            end = numpy.array(tuple(xyz))
            cur = numpy.array(tuple(self.curpos[:3]))
            cen = cur + numpy.array(tuple(ijk))
            midchord = cur + ((end - cur ) / 2)
            midarc = cen + ((midchord - cen) * numpy.linalg.norm(cur - cen) / numpy.linalg.norm(midchord - cen))
            pos1 = midarc + ypr
            pos2 = xyz + ypr
            self.movea(pos1, pos2)

        else:
            return

    @property
    def maxSpeed(self):
        return self.rapid

    @maxSpeed.setter
    def maxSpeed(self, speed):
        self.sendcmd('mspeed ' + str(speed))
        self.rapid = speed


def main():
    preciseBoiAddress = {'host':DEFAULT_HOST,'port':DEFAULT_PORT}

    robot = PA3400(preciseBoiAddress)

    robot.connect()
    robot.enable()

    robot.maxSpeed = 80

    robot.gohome()
    # time.sleep(8)

    #top of bottle 244 (Z)
    # bottom of bottle 164 (Z)
    # row 5 -411 (Y)
    # row 4 -333 (Y)
    # row 1 -155 (Y)
    # place on shelf -200 (X)
    # approach shelf -100 (X)

    pos = [-100, -155, 244, 179.99, 90, -180, 2]
    robot.movec(pos)
    # time.sleep(3)
    pos = [-200, -155, 244, 179.99, 90, -180, 2]
    robot.movec(pos)
    # time.sleep(2)
    pos = [-200, -155, 164, 179.99, 90, -180, 2]
    robot.movec(pos)
    # time.sleep(2)
    pos = [-200, -155, 244, 179.99, 90, -180, 2]
    robot.movec(pos)
    # time.sleep(2)
    pos = [-100, -155, 244, 179.99, 90, -180, 2]
    robot.movec(pos)
    # time.sleep(2)

    pos = [-100, -411, 244, 179.99, 90, -180, 2]
    robot.movec(pos)
    # time.sleep(2)
    pos = [-200, -411, 244, 179.99, 90, -180, 2]
    robot.movec(pos)
    # time.sleep(2)
    pos = [-200, -411, 164, 179.99, 90, -180, 2]
    robot.movec(pos)
    # time.sleep(2)
    pos = [-200, -411, 244, 179.99, 90, -180, 2]
    robot.movec(pos)
    # time.sleep(2)
    pos = [-100, -411, 244, 179.99, 90, -180, 2]
    robot.movec(pos)
    # time.sleep(2)

    # pos = [300, 0, 600, 120, 90, -180, 1]
    # robot.movec(pos)
    # time.sleep(30)
    # pos = [300, 0, 600, 120, 90, -180, 2]
    # robot.movec(pos)
    # time.sleep(30)
    #
    #
    #
    #
    # robot.gohome()
    # time.sleep(3)
    #
    # pos = [300, 0, 300, 90, 90, -180, 2]
    # robot.movec(pos)
    # time.sleep(3)

    robot.gohome()
    # time.sleep(8)
    time.sleep(20)

    robot.disable()
    robot.disconnect()

if __name__ == "__main__":
    main()