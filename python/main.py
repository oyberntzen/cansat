import data
import multiprocessing
import pipe_header
import tui
import time

def main():
    data_pipe, other_pipe = multiprocessing.Pipe()
    data_manager = data.DataManager(other_pipe, None)
    data_process = multiprocessing.Process(target=data_manager.run)
    data_process.start()

    variables = ["temp", "humid", "speed"]
    term = tui.TUI([data.Session(1, True, True)], variables, 2, None)

    session_pipe = None

    while True:
        while data_pipe.poll():
            message = data_pipe.recv()
            #print(message)
            if message[0] == pipe_header.SESSIONS:
                sessions = message[1]
                #serial_session = message[1]["serial"]
                #if serial_session != None:
                #    sessions[sessions.index(serial_session)] += " (Serial)"
                term.change_sessions(sessions)
            """elif message[0] == pipe_header.PACKET:
                packet = message[1]
                term.change_packet(packet)"""
        if session_pipe != None:
            while session_pipe.poll():
                packet = session_pipe.recv()
                term.change_packet(packet)

        message = term.update()
        if message != None:
            flag, message_data = message
            if flag == tui.QUIT:
                break
            if flag == tui.CHANGE_SESSION:
                session_pipe, other_pipe = multiprocessing.Pipe()
                data_pipe.send((pipe_header.ADD_PIPE, (other_pipe, message_data)))
                #data_pipe.send((pipe_header.CHANGE_SESSION, message_data))

            print(flag, message_data)
        time.sleep(1/60)

if __name__ == "__main__":
    main()