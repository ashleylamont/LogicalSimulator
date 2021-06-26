import typing
from tkinter import messagebox
import time

from utils import generate_id, Vector

print("Loaded Simulation.py")

lastError = 0  # Time in seconds since last error message, prevents spamming users with error boxes


# Base object class for all gates and items on canvas
class Object:
    def __init__(self, canvas_objects: dict, position=None):
        if position is None:
            position = [0, 0]
        self.position = position
        self.modules = {}
        self.id = generate_id()
        self.connections = []
        self.size: Vector = [0, 0]
        self.image = ""
        self.cached_state = False
        print("New Object created with ID %s" % self.id)
        # Attach available_object to the master array of objects so that it can be referenced later. Yes of course
        # that will work, python is pass-by-ref so instances of objects can be assigned to an array without having to
        # worry about duplication. Don't worry, I checked. Side note: I actually checked and it's
        # pass-by-available_object-ref, which is strictly speaking, different. However, in this case, it won't matter
        # since this specific outcome is the same regardless. Just as long as you only use mutable object methods.
        canvas_objects[self.id] = self

    def calc_function(self, modules=None):
        # Define a stub to be overwritten in child classes.
        pass

    # Returns a list of all connections in self.connections with a conn_type of "Input".
    def get_inputs(self):
        return list(filter(lambda connection: connection.conn_type == "Input", self.connections))

    # Returns a list of all connections in self.connections with a conn_type of "Input".
    def get_outputs(self):
        return list(filter(lambda connection: connection.conn_type == "Output", self.connections))

    # Returns first connection in self.connections with name property matching function parameter name.
    def get_connection_by_name(self, name):
        for connection in self.connections:
            if connection.name == name:
                return connection
        return None


# Connection class that describes all of the connection points on an object.
class Connection:
    def __init__(self, parent: Object, position: Vector, name: str, conn_type: int, connectors: list):
        self.parent = parent  # May need to change this to make use of IDs depending on how python works
        self.position = position
        self.name = name
        self.conn_type = ["Input", "Output"][conn_type]  # Uses an array index to enforce consistency
        self.tooltip: Tooltip
        self.connectors = connectors

    # Returns a list of all of the connections attached to this via connectors
    def get_connections(self):
        connected = list()
        if self.conn_type == "Input":
            connected = list(
                map(lambda connector: connector.input,
                    filter(lambda connector: connector.output == self, self.connectors)
                    )
            )
        elif self.conn_type == "Output":
            connected = list(
                map(lambda connector: connector.output,
                    filter(lambda connector: connector.input == self, self.connectors)
                    )
            )
        return connected


# Connector class that links an output connection to an input connection
class Connector:
    def __init__(self, conn_input: Connection, conn_output: Connection, connectors: list):
        self.output = conn_output
        self.input = conn_input
        connectors.append(self)


# Tooltip object to enforce data consistency in storing information for
class Tooltip:
    def __init__(self, object_name: str, object_description: str, object_image: str = None):
        self.object_description = object_description
        self.object_name = object_name
        self.object_image = object_image


# Calculate on/off states of all gates in circuit by picking a random object and backtracking to the original gate,
# working forwards from there.
def calculate_logic(canvas_objects: dict):
    if len(canvas_objects) == 0:
        return None
    i = 0
    canvas_ids = list(canvas_objects.keys())
    objects_to_calculate = []
    check_chain = []
    while i < len(canvas_objects):
        objects_to_calculate.append(canvas_objects[canvas_ids[i]])
        i = i + 1
    current_object: Object = objects_to_calculate[0]
    while len(objects_to_calculate) > 0:
        i_alternate = 0
        inputs: typing.List[Connection] = current_object.get_inputs()
        while i_alternate < len(inputs):
            sub_inputs = inputs[i_alternate].get_connections()
            temp_bool = False
            temp_object = None
            for sub_input in sub_inputs:
                if sub_input.parent in objects_to_calculate:
                    temp_bool = True
                    temp_object = sub_input.parent
                    break
            if temp_bool:
                # Catch looped circuits and prevent infinite repetition.
                if current_object in check_chain:
                    global lastError
                    if lastError + 10 < time.time():
                        messagebox.showerror(title="Fatal Exception", message="You have created a loop in your "
                                                                              "simulation. The program is unable to "
                                                                              "calculate this and will pause execution "
                                                                              "until you remove the loop.\nThis error "
                                                                              "will show again in 10 seconds if you "
                                                                              "do not remove the loop.")
                        lastError = time.time()
                    return None
                check_chain.append(current_object)
                current_object = temp_object
                break
            else:
                i_alternate += 1
        if i_alternate >= len(inputs):
            # noinspection PyNoneFunctionAssignment
            current_object.cached_state = current_object.calc_function(modules=current_object.modules)
            objects_to_calculate.remove(current_object)
            if len(check_chain) > 0:
                current_object = check_chain.pop()
            elif len(objects_to_calculate) > 0:
                current_object = objects_to_calculate[0]
