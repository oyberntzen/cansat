import data
import multiprocessing
import pipe_header
import tui
import time
import plot
import packet_pb2

def main():
    data_pipe, other_pipe = multiprocessing.Pipe()
    data_manager = data.DataManager(other_pipe, None)
    data_process = multiprocessing.Process(target=data_manager.run)
    data_process.start()

    packet = packet_pb2.Packet()
    #variables = list(map(lambda x: x(), plot.all_variables(packet)))
    variables = plot.all_variables(packet)
    term = tui.TUI([data.Session(1, True, True)], variables, 2, None)

    session_pipe = None
    current_session = None

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
                current_session = message_data
                session_pipe, other_pipe = multiprocessing.Pipe()
                data_pipe.send((pipe_header.ADD_PIPE, (other_pipe, current_session)))
                #data_pipe.send((pipe_header.CHANGE_SESSION, message_data))
            if flag == tui.PLOT_VARIABLE:
                data_manager_pipe, plot_pipe = multiprocessing.Pipe()
                data_pipe.send((pipe_header.ADD_PIPE, (data_manager_pipe, current_session)))
                plot_process = multiprocessing.Process(target=plot.Plot2D, args=(plot_pipe, message_data[0], message_data[1]))
                plot_process.start()


            print(flag, message_data)
        time.sleep(1/60)

if __name__ == "__main__":
    main()