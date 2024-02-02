import serial
import packet_pb2

arduino = serial.Serial(port="COM6", baudrate=9600)

while True:
    length = int(arduino.read(1)[0])
    data = arduino.read(length)
    packet = packet_pb2.Packet()
    packet.ParseFromString(data)
    print(packet)