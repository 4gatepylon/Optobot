from __future__ import annotations

def parse_command(self, _cmd: str) -> tuple[str, list[str]]:
    _cmd = _cmd.strip()
    keyword, cmd = _cmd.split(" ", 1)
    cmd = cmd.strip()
    cmd = cmd.split(" ")
    cmd = [x.strip() for x in cmd]
    cmd = [x for x in cmd if x != ""]
    return keyword, cmd

def execute_cmd(cmd: str, robot: PA3400, ) -> str:
    keyword, args = parse_command(cmd)
    if keyword == "m":
        move(args)
    elif keyword == "l":
        set_linear()


def play_recording(recording):
    raise NotImplementedError

def main():
    """This REPL is basically a meant to be used in a loop where 
    users provide simple commands to the arm that let it go at certain speeds.

    The following comands are supported:
    
    Movement and gripping commands:
      m [int ]{6} = move 
      l           = set linear
      v           = set max speed/speed
      w           = wherec
      j           = wherej
      r           = start recording
      s           = stop recording            
    
    All commands can be joined with "&&" to run in sequence

    """
    # Current recording has to be in the format if {'input': ..., "output": ...}
    current_recording = []
    command_history = []
    curr_command = None
    exit_keyword = "exit"
    while curr_command != exit_keyword:
        curr_command = input("Enter a command: ")
        curr_command = curr_command.lower()
        # Enable repetitions
        # set("rrr") = {"r"} (go back thrice)
        if curr_command == "again":
            curr_command = "r"
        if set(curr_command) == "r" and len(curr_command) <= len(command_history):
            end_idx = len(command_history) - len(curr_command)
            curr_command = command_history[end_idx]
        elif set(curr_command) == "r" and len(curr_command) > len(command_history):
            print("Invalid repetition (command stack does not go back that long)")
            continue
        
        # Add to history and run this command
        response = execute_cmd(curr_command)
        print("Response: ", response)
        command_history.append(curr_command)
    print("Exiting loop and exiting program!")
        

if __name__ == "__main__":
    main()