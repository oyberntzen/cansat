import serial
import packet_pb2

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import threading

packets = []
packets_lock = threading.Lock()
done = False

def packets_serial():
    print("test")
    arduino = serial.Serial(port="COM6", baudrate=9600, timeout=0.01)
    while not done:
        first_byte = []
        while len(first_byte) == 0:
            first_byte = arduino.read(1)
            if done:
                return
        length = int(first_byte[0])

        data = arduino.read(length)
        if len(data) != length:
            continue

        packet = packet_pb2.Packet()
        packet.ParseFromString(data)
        print(packet)

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
    global done
    while not done:
        command = input("> ").split()

        if command[0] == "quit":
            done = True
        elif command[0] == "serial":
            threading.Thread(target=packets_serial).start()
        elif command[0] == "plot":
            plot_variable()

if __name__ == "__main__":
    main()