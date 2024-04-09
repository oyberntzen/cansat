import packet_pb2
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math

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
    def value(packets):
        current_variable = packets[-1]
        for i in variable_path:
            current_variable = getattr(current_variable, i)
        return current_variable

    return [Variable(value, variable_path[-1])]

def altitude2(packets):
    average_temperature = 0
    for packet in packets:
        average_temperature += packet.telemetry.env.temperature + 273.15
    average_temperature /= len(packets)

    pressure0 = packets[0].telemetry.env.pressure
    pressure1 = packets[-1].telemetry.env.pressure

    if pressure1 == 0:
        return 0

    gas_constant = 8.314
    gravity = 9.81
    molar_mass = 0.029

    height = gas_constant*average_temperature / (gravity*molar_mass) * math.log(pressure0/pressure1)
    return height

def latitude_meters(packets):
    latitude0 = packets[0].telemetry.gps.latitude
    latitude1 = packets[-1].telemetry.gps.latitude

    difference = latitude1 - latitude0
    radius = 6371e3
    meters = math.tan(math.radians(difference)) * radius
    return meters

def longitude_meters(packets):
    longitude0 = packets[0].telemetry.gps.longitude
    longitude1 = packets[-1].telemetry.gps.longitude

    difference = longitude1 - longitude0
    radius = 6371e3
    meters = math.tan(math.radians(difference)) * radius
    return meters


def all_variables():
    variables = all_path_variables()
    variables.append(Variable(altitude2, "altitude2"))
    variables.append(Variable(latitude_meters, "latitudeM"))
    variables.append(Variable(longitude_meters, "longitudeM"))

    variables_dict = {}
    for variable in variables:
        if variable.name in variables_dict:
            print(f"Variable name not uniquie: {variable.name}")
        variables_dict[variable.name] = variable

    return variables_dict

class Plot2D:
    def __init__(self, session_pipe, names, last, num, equal, packets):
        self.session_pipe = session_pipe
        self.names = names

        self.last = last
        self.num = num
        self.equal = equal

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
        variables = all_variables()
        self.variables = list(map(lambda name: variables[name], self.names))

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

            if self.equal:
                if self.dimensions == 2:
                    self.axes.axis("equal")
                else:
                    self.axes.set(xlim=(min(self.values[0]), max(self.values[0])), ylim=(min(self.values[1]), max(self.values[1])))
                    if self.dimensions == 3:
                        self.axes.set(zlim=(min(self.values[2]), max(self.values[2])))

            plot_values = []
            for dimension in range(self.dimensions):
                if self.last:
                    plot_values.append(self.values[dimension][-self.num:])
                else:
                    print(self.num)
                    plot_values.append(self.values[dimension][self.num:])

            self.axes.plot(*plot_values)
        self.changed = False