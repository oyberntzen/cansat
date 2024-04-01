import data
import multiprocessing
import pipe_header
import tui
import time
import plot
import packet_pb2

def main():
    data_manager = data.DataManager(None)

    packet = packet_pb2.Packet()
    #variables = list(map(lambda x: x(), plot.all_variables(packet)))
    variables = plot.all_variables(packet)
    term = tui.TUI(list(data_manager.sessions.keys()), variables, 2, None)

    current_session = None
    plot_pipes = {}

    while True:
        new_data = data_manager.read_serial_packet()
        if new_data != None:
            term.change_sessions(list(data_manager.sessions.keys()))
            if current_session != None:
                term.change_packet(data_manager.sessions[current_session][-1])
            
            packet, session = new_data
            if session in plot_pipes:
                for pipe in plot_pipes[session]:
                    pipe.send(packet)

        message = term.update()
        if message != None:
            flag, message_data = message
            if flag == tui.QUIT:
                break
            if flag == tui.CHANGE_SESSION:
                current_session = message_data
                term.change_packet(data_manager.sessions[current_session][-1])
            if flag == tui.PLOT_VARIABLE:
                pipe, plot_pipe = multiprocessing.Pipe()
                if not current_session in plot_pipes:
                    plot_pipes[current_session] = []
                plot_pipes[current_session].append(pipe)

                plotter = plot.Plot2D(plot_pipe, message_data[0], message_data[1], data_manager.sessions[current_session])
                plot_process = multiprocessing.Process(target=plotter.run)
                plot_process.start()
        time.sleep(1/60)

if __name__ == "__main__":
    main()