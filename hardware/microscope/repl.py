from __future__ import annotations

import os
import requests 
from typing import Optional, Union
from web_example import PyuscopeHTTPClient
from enum import Enum
from datetime import datetime
from pathlib import Path

from microscope_moves import image_pos

# TODO(Adriano) add support for move relative vs. move absolute
# TODO(Adriano) add support for imaging with a filename
# TODO(Adriano) support back key
class CommandType(Enum):
    MOVE_REL = "move_rel"
    MOVE_ABS = "move_abs"
    IMAGE = "image"
    IMAGE_SEQ = "image_seq"
    INFO = "info"

class Command:
    def __init__(self, ctype: CommandType, arguments: list[Union[str, float]]):
        assert isinstance(ctype, CommandType)
        self.ctype = ctype
        self.arguments = arguments
    
    def format(self) -> str:
        assert self.ctype in [CommandType.MOVE_REL, CommandType.MOVE_ABS, CommandType.IMAGE, CommandType.IMAGE_SEQ, CommandType.INFO]
        assert(len(self.arguments) % 2 == 0 or len(self.arguments) == 3) if self.ctype in [CommandType.MOVE_ABS, CommandType.MOVE_REL, CommandType.IMAGE_SEQ] else len(self.arguments) in [0, 1]
        # all these three need the location
        if self.ctype == CommandType.MOVE_REL or self.ctype == CommandType.MOVE_ABS or self.ctype == CommandType.IMAGE_SEQ:
            d = {}
            if len(self.arguments) == 3:
                d["x"] = float(self.arguments[0])
                d["y"] = float(self.arguments[1])
                d["z"] = float(self.arguments[2])
            else:
                for i in range(0, len(self.arguments), 2):
                    d[self.arguments[i]] = float(self.arguments[i+1])
            print("EXTRACTED MOVE: ", d) # Debug!
            return d
        # this just needs maybe the image name optionally
        elif self.ctype == CommandType.IMAGE:
            return self.arguments[0] if len(self.arguments) == 1 else None
        elif self.ctype == CommandType.INFO:
            assert len(self.arguments) == 0
            return None
        else:
            raise ValueError(f"Invalid command type {self.ctype.value}")

def generate_image_name() -> str:
    return f"scope_image_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"

# Valid keyword if starts with move and then has x | y | z and then has a number
def valid_keyword(keyword: str) -> Optional[Command]:
    keywords = keyword.strip().split(" ")
    keywords = [x.strip() for x in keywords]
    keywords = [x for x in keywords if x != ""]
    if len(keywords) == 0:
        return None
    try:
        # Just some hotkeys... probably a cleaner way to do this in the future somewhere else!
        if keywords[0] == "m" or keywords[0] == "move":
            keywords[0] = "move_rel"
        if keywords[0] == "a":
            keywords[0] = "move_abs"
        if keywords[0] == "i":
            keywords[0] = "image"
        if keywords[0] == "is" or keywords[0] == "s":
            keywords[0] = "image_seq"
        if keywords[0] == "p" or keywords[0] == "pos" or keywords[0] == "position":
            keywords[0] = "info"
        return Command(CommandType(keywords[0]), arguments=keywords[1:])
    except:
        return None

def main():
    # To make sure you get these, run export $(cat .env) and make sure you have these environment variables there,
    # Ask adriano, Yusuf or one of the other Labsmore people
    assert "SCOPE_IP" in os.environ
    assert "SCOPE_PORT" in os.environ
    assert "SCOPE_IMAGE_FOLDER" in os.environ
    scope_folder = Path(os.environ["SCOPE_IMAGE_FOLDER"])
    assert not scope_folder.exists()
    scope_folder.mkdir(parents=True)
    print(f"Your images will be stored in {scope_folder.as_posix()}")
    # To understand how to use the microscope API visit
    # https://docs.google.com/document/d/1DeH7sRFJL5jzOhhswXLT6Msq-TXWYu_6sOhDkCAcsn0/edit#heading=h.ltc37h9sv735
    # ALSO reminder to self: you must be on LAN (no VPN AFAIK)
    client = PyuscopeHTTPClient(debug=True)
    exit_keyword = "exit"
    last_keyword = None
    keyword = None
    while keyword != exit_keyword:
        keyword = input("Enter a command: ")
        keywords = [x.strip() for x in keyword.split("&&")]
        for keyword in keywords:
            keyword = keyword.lower()
            # Enable repetitions
            if keyword== "r" and last_keyword is not None:
                keyword = last_keyword
            last_keyword = keyword
            # ...
            kw = valid_keyword(keyword)
            if kw is None:
                print("Invalid keyword")
                continue
            if kw.ctype == CommandType.MOVE_REL:
                print("was type move_rel!", kw.format()) # XXX
                client.move_relative(kw.format())
            elif kw.ctype == CommandType.MOVE_ABS:
                print("was type move_abs!", kw.format()) # XXX
                client.move_absolute(kw.format())
            elif kw.ctype == CommandType.IMAGE:
                print("was type image!", kw.format()) # XXX
                # NOTE that this is a PIL image
                im = client.image()
                im_name = kw.format()
                im_file = (scope_folder / im_name).as_posix()
                im.save(im_file)
            elif kw.ctype == CommandType.IMAGE_SEQ:
                fmt = kw.format()
                print("was type image_seq!", fmt)
                image_pos(fmt, client=client)
            elif kw.ctype == CommandType.INFO:
                curr_pos = client.get_position()
                print(f"Current position:")
                print("\tx: ", curr_pos["x"])
                print("\ty: ", curr_pos["y"])
                print("\tz: ", curr_pos["z"])
            else:
                # Should never be reached
                raise ValueError(f"Command was not a valid command! type of kw={type(kw)} type of kw ctype={type(kw.ctype)}")
    print("")
    print("Done!")

        
    

if __name__ == "__main__":
    main()