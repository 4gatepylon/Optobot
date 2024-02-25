from arm_lib import PA3400_ZeroTorque as PA3400

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
