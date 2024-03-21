import serial
import packet_pb2
from google.protobuf.message import DecodeError 

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import threading
import os

packets = []
packets_lock = threading.Lock()
done = threading.Event()

data_dir = "./data"

def data_to_packet(data):
    packet = packet_pb2.Packet()
    try:
        packet.ParseFromString(data)
    except DecodeError as e:
        print("Invalid packet")
        return None
    return packet

def read_packet(arduino):
    while not done.is_set():
        first_byte = []
        while len(first_byte) == 0 and not done.is_set():
            first_byte = arduino.read(1)
        if done.is_set():
            break
        length = int(first_byte[0])

        data = arduino.read(length)
        print(data)
        if len(data) != length:
            continue

        packet = data_to_packet(data)
        if packet == None:
            continue
        print(packet)
        print(packet.telemetry.gps.latitude)
        return packet

def read_packets(arduino, first_packet=None):
    print("Reading")
    global packets

    if first_packet == None:
        first_packet = read_packet(arduino)
        print(first_packet)
    session_id = first_packet.header.session_id

    # Read packets from file
    with packets_lock:
        packets = []
        path = f"{data_dir}/{session_id}"
        if os.path.exists(path):
            with open(path, "rb") as file:
                while True:
                    first_byte = file.read(1)
                    if len(first_byte) != 1:
                        break
                    length = int(first_byte[0])

                    data = file.read(length)
                    if len(data) != length:
                        print("Wrong file data")
                        break
                    packet = data_to_packet(data)
                    if packet == None:
                        print("Wrong file data")
                        break
                    packets.append(packet)
        else:
            open(path, "x").close()

        packets.append(first_packet)

    with open(path, "wb") as file:
        while not done.is_set():
            packet = read_packet(arduino)

            if packet.header.session_id != session_id:
                read_packets(arduino, first_packet)
                break

            with packets_lock:
                packets.append(packet)

            data = packet.SerializeToString()
            file.write(data)

def plot_variable():
    def animate(i):
        x = []
        y = []
        with packets_lock:
            for p in packets:
                x.append(p.header.index)
                y.append(p.telemetry.env.temperature)

        ax1.clear()
        ax1.plot(x, y)
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    ani = animation.FuncAnimation(fig, animate, interval=200)
    plt.show()


def main():
    """packet = packet_pb2.Packet()
    packet.header.session_id = 2
    data = packet.SerializeToString()
    print(data)
    print(data_to_packet(data))"""


    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    arduino = serial.Serial(port="COM6", baudrate=9600, timeout=0.1)
    #read_packets(arduino)
    thread = threading.Thread(target=read_packets, args=(arduino, None))
    thread.start()

    plot_variable()
    done.set()
    thread.join()
    arduino.close()
    

    """global done
    while not done:
        command = input("> ").split()

        if command[0] == "quit":
            done = True
        elif command[0] == "serial":
            threading.Thread(target=packets_serial).start()
        elif command[0] == "plot":
            plot_variable()"""

if __name__ == "__main__":
    main()