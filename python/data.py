import serial
import packet_pb2
from google.protobuf.message import DecodeError 
import pipe_header
import os


# Shared state:
# Packets
# Sessions
# Done flag

# Queues and pipes:
# Packets -> main process -> plots
# Sessions pipes
# Done flag pipes

class DataManager:
    def __init__(self, pipe, arduino_port):
        self.sessions = {}
        self.pipe = pipe
        self.sending_session = None
        self.last_session_added = None
        
        self.data_dir = "./data"

        self.arduino = None
        if arduino_port != None:
            self.arduino = serial.Serial(port=arduino_port, baudrate=9600, timeout=0.1)
        
        for filename in os.listdir(self.data_dir):
            session_id = int(filename)
            self.from_file(session_id)

    def session_file(self, session_id):
        return f"{self.data_dir}/{session_id}"

    def send_sessions(self):
        message = {}
        message["sessions"] = list(self.sessions.keys())
        message["serial"] = self.last_session_added
        self.pipe.send((pipe_header.SESSIONS, message))
    
    def add_packet(self, packet):
        session_id = packet.header.session_id
        if not session_id in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(packet)

        if session_id == self.sending_session:
            self.pipe.send((pipe_header.PACKET, packet))

        data = packet.SerializeToString()
        with open(self.sending_session(session_id), "ab+") as file:
            file.write(bytes(len(data)) + bytes(data))

        if session_id != self.last_session_added:
            self.last_session_added = session_id
            self.send_sessions()

    def from_file(self, session_id):
        packets = []
        with open(self.session_file(session_id), "rb") as file:
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
        self.sessions[session_id] = packets

    def read_serial_packet(self):
        if self.arduino == None:
            return

        first_byte = self.arduino.read(1)
        if len(first_byte) == 0:
            return

        length = int(first_byte[0])

        data = self.arduino.read(length)
        if len(data) != length:
            return

        packet = data_to_packet(data)
        if packet != None:
            self.add_packet(packet)

    def read_message(self):
        #print("Checking for message")
        if self.pipe.poll(timeout=0.1):
            #print("Got message")
            try:
                message = self.pipe.recv()
                if message[0] == pipe_header.CHANGE_SESSION:
                    session_id = message[1]
                    self.sending_session = session_id
                    for packet in self.sessions[session_id]:
                        self.pipe.send((pipe_header.PACKET, packet))

            except EOFError:
                return True
        return False

    def run(self):
        self.send_sessions()
        while True:
            self.read_serial_packet()
            if self.read_message():
                break
        
        if self.arduino != None:
            self.arduino.close()

def data_to_packet(data):
    packet = packet_pb2.Packet()
    try:
        packet.ParseFromString(data)
    except DecodeError as e:
        print("Invalid packet")
        return None
    return packet