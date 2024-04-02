import data
import multiprocessing
import tui
import time
import plot

def main():
    #data_manager = data.DataManager("COM6")
    data_manager = data.DataManager(None)

    variables = list(plot.all_variables().values())
    term = tui.TUI(data_manager.all_sessions(), variables)

    current_session = None
    plot_pipes = {}

    while True:
        term_changed = False

        new_data = data_manager.read_serial_packet()
        if new_data != None:
            term.change_sessions(data_manager.all_sessions())
            
            packet, session = new_data
            if session in plot_pipes:
                removes = []
                for pipe in plot_pipes[session]:
                    if pipe.poll():
                        removes.append(pipe)
                    else:
                        pipe.send(packet)
                for pipe in removes:
                    plot_pipes[session].remove(pipe)

            current_packets = []

            term_changed = True

        current_packets = []
        if current_session != None:
            current_packets = data_manager.sessions[current_session]
        message = term.update()
        if message != None:
            flag, message_data = message
            if flag == tui.QUIT:
                break
            if flag == tui.CHANGE_SESSION:
                current_session = message_data
            if flag == tui.PLOT_VARIABLE:
                pipe, plot_pipe = multiprocessing.Pipe()
                if not current_session in plot_pipes:
                    plot_pipes[current_session] = []
                plot_pipes[current_session].append(pipe)

                plotter = plot.Plot2D(plot_pipe, message_data[0].name, message_data[1].name, data_manager.sessions[current_session])
                plot_process = multiprocessing.Process(target=plotter.run)
                plot_process.start()

            if message != None:
                term_changed = True
        
        if term_changed:
            if current_session != None:
                current_packets = data_manager.sessions[current_session]
            term.draw(current_packets)

        time.sleep(1/60)

if __name__ == "__main__":
    main()