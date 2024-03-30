import serial
import packet_pb2
from google.protobuf.message import DecodeError 
import pipe_header
import os
from datetime import datetime

class Session:
    def __init__(self, id, arduino, serial=False):
        self.id = id
        self.arduino = arduino
        self.serial = serial

    def from_filename(filename):
        arduino = filename[0] == "a"
        id = int(filename[1:])
        return Session(id, arduino, False)
    
    def filename(self):
        prefix = "a" if self.arduino else "r"
        return f"{prefix}{str(self.id)}"

    def __hash__(self):
        return self.id*2 + int(self.arduino)

    def __eq__(self, other):
        return (self.id == other.id) and (self.arduino == other.arduino)
    
    def __str__(self):
        prefix = "a" if self.arduino else "r"
        time = datetime.fromtimestamp(self.id).strftime("%Y-%m-%d %H:%M:%S")
        suffix = "(Serial)" if self.serial else ""
        return f"{prefix} {time} {suffix}"

class DataManager:
    def __init__(self, pipe, arduino_port):
        self.sessions = {}
        self.pipe = pipe
        self.sending_session = None
        self.last_session_added = None
        
        self.session_pipes = {} 
        
        self.data_dir = "./data"

        self.arduino = None
        if arduino_port != None:
            self.arduino = serial.Serial(port=arduino_port, baudrate=9600, timeout=0.1)
        
        for filename in os.listdir(self.data_dir):
            session = Session.from_filename(filename)
            self.from_file(session)

    def session_file(self, session):
        return f"{self.data_dir}/{session.filename()}"

    def send_sessions(self):
        message = list(self.sessions.keys())
        self.pipe.send((pipe_header.SESSIONS, message))
    
    def add_packet(self, packet, arduino):
        session = Session(packet.header.session_id, arduino)
        if not session in self.sessions:
            self.sessions[session] = []
        self.sessions[session].append(packet)

        if session == self.sending_session:
            self.pipe.send((pipe_header.PACKET, packet))

        for pipe in self.session_pipes[session]:
            pipe.send(packet)

        data = packet.SerializeToString()
        with open(self.session_file(session), "ab+") as file:
            file.write(bytes(len(data)) + bytes(data))

        if session != self.last_session_added:
            self.last_session_added = session
            self.send_sessions()

    def from_file(self, session):
        packets = []
        with open(self.session_file(session), "rb") as file:
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
        self.sessions[session] = packets

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
            self.add_packet(packet, True)

    def read_message(self):
        #print("Checking for message")
        if self.pipe.poll(timeout=0.1):
            #print("Got message")
            try:
                message = self.pipe.recv()
                if message[0] == pipe_header.CHANGE_SESSION:
                    session = message[1]
                    self.sending_session = session
                    for packet in self.sessions[session]:
                        self.pipe.send((pipe_header.PACKET, packet))
                elif message[0] == pipe_header.ADD_PIPE:
                    pipe, session = message[1]
                    self.add_session_pipe(pipe, session)
            except EOFError:
                return True
        return False

    def add_session_pipe(self, pipe, session):
        if not session in self.session_pipes:
            self.session_pipes[session] = []
        self.session_pipes[session].append(pipe)

        for packet in self.sessions[session]:
            pipe.send(packet)

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

if __name__ == "__main__":
    session = Session(213, True, False)
    print(session.__hash__())