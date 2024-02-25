#!/usr/bin/env python3
from __future__ import annotations

import os
import requests
import base64
from PIL import Image
import io
from typing import Optional

class PyuscopeHTTPClient:
    """A class to help you make basic moves of a microscope. This is copied (with only minor modifications) from
    https://github.com/Labsmore/pyuscope/blob/main/examples/web_example.py
    """
    def __init__(self, host: Optional[str]=None, port: Optional[int]=None, debug: bool = False):
        if host is None:
            if "SCOPE_IP" in os.environ:
                host = os.environ['SCOPE_IP']
            else:
                host = "localhost"
        self.host = host
        if port is None:
            if "SCOPE_PORT" in os.environ:
                port = int(os.environ['SCOPE_PORT'])
            else:
                port = 8080
        self.port = port
        assert self.port is not None
        assert self.host is not None
        self.base_url = f"http://{self.host}:{self.port}"

        # Adds logging
        self.debug = debug
        

    def request(self, page: str, query_args: dict[str, str]={}):
        query_str = ""
        if len(query_args):
            query_str = "?" + "&".join(f"{k}={v}"
                                       for k, v in query_args.items())
        response = requests.get(self.base_url + page + query_str)
        return response.json()

    def get_position(self):
        if self.debug:
            print("DEBUG: GETTING POSITION")
        ret = self.request("/get/position")
        pos = ret["data"]
        for k, v in pos.items():
            pos[k] = float(v)
        return pos

    def move_absolute(self, pos: dict[str, float], block=True):
        # Positions should be in the format {"x": float, "y": float, etc...}
        # though any of these keys could also be missing
        qargs = {"block": int(block)}
        for k, v in pos.items():
            qargs["axis." + k] = float(v)
        if self.debug:
            print(f"DEBUG: MOVE ABSOLUTE WITH {qargs}")
        # print("move_absolute", qargs)
        self.request("/run/move_absolute", qargs)

    def move_relative(self, pos: dict[str, float], block: bool=True):
        qargs = {"block": int(block)}
        for k, v in pos.items():
            qargs["axis." + k] = v
        if self.debug:
            print(f"DEBUG: MOVE RELATIVE WITH {qargs}")
        self.request("/run/move_relative", qargs)

    def image(self, wait_imaging_ok: bool=True, raw: bool=False):
        # NOTE that it is also possible to setup an RTSP (https://en.wikipedia.org/wiki/Real-Time_Streaming_Protocol)
        # server but you are going to have to ask the Labsmore guys
        if self.debug:
            print("DEBUG: IMAGE")
        response = self.request("/get/image", {
            "wait_imaging_ok": int(wait_imaging_ok),
            "raw": int(raw)
        })
        buf = base64.b64decode(response["data"]["base64"])
        return Image.open(io.BytesIO(buf))


def main():
    # Get the host and port if necessary
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate calibreation files from specially captured frames'
    )
    parser.add_argument("--host", default=None)
    parser.add_argument('--port', default=None)
    args = parser.parse_args()

    client = PyuscopeHTTPClient(host=args.host, port=args.port)

    # Iteratively run through an example movement sequence
    # Units in mm
    pos = client.get_position()
    print(f"Initial position: {pos}")
    delta = 2
    print("Moving right")
    pos["x"] += delta
    client.move_absolute(pos)
    pos = client.get_position()
    print(f"Middle position: {pos}")
    im = client.image()
    print(f"Got image w/ size {im.size}, mode: {im.mode}")
    im.save('out.jpg')
    print("Moving left")
    pos["x"] -= delta
    client.move_absolute(pos)
    pos = client.get_position()
    print(f"Final position: {pos}")


if __name__ == "__main__":
    # Run script with python3 web_example.py
    main()