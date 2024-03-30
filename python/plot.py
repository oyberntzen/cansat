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
    def __init__(self, session_pipe, x_variable, y_variable):
        self.session_pipe = session_pipe
        self.x_variable = x_variable
        self.y_variable = y_variable

        self.x_values = []
        self.y_values = []

        fig = plt.figure()
        self.axes = fig.add_subplot(1,1,1)
        ani = animation.FuncAnimation(fig, self.animate, interval=200)
        plt.show()

    def animate(self, i):
        changed = False
        while self.session_pipe.poll():
            changed = True
            packet = self.session_pipe.recv()
            self.x_values.append(self.x_variable.value(packet))
            self.y_values.append(self.y_variable.value(packet))

        if changed:
            self.axes.clear()
            self.axes.plot(self.x_values, self.y_values)

def plot2d(data_pipe, x_var, y_var):
    x = []
    y = []
    def animate(i):
        with packets_lock:
            for p in packets:
                x.append(p.header.index)
                y.append(p.telemetry.env.temperature)

        ax1.clear()
        ax1.plot(x, y)
    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)
    ani = animation.FuncAnimation(fig, animate, interval=200)
    plt.show()


if __name__ == "__main__":
    packet = packet_pb2.Packet()
    variables = all_variables(packet)
    for i in variables:
        print(str(i()))
        print(i().value(packet))