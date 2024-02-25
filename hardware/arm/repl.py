from __future__ import annotations

import json

from arm_lib import PA3400, Gripper, DEFAULT_HOST, DEFAULT_PORT
import time

def parse_command(self, _cmd: str) -> tuple[str, list[str]]:
    _cmd = _cmd.strip()
    keyword, cmd = _cmd.split(" ", 1)
    cmd = cmd.strip()
    cmd = cmd.split(" ")
    cmd = [x.strip() for x in cmd]
    cmd = [x for x in cmd if x != ""]
    return keyword, cmd

def run_command(command: str, args: list[str], robot: PA3400, gripper: Gripper) -> str:
    response = "Command format invalid"
    if command == "m":
        print("(NOTE these will have to be 6 coordinates or this will be ignored)")
        if len(args) == 6:
            robot.move_cartesian_position(args)
            loc = robot.query_cartesian_position()
            response = f"Moved to position {str(args)}, ended up at {loc}"
    elif command == "v":
        print("(NOTE ignore all non-0 index values for speed)")
        robot.maxSpeed = args[0]
        response = f"Set max speed to {args[0]}"
    elif command == "g":
        print("(NOTE ignore all non-0 index values for grip)")
        gripper.grip_by_amount(args[0])
        response = f"Gripped by {args[0]}"
    elif command == "o":
        gripper.open_gripper()
        response = "Opened gripper"
    elif command == "c":
        gripper.close_gripper()
        response = "Closed gripper"
    return response

def main():
    """This REPL is basically a meant to be used in a loop where 
    users provide simple commands to the arm that let it go at certain speeds.

    The following comands are supported:
    
    Movement and gripping commands:
      (t is secret command for repeating last command, use pp to repeat 2nd to last, ppp for 3rd to last, etc...)
      m [int ]{6} = move 
      v [int]     = set max speed/speed
      w           = wherec
      j           = wherej
      r           = start recording
      s           = stop recording    
      p           = play recording
      g           = grip by amount
      o           = open gripper
      c           = close gripper
      (might support sh and h for set home and go to home)
      (hi is secret command for printing history of commands and responses)
      (hr is the secret command for printing the current recording)        
    
    All commands can be joined with "&&" to run in sequence

    """
    # Initialize hardware
    preciseBoiAddress = {'host':DEFAULT_HOST,'port':DEFAULT_PORT}
    robot = PA3400(preciseBoiAddress)
    robot.connect()
    robot.enable()
    robot.set_linear_motion()
    gripper = Gripper()

    curr_loc = robot.query_cartesian_position()
    current_position = curr_loc

    gripper.open_gripper()
    current_grip = gripper.default_open_grip

    # Current recording has to be in the format if {'input': ..., "output": ...}
    # same for command history
    current_recording = []
    command_history = []
    curr_command = None
    is_recording = False
    while curr_command != "exit":
        curr_command = input("Enter a command: ")
        curr_command = curr_command.lower()
        # Enable repetitions
        # set("rrr") = {"r"} (go back thrice)
        # These aint logged!
        if curr_command == "exit":
            break
        elif curr_command == "r":
            is_recording = True
            current_recording = []
        elif curr_command == "s":
            # Keep it so you can print it
            is_recording = False
        elif curr_command == "hi":
            print("\t\n".join(json.dumps(x, indent=4) for x in command_history))
        elif curr_command == "hp":
            print("\t\n".join(json.dumps(x, indent=4) for x in current_recording))
        elif set(curr_command) == "t" and len(curr_command) <= len(command_history):
            end_idx = len(command_history) - len(curr_command)
            curr_command = command_history[end_idx]
        elif set(curr_command) == "t" and len(curr_command) > len(command_history):
            resp = "Invalid repetition (command stack does not go back that long)"
            print(resp)
            continue
        elif curr_command == "w":
            print(robot.query_cartesian_position())
        elif curr_command == "j":
            print(robot.query_joint_position())
        elif curr_command == "p":
            # Shitty not tested
            for c in current_recording:
                inp = c['input']
                out = c['output']
                cmd_keyword, args = parse_command(inp)
                print("Running: ", json.dumps(c, indent=4))
                resp = run_command(cmd_keyword, args, robot, gripper)
                print(json.dumps({
                    "previous_out": out,
                    "curr_out": resp
                }, indent=4))
                
        elif curr_command in ["m", "v", "g", "o", "c"]:
            # These get  recorded!
            # Add to history and run this command
            command, args = parse_command(curr_command)
            args = [float(x) for x in args] # NOTE these are ALWAYS floats

            response = run_command(command, args)

            print("Response: ", response)
            command_history.append({
                    'input': curr_command,
                    'output': response,
                })
            if is_recording:
                current_recording.append({
                    'input': curr_command,
                    'output': response,
                })
            command_history.append(curr_command)
        else:
            print("Invalid command, read the docs")
    
    # Teardown
    robot.disable()
    robot.disconnect()
    print("Exiting loop and exiting program!")
        

if __name__ == "__main__":
    main()