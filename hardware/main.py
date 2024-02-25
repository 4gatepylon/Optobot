from __future__ import annotations
import time

# Not clear if we should use arm_movement or sample_movement
from arm.arm_movement import PA3400, Gripper
from arm.sample_movement import DEFAULT_HOST as ARM_DEFAULT_HOST
from arm.sample_movement import DEFAULT_PORT as ARM_DEFAULT_PORT

from microscope.web_example import PyuscopeHTTPClient
from microscope.microscope_moves import image_pos, DEFAULT_SCOPE_IP, DEFAULT_SCOPE_PORT
# Image position is going to image the position requested FROM THE REFERENCE FRAME OF THE MICROSCOPE

ARM_INTERMEDIATE_IN_TO_SCOPE_POSITION = [0, 0, 0, 0, 0, 0] # TODO
ARM_SCOPE_POSITION = [0, 0, 0, 0, 0, 0] # TODO
ARM_INTERMEDIATE_SCOPE_TO_OUT_POSITION = [0, 0, 0, 0, 0, 0] # TODO
ARM_POSITIONS = {
    'home': [0, 0, 0, 0, 0, 0], # TODO
    # Two places to pickup for now: top and bottom shelf
    'pick-and-place-top-shelf-in-to-scope': [
        [0, 0, 0, 0, 0, 0], # LOCATION OF TOP SHELF (IN) TODO
        ARM_INTERMEDIATE_IN_TO_SCOPE_POSITION,
        ARM_SCOPE_POSITION,
    ],
    'pick-and-place-scope-to-bottom-shelf-out': [
        ARM_SCOPE_POSITION,
        ARM_INTERMEDIATE_SCOPE_TO_OUT_POSITION,
        [0, 0, 0, 0, 0, 0], # LOCATION OF BOTTOM SHELF (OUT) TODO
    ],
    'pick-and-and-place-bottom-shelf-in-to-scope': [
        [0, 0, 0, 0, 0, 0], # LOCATION OF BOTTOM SHELF (IN) TODO
        ARM_INTERMEDIATE_IN_TO_SCOPE_POSITION,
        ARM_SCOPE_POSITION,
    ],
    'pick-and-place-scope-to-top-shelf-out': [
        ARM_SCOPE_POSITION,
        ARM_INTERMEDIATE_SCOPE_TO_OUT_POSITION,
        [0, 0, 0, 0, 0, 0], # LOCATION OF TOP SHELF (OUT) TODO
    ],
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
    ('arm', 'pick-and-place-top-shelf-in-to-scope'),
    # Wait at home
    ('arm', 'home'),
    # Image position
    ('scope', 'image'), # NOTE that the "image" command both MOVES to the image location AND takes MULTIPLE IMAGES
    ('scope', 'home'),
    # Pickup and place in the output box sequence)
    ('arm', 'pick-and-place-scope-to-bottom-shelf-out'),
    # Home and repeat
    ('arm', 'home')
    ('arm', 'pick-and-and-place-bottom-shelf-in-to-scope'),
    # Wait at home (second time)
    ('arm', 'home')
    # Now image again
    ('scope', 'image'),
    ('scope', 'home'),
    # Now move it
    ('arm', 'pick-and-place-scope-to-top-shelf-out'),
    # Idle at home now
    ('arm', 'home')
    # Now we are done
]

def main():
    # Initialize arm!
    preciseBoiAddress = {'host':ARM_DEFAULT_HOST,'port':ARM_DEFAULT_PORT}
    robot = PA3400(preciseBoiAddress)
    gripper = Gripper()

    robot.connect()
    robot.enable()
    robot.set_linear_motion()

    robot.maxSpeed = 80

    # Initialize scope
    scope = PyuscopeHTTPClient(host=DEFAULT_SCOPE_IP, port=DEFAULT_SCOPE_PORT)

    # Just go home
    print("Going home!")
    robot.gohome()

    # NOTE that in each case the instruction is a POSITION and but it may implicitely imply doing certain more things!
    for actor_name, instruction in INSTR_SEQUENCE:
        if actor_name == 'arm':
            if instruction == 'movec':
                print(f"ARM MOVING TO: {' '.join(str(n) for n in ARM_POSITIONS[instruction])}")
                robot.movec(ARM_POSITIONS[instruction])
            elif 'pick-and-place' in instruction:
                posses = ARM_POSITIONS[instruction]
                assert isinstance(posses, list)
                assert len(posses) == 3
                assert all(isinstance(pos, list) for pos in posses)
                assert all(len(pos) == 6 for pos in posses)
                assert all(all(isinstance(n, (int, float)) for n in pos) for pos in posses)
                _ = '\t\n'.join(str(n) for n in ARM_POSITIONS[instruction])
                print(f"ARM MOVING AND THEN PLACING DOWN TO/AT and then going to:\n{_}\n")
                robot.pick_and_place(posses[0], posses[1], posses[2], gripper)
                robot.gohome() # For safety just in case
        elif actor_name == 'scope':
            if instruction == 'image':
                print("IMAGING!")
                image_pos(MICROSCOPE_POSITIONS[instruction], client=scope)
            elif instruction == 'home':
                print("SCOPE GOING HOME!")
                scope.move_absolute(MICROSCOPE_POSITIONS[instruction])
            else:
                raise ValueError("GOT WRONG INSTRUCTION FOR MICROSCOPE")
        else:
            raise ValueError(f"Unknown actor name: {actor_name}")
        
    print("Done!")
    print("Shutting down robot")
    robot.gohome()
    # time.sleep(8)
    time.sleep(20)

    robot.disable()
    robot.disconnect()
    print("No steps for the scope to shut down!")
    print("Done!")
    print("ALL done! (exiting)")

if __name__ == "__main__":
    main()
