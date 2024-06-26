import serial
import packet_pb2
from google.protobuf.message import DecodeError 
import os
from datetime import datetime

class Session:
    def __init__(self, id, arduino, serial=False):
        self.id = id
        self.arduino = arduino
        self.serial = serial

    def from_filename(filename):
        id_hex, extension = filename.lower().split(".")
        arduino = extension == "ard"
        id = int(id_hex, 16)
        return Session(id, arduino, False)
    
    def filename(self):
        id_hex = hex(self.id)[2:]
        extension = "ard" if self.arduino else "rad"
        return f"{id_hex}.{extension}"

    def __hash__(self):
        return self.id*2 + int(self.arduino)

    def __eq__(self, other):
        if other is None:
            return False
        return (self.id == other.id) and (self.arduino == other.arduino)
    
    def __str__(self):
        prefix = "a" if self.arduino else "r"
        time = datetime.fromtimestamp(self.id).strftime("%Y-%m-%d %H:%M:%S")
        suffix = "(S)" if self.serial else ""
        return f"{prefix} {time} {suffix}"

class DataManager:
    def __init__(self, arduino_port, logger):
        self.logger = logger

        self.sessions = {}
        self.last_session_added = None
        
        self.data_dir = "./data"

        self.arduino = None
        if arduino_port != None:
            try:
                self.arduino = serial.Serial(port=arduino_port, baudrate=9600, timeout=0.1)
            except:
                self.logger.put(f"Could not connect to {arduino_port}")
        
        for filename in os.listdir(self.data_dir):
            session = Session.from_filename(filename)
            self.from_file(session)

    def session_file(self, session):
        return f"{self.data_dir}/{session.filename()}"
    
    def add_packet(self, packet, session):
        if not session in self.sessions:
            self.sessions[session] = []
        self.sessions[session].append(packet)

        data = packet.SerializeToString()
        with open(self.session_file(session), "ab+") as file:
            file.write(len(data).to_bytes(1) + bytes(data))

        if session != self.last_session_added:
            self.last_session_added = session

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
                    print(f"Wrong file data ({session.id})")
                    break
                packet = self.data_to_packet(data)
                if packet == None:
                    print(f"Wrong file data ({session.id})")
                    break
                packets.append(packet)
        self.sessions[session] = packets

    def read_serial_packet(self):
        if self.arduino == None:
            return None

        first_byte = self.arduino.read(1)
        if len(first_byte) == 0:
            return None

        length = int(first_byte[0])

        data = self.arduino.read(length)
        if len(data) != length:
            self.logger.put("Wrong packet length")
            return None

        packet = self.data_to_packet(data)
        if packet != None:
            session_id = packet.header.session_id
            self.logger.put(f"Recieved packet ({session_id})")
            session = Session(session_id, False)
            self.add_packet(packet, session)
            return packet, session
        return None

    def all_sessions(self):
        sessions = list(self.sessions.keys())
        for session in sessions:
            if session == self.last_session_added:
                session.serial = True
            else:
                session.serial = False
        sessions.sort(key = lambda s: -s.__hash__())
        return sessions

    def data_to_packet(self, data):
        packet = packet_pb2.Packet()
        try:
            packet.ParseFromString(data)
        except DecodeError as e:
            self.logger.put("Invalid packet")
            return None
        return packet

if __name__ == "__main__":
    manager = DataManager(None)