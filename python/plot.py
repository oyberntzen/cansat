import packet_pb2
import matplotlib.pyplot as plt
import matplotlib.animation as animation

class Variable:
    def __init__(self, value, name):
        self.value = value
        self.name = name
    
    def __str__(self):
        return self.name

def all_path_variables(packet=packet_pb2.Packet(), path=[]):
    if hasattr(packet, "DESCRIPTOR"):
        variables = []
        fields = packet.DESCRIPTOR.fields
        for field in fields:
            path.append(field.name)
            obj = getattr(packet, field.name)
            variables += all_path_variables(obj, path)
            path.pop()
        return variables

    variable_path = path.copy()
    def value(packet):
        current_variable = packet[-1]
        for i in variable_path:
            current_variable = getattr(current_variable, i)
        return current_variable

    return [Variable(value, variable_path[-1])]

def all_variables():
    variables = all_path_variables()

    variables_dict = {}
    for variable in variables:
        if variable.name in variables_dict:
            print(f"Variable name not uniquie: {variable.name}")
        variables_dict[variable.name] = variable

    return variables_dict

class Plot2D:
    def __init__(self, session_pipe, x_name, y_name, packets):
        self.session_pipe = session_pipe
        self.x_name = x_name
        self.y_name = y_name

        self.x_values = []
        self.y_values = []

        self.starting_packets = packets
        self.packets = []

        self.changed = True

    def add_packet(self, packet):
        self.packets.append(packet)
        self.x_values.append(self.x_variable.value(self.packets))
        self.y_values.append(self.y_variable.value(self.packets))

    def run(self):
        variables = all_variables()
        self.x_variable = variables[self.x_name]
        self.y_variable = variables[self.y_name]

        for packet in self.starting_packets:
            self.add_packet(packet)

        fig = plt.figure()
        self.axes = fig.add_subplot(1,1,1)
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
            self.axes.plot(self.x_values, self.y_values)
        self.changed = False