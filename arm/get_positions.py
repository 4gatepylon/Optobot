import socket
import time

class PA3400:
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

if __name__ == "__main__":
    robot = PA3400("10.10.10.40", 10100)
    robot.connect()

    robot.disable_zero_torque()  # Disable zero torque mode

    while True:
        command = input("Enter 'c' for Cartesian position, 'j' for joint position, or 'exit' to quit: ").strip().lower()
        if command == "exit":
            break
        elif command == "wherec":
            cartesian_position = robot.query_cartesian_position()
            print(f"Cartesian Position: {cartesian_position}")
        elif command == "wherej":
            joint_position = robot.query_joint_position()
            print(f"Joint Position: {joint_position}")
        else:
            print("Invalid command. Please enter 'c', 'j', or 'exit'.")

    robot.disconnect()
