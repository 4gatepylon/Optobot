from __future__ import annotations

def execute_keyword(keyword: str):
    print("dummy! execute here later")
    pass

class Repl:
    """This REPL is basically a meant to be used in a loop where 
    users provide simple commands to the arm that let it go at certain speeds.

    The following comands are supported:
    
    Movement and gripping commands:
      movec | move | m [int ]{6} (speed [float])?
      movec | move | m undo
      undo | u
        alias of movec undo (just goto previous position)
        (do uuuuu.... to undo multiple times)
        TODO(Adriano) support move more or less with the ARM as well like for the gripper
      grip [float]
      ungrip | release [float]?
        (if float is provided, same as  grip, otherwise release to previous gripping state)
      less | ls
        (repeat GRIP DELTA but with less grip amount)
      more | mr
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
        (NOTE (TODO) two-way not supported rigth now)
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
    
    All commands can be joined with "&&" to run in sequence

    """
    def __init__(self):
        pass
    def init(self):
        pass
    def execute_keyword(self, keyword: str):
        return "OK"

def main():
    keyword_history = []
    curr_keyword = None
    exit_keyword = "exit"
    rep = Repl()
    rep.init()
    while curr_keyword != exit_keyword:
        curr_keyword = input("Enter a command: ")
        curr_keyword = curr_keyword.lower()
        # Enable repetitions
        # set("rrr") = {"r"} (go back thrice)
        if curr_keyword == "again":
            curr_keyword = "r"
        if set(curr_keyword) == "r" and len(curr_keyword) <= len(keyword_history):
            end_idx = len(keyword_history) - len(curr_keyword)
            curr_keyword = keyword_history[end_idx]
            # MAke sure to exclude that ending one
            keyword_history = keyword_history[:end_idx]
        elif set(curr_keyword) == "r" and len(curr_keyword) > len(keyword_history):
            print("Invalid repetition (command stack does not go back that long)")
            continue
        
        # Add to history and run this command
        response = rep.execute_keyword(curr_keyword)
        print("Response: ", response)
        keyword_history.append(curr_keyword)
    print("Exiting loop and exiting program!")
        

if __name__ == "__main__":
    main()