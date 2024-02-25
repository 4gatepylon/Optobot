# Not clear what main does (TODO(Adriano))
from arm.sample_movement import main
# Image position is going to image the position requested FROM THE REFERENCE FRAME OF THE MICROSCOPE
from microscope.microscope_moves import image_pos, go_to_pos

ARM_POSITIONS = {
    'home': [0, 0, 0, 0, 0, 0], # TODO
    # Two places to pickup for now: top and bottom shelf
    'pickup-in-top-shelf': [0, 0, 0, 0, 0, 0], # TODO
    'pickup-in-bottom-shelf': [0, 0, 0, 0, 0, 0], # TODO
    # You place for the scope and pickup for the scope in a fixed position
    'place-for-scope': [0, 0, 0, 0, 0, 0], # TODO
    'pickup-from-scope': [0, 0, 0, 0, 0, 0], # TODO
    # Two places to place for now: top and bottom shelf (on the seperate shelf)
    'place-out-bottom-shelf': [0, 0, 0, 0, 0, 0], # TODO
    'place-out-top-shelf': [0, 0, 0, 0, 0, 0], # TODO
}

MICROSCOPE_POSITIONS = {
    'home': {'x': None, 'y': None, 'z': None}, # TODO)
    'image': {'x': None, 'y': None, 'z': None}, # TODO
}

# TODO(Adriano) deal with image names
INSTR_SEQUENCE: tuple[str, str] = [
    # Start at home
    ('arm', 'home'),
    ('scope', 'home'),
    # Pickup and place sequence
    ('arm', 'pickup-in-top-shelf'),
    ('arm', 'home'),
    ('arm', 'place-for-scope'),
    # Wait at home
    ('arm', 'home'),
    # Image position
    ('scope', 'image'), # NOTE that the "image" command both MOVES to the image location AND takes MULTIPLE IMAGES
    ('scope', 'home'),
    # Pickup and place in the output box sequence)
    ('arm', 'pickup-from-scope')
    ('arm', 'home')
    ('arm', 'place-out-bottom-shelf'),
    # Home and repeat
    ('arm', 'home')
    ('arm', 'pickup-in-bottom-shelf')
    ('arm', 'home')
    ('arm', 'place-for-scope'),
    # Wait at home (second time)
    ('arm', 'home')
    # Now image again
    ('scope', 'image'),
    ('scope', 'home'),
    # Now move it
    ('arm', 'pickup-from-scope')
    ('arm', 'home')
    ('arm', 'place-out-top-shelf'),
    # Idle at home now
    ('arm', 'home')
    # Now we are done
]

def main():
    # NOTE that in each case the instruction is a POSITION and but it may implicitely imply doing certain more things!
    for actor_name, instruction in INSTR_SEQUENCE:
        if actor_name == 'arm':
            raise NotImplementedError # It's not main XXX
        elif actor_name == 'scope':
            if instruction == 'image':
                image_pos(MICROSCOPE_POSITIONS[instruction])
                print("Imaging!")
            elif instruction == 'home':
                go_to_pos(MICROSCOPE_POSITIONS[instruction])
                print("Microscope going home!")
            else:
                raise ValueError("GOT WRONG INSTRUCTION FOR MICROSCOPE")
        else:
            raise ValueError(f"Unknown actor name: {actor_name}")
    print("Done!")
if __name__ == "__main__":
    main()
