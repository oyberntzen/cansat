import serial
import packet_pb2

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import threading
import os

packets = []
packets_lock = threading.Lock()
done = threading.Event()

data_dir = "./data"

def read_packet(arduino):
    while not done.is_set():
        first_byte = []
        while len(first_byte) == 0:
            first_byte = arduino.read(1)
        length = int(first_byte[0])

        data = arduino.read(length)
        if len(data) != length:
            continue

        packet = packet_pb2.Packet()
        packet.ParseFromString(data)
        print(packet)
        return packet


def read_packets(arduino, first_packet=None):
    if first_packet == None:
        first_packet = read_packet(arduino)
    session_id = first_packet.header.session_id
    packets = []

    # Read packets from file

    packets.append(first_packet)

    print("test")
    while not done.is_set():
        packet = read_packet(arduino)

        if packet.header.session_id != session_id:
            read_packets(arduino, first_packet)
            return

        with packets_lock:
            packets.append(packet)

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
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    thread = threading.Thread(target=read_packets)
    thread.start()

    plot_variable()
    done.set()
    

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