#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
from web_example import PyuscopeHTTPClient

DEFAULT_SCOPE_IP = "192.168.0.236"
DEFAULT_SCOPE_PORT = 8401

# Kind of a dumb wrapper, maybe just delete this?
def go_to_pos(pos: dict[str, float]):
    # Get the host and port if necessary
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate calibreation files from specially captured frames'
    )
    # NOTE this may be subject to change, ask Jose or Adriano
    parser.add_argument("--host", default=DEFAULT_SCOPE_IP)
    parser.add_argument('--port', default=str(DEFAULT_SCOPE_PORT))
    args = parser.parse_args()

    client = PyuscopeHTTPClient(host=args.host, port=args.port)

    client.move_absolute(pos)
    print(f"Moved to position: {pos}")

def image_pos(right_pos: dict[str, float]):
    # Get the host and port if necessary
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate calibreation files from specially captured frames'
    )
    # NOTE this may be subject to change, ask Jose or Adriano
    parser.add_argument("--host", default=DEFAULT_SCOPE_IP)
    parser.add_argument('--port', default=str(DEFAULT_SCOPE_PORT))
    args = parser.parse_args()

    client = PyuscopeHTTPClient(host=args.host, port=args.port)

    delta = 30

    pos = client.get_position()
    print(f"Initial position: {pos}")

    #Go to right position 
    client.move_absolute(right_pos)

    im = client.image()
    print(f"Got image w/ size {im.size}, mode: {im.mode}")
    filename = get_img_filename()
    im.save(filename)
    
    #Iterate down the 4 slides
    for i in range(3):
        right_pos["y"] += delta

        client.move_absolute(right_pos)
        print(f"Moved tp position: {right_pos}")
        im = client.image()
        print(f"Got image w/ size {im.size}, mode: {im.mode}")
        filename = get_img_filename()
        im.save(filename)

def get_img_filename():
    now = datetime.now()
    # Format the date and time as a string
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    # Construct the filename
    filename = f"microscope_img_{timestamp}.jpg"
    return filename

if __name__ == "__main__":
    # Run script with python3 web_example.py
    # main()
    posA = {'y': 44.49499999999998, 'z': -22.73, 'x': 51.78124999999998}
    image_pos(posA)

