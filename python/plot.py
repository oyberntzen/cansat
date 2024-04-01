import packet_pb2
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def all_variables(packet, path=[]):
    if hasattr(packet, "DESCRIPTOR"):
        variables = []
        fields = packet.DESCRIPTOR.fields
        for field in fields:
            path.append(field.name)
            obj = getattr(packet, field.name)
            variables += all_variables(obj, path)
            path.pop()
        return variables

    return [PathVariable(path)]

class PathVariable:
    def __init__(self, path):
        self.path = path.copy()

    def __str__(self):
        return self.path[len(self.path)-1]

    def value(self, packet):
        current_packet = packet
        for i in self.path:
            current_packet = getattr(current_packet, i)
        return current_packet

class Plot2D:
    def __init__(self, session_pipe, x_variable, y_variable, packets):
        self.session_pipe = session_pipe
        self.x_variable = x_variable
        self.y_variable = y_variable

        self.x_values = []
        self.y_values = []

        for packet in packets:
            self.add_packet(packet)

        self.changed = True

    def add_packet(self, packet):
        self.x_values.append(self.x_variable.value(packet))
        self.y_values.append(self.y_variable.value(packet))

    def run(self):
        fig = plt.figure()
        self.axes = fig.add_subplot(1,1,1)
        ani = animation.FuncAnimation(fig, self.animate, interval=200)
        plt.show()

    def animate(self, i):
        while self.session_pipe.poll():
            self.changed = True
            packet = self.session_pipe.recv()
            self.add_packet(packet)

        if self.changed:
            self.axes.clear()
            self.axes.plot(self.x_values, self.y_values)
        self.changed = False

if __name__ == "__main__":
    packet = packet_pb2.Packet()
    variables = all_variables(packet)
    for i in variables:
        print(str(i()))
        print(i().value(packet))