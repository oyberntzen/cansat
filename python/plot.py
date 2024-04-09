import matplotlib.pyplot as plt
import matplotlib.animation as animation
import variables

class Plot:
    def __init__(self, session_pipe, names, settings, packets, logger):
        self.logger = logger
        self.session_pipe = session_pipe
        self.names = names

        self.settings = settings

        self.dimensions = len(names)
        self.values = [[] for i in range(self.dimensions)]

        self.starting_packets = packets
        self.packets = []

        self.changed = True

    def add_packet(self, packet):
        self.packets.append(packet)
        for i in range(self.dimensions):
            self.values[i].append(self.variables[i].value(self.packets))

    def run(self):
        vars = variables.all_variables()
        self.variables = list(map(lambda name: vars[name], self.names))
        self.logger.put(f"Plotting: {self.names}")

        for packet in self.starting_packets:
            self.add_packet(packet)

        fig = plt.figure()
        projection = "rectilinear"
        if self.dimensions == 3:
            projection = "3d"
        self.axes = fig.add_subplot(1,1,1, projection=projection)


        ani = animation.FuncAnimation(fig, self.animate, interval=200, cache_frame_data=False)
        plt.show()
        self.session_pipe.send(0)

    def animate(self, i):
        while self.session_pipe.poll():
            self.changed = True
            packet = self.session_pipe.recv()
            self.add_packet(packet)

        if self.changed:
            self.axes.clear()

            if self.settings["axis"] == 1:
                if self.dimensions == 2:
                    self.axes.axis("equal")
                else:
                    pass #TODO

            plot_values = []
            for dimension in range(self.dimensions):
                if self.settings["start_choice"] == 1:
                    plot_values.append(self.values[dimension][-self.settings["start_num"]:])
                else:
                    plot_values.append(self.values[dimension][self.settings["start_num"]:])

            self.axes.plot(*plot_values)
        self.changed = False