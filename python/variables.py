import packet_pb2
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