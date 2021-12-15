import subprocess
import socket
import struct
import can
import random

_FRAME_FORMAT = "=IB3xBBBBBBBB"
_FRAME_SIZE = struct.calcsize(_FRAME_FORMAT)
_RANDOM_MESSAGE = can.Message(arbitration_id=random.randint(0x0, 0x7ff),
                          data=[random.randint(0, 255) for _ in range(8)],
                          is_extended_id=False)

def interface_activity(cansocket):

    frames_received = 0
    errno19_count = 0
    timeouts = 0

    # create the device interface using index 11 and verify that the interface was created
    subprocess.call(['sudo', 'ip', 'link', 'add', 'index', '11', 'dev', 'vcan0', 'type', 'vcan'])
    subprocess.call(['sudo', 'ip', 'link', 'set', 'vcan0', 'up'])
    assert(subprocess.check_output(['ip', 'link', 'show']).decode('utf-8').find('11: vcan0') != -1)

    # create bus for sending messages and bind the socket to the channel
    bus = can.interface.Bus(channel='vcan0', bustype='socketcan')
    cansocket.bind(('vcan0',))

    # send a message and try to receive it
    for i in range(10):
        bus.send(_RANDOM_MESSAGE)
        try:
            frame = cansocket.recv(_FRAME_SIZE)
            if frame is not None:
                frames_received += 1
        except socket.timeout:
            timeouts += 1
        except OSError as err:
            if err.errno == 19:
                errno19_count += 1

    print("Frames received: " + str(frames_received))
    print("No such device errors: " + str(errno19_count))
    print("Number of timeouts: " + str(timeouts))

    # Remove the device interface and verify that it's been deleted
    subprocess.call(['sudo', 'ip', 'link', 'del', 'dev', 'vcan0'])
    assert (subprocess.check_output(['ip', 'link', 'show']).decode('utf-8').find('vcan0') == -1)


test_cansocket = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
test_cansocket.settimeout(0.1)

print("\nFIRST TIME (WORKING)\n")
interface_activity(test_cansocket)
print("\nSECOND TIME (BROKEN)\n")
interface_activity(test_cansocket)