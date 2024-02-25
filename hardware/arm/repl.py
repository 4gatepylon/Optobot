from __future__ import annotations
from pathlib import Path
from typing import Optional, Union

from arm_lib import PA3400, Gripper, DEFAULT_HOST, DEFAULT_PORT
import time

class Repl:
    """This REPL is basically a meant to be used in a loop where 
    users provide simple commands to the arm that let it go at certain speeds.

    The following comands are supported:
    
    Movement and gripping commands:
      movec | move | m [int ]{6} (speed [float])?
      undo | u
        (undo move or grip)
      grip [float]
      ungrip | release [float]?
        (if float is provided, same as  grip, otherwise release to previous gripping state)
      less-grip | less | ls
        (repeat GRIP DELTA but with less grip amount)
      more-grip | more | mr
        (repeat GRIP DELTA but with more grip amount)
      
      wait | sleep [float]
    
    General purpose commands:
      cmd [str]
        (with quotes, will STRIP commmnd)

    Homes stack:
      push-home | set-home | sh
      pop-home | home | ph | h
      clear-home | ch
    
    Set Config:
      set-linear | linear | l
        (NOTE (Later Support) two-way not supported right now)
      set-max-speed | max-speed | ms [float]
      disable-zero-torque | dzt | ztq | zt | zq | z
        (meant for measuring the location of the joints)
      set-speed | speed | ss [float]

    
    Get Config:
      wherec | wc | w
      wherej | wj | j
      whereg | wg | g
        (NOTE this just tells you how much you are gripping)
    
    Repeat and command management:
      again | redo | repeat | r
        (use rrr to repeat 3 times, rrrr 4, etc...)
      history | hi
      clear-history | chi
      record | rec [str]?
      stop-record | stop-rec
        (NOTE this will save your recordings)
      set-recordings-folder | srf [str]
      play-recording | play-rec | play [str]?
        (NOTE that if you provide a string it will play the recording by that name
        and if you don't it should be the index and if you provide nothing it plays the
        latest recording excluding current recording - note that if you
        have a current recording you cannot play a recording)
    
    All commands can be joined with "&&" to run in sequence

    """
    def __init__(self, recording_folder: Path = Path("recordings"), host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.exit_keyword = "exit"
        
        # Command history XXX support history better!
        self.grips_queue = []
        self.locations_stack = []
        self.command_stack = []
        self.home_queue = []
        self.latest_move_or_grip_was_move = True

        # Recording management
        self.recording_folder = recording_folder
        self.recording = False
        self.playing_recording = False
        self.current_recording_inputs: str = []
        self.current_recording_outputs: str = []
        self.past_recordings: list[tuple[list[str], list[str]]] = []
        self.recordings_name2idx: dict[str, int] = {}
        
        # Actual objects
        self.max_speed = 10  # Default max speed
        self.open_default_status4gripper = 0.5  # Default open status for gripper
        self.linear_motion_enabled = False  # Placeholder for linear motion state
        self.current_location = None
        self.current_grip = None
        self.gripper = None
        self.robot = None
        self.current_position = None
        self.host = host
        self.port = port


    def init(self):
        preciseBoiAddress = {'host':DEFAULT_HOST,'port':DEFAULT_PORT}
        self.robot = PA3400(preciseBoiAddress)
        self.robot.connect()
        self.robot.enable()
        self.gripper = Gripper()

        curr_loc = self.robot.query_cartesian_position()
        self.current_position = curr_loc

        self.gripper.open_gripper()
        self.current_grip = self.gripper.default_open_grip
    
    def teardown(self):
        self.robot.disable()
        self.robot.disconnect()


    def parse_command(self, _cmd: str) -> tuple[str, list[str]]:
        _cmd = _cmd.strip()
        keyword, cmd = _cmd.split(" ", 1)
        cmd = cmd.strip()
        cmd = cmd.split(" ")
        cmd = [x.strip() for x in cmd]
        cmd = [x for x in cmd if x != ""]
        return keyword, cmd
    
    def play_recording(self, recording: Optional[Union[int, str]]) -> None:
        raise NotImplementedError

    def log(self, cmd: str, response: str) -> None:
        self.command_stack.append(cmd)
        if self.recordings:
            self.current_recording_inputs.append(cmd)
            self.current_recording_outputs.append(str(response))

    # NOTE the response is what will get logged
    def execute_command(self, cmd: str) -> str:
        assert self.current_location is not None
        assert self.gripper is not None
        assert self.current_position is not None

        cmd = cmd.lower()
        cmd = cmd.strip()

        if cmd == self.exit_keyword:
            return None

        # Enable repetitions
        # set("rrr") = {"r"} (go back thrice)
        if cmd in ["again", "redo", "repeat"]:
            cmd = "r"
        if set(cmd) == "r" and len(cmd) <= len(self.command_stack):
            end_idx = len(cmd) - len(cmd)
            cmd = self.command_stack[end_idx]
        elif set(cmd) == "r" and len(cmd) > len(self.command_stack):
            return "Invalid repetition (command stack does not go back that long)"
            
        # Parse and handle (action = keyword)
        action, arguments = self.parse_command(cmd)

        # Handle each action

        # SUPPORT MOVING
        if action in ["movec", "move", "m"]:
            loc = [float(arg) for arg in arguments[:6]]
            # TODO()
            assert len(loc) == 6
            self.locations_stack.append(self.current_position)
            self.robot.movec(loc)
            lloc = self.robot.query_cartesian_position()
            lloc = lloc.strip()
            lloc = lloc.split(" ")
            lloc = [x.strip() for x in lloc]
            lloc = [x for x in lloc if x != ""]
            lloc = [float(x) for x in lloc]
            self.current_location = lloc
            self.latest_move_or_grip_was_move = True
            self.log(cmd, str(lloc))
            return f"Moved to {loc}, ended up in {lloc}"
        # SUPPORT GRIPPING
        elif action in ["grip"] or action in ["ungrip", "release"]:
            assert len(arguments) == 0 or len(arguments) == 1
            if len(arguments) == 1:
                grip_strength = float(arguments[0].strip())
                self.gripper.grip(grip_strength)
                self.grips_queue.append(grip_strength)
                self.latest_move_or_grip_was_move = False
                return f"Gripped at {grip_strength}"
            else:
                if action == "grip":
                    self.gripper.grip()
                    self.grips_queue.append(self.gripper.default_close_grip)
                    self.latest_move_or_grip_was_move = False
                    return "Gripped"
                else:
                    self.gripper.ungrip()
                    self.grips_queue.append(self.gripper.default_open_grip)
                    self.latest_move_or_grip_was_move = False
                    return "Ungripped"
        # SUPPORT GRIPPING SAME AS BEFORE BUT WITH LESS OR MORE
        elif action in ["less-grip", "less", "ls"]:
            if len(self.grips_queue) == 0:
                return "No grip to reduce"
            
            # Example: less-grip
            # TODO: Implement less-grip functionality
            pass
        elif action in ["more-grip", "more", "mr"]:
            # Example: more-grip
            # TODO: Implement more-grip functionality
            pass
        elif action in ["wait", "sleep"]:
            # Example: wait 5 (waits for 5 seconds)
            time.sleep(float(params[0]))
            return "OK"
        elif action in ["cmd"]:
            # Example: cmd "custom command"
            # TODO: Implement cmd functionality
            pass
        elif action in ["push-home", "set-home", "sh"]:
            # Example: push-home
            self.home_queue.append(self.current_position)
            return "Home position set."
        elif action in ["pop-home", "home", "ph", "h"]:
            # Example: pop-home
            if self.home_queue:
                self.current_position = self.home_queue.pop()
                return "Moved to last home position."
            else:
                return "Home stack is empty."
        elif action in ["clear-home", "ch"]:
            # Example: clear-home
            self.home_queue.clear()
            return "Home stack cleared."
        # More command implementations can be added here...

        # Record the command if recording is active
        if self.recording:
            self.current_recording.append(cmd)
        
        return "Command executed."

        return "OK"

def main():
    rep = Repl()
    rep.init()
    response = ""
    while response is not None:
        cmd = input("Enter a command: ")
        response = rep.execute_keyword(cmd)
        print("Response: ", response)
    rep.teardown()
    print("Exiting loop and exiting program!")
        

if __name__ == "__main__":
    main()