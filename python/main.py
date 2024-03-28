import data
import multiprocessing
import pipe_header
import tui

def main():
    data_pipe, other_pipe = multiprocessing.Pipe()
    data_manager = data.DataManager(other_pipe, None)
    data_process = multiprocessing.Process(target=data_manager.run)
    data_process.start()

    variables = ["temp", "humid", "speed"]
    term = tui.TUI(["test"], variables, 2, None)

    while True:
        if data_pipe.poll(0.1):
            message = data_pipe.recv()
            #print(message)
            if message[0] == pipe_header.SESSIONS:
                sessions = message[1]["sessions"]
                #serial_session = message[1]["serial"]
                #if serial_session != None:
                #    sessions[sessions.index(serial_session)] += " (Serial)"
                term.change_sessions(sessions)
            elif message[0] == pipe_header.PACKET:
                packet = message[1]
                term.change_packet(packet)

        message = term.update()
        if message != None:
            flag, message_data = message
            if flag == tui.QUIT:
                break
            if flag == tui.CHANGE_SESSION:
                data_pipe.send((pipe_header.CHANGE_SESSION, message_data))
            print(flag, message_data)

if __name__ == "__main__":
    main()