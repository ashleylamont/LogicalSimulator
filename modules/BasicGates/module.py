# Basic Gates


# Get input states of gate connections and return states as a boolean array.
def get_input_ab(gate_object):
    inputs = gate_object.get_inputs()
    input_a = list(filter(lambda c: c.name == "InputA", inputs))[0]
    input_b = list(filter(lambda c: c.name == "InputB", inputs))[0]
    input_a_state = False
    input_b_state = False
    for input_obj in input_a.get_connections():
        if input_obj.parent.cached_state:
            input_a_state = True
    for input_obj in input_b.get_connections():
        if input_obj.parent.cached_state:
            input_b_state = True
    return [input_a_state, input_b_state]


def and_gate(self, modules=None):
    inputs = get_input_ab(self)
    if inputs[0] and inputs[1]:
        return True
    else:
        return False


def nand_gate(self, modules=None):
    inputs = get_input_ab(self)
    if inputs[0] and inputs[1]:
        return False
    else:
        return True


def or_gate(self, modules=None):
    inputs = get_input_ab(self)
    if inputs[0] or inputs[1]:
        return True
    else:
        return False


def xor_gate(self, modules=None):
    nand_condition = nand_gate(self)
    or_condition = or_gate(self)
    return nand_condition and or_condition


def nor_gate(self, modules=None):
    inputs = get_input_ab(self)
    if inputs[0] or inputs[1]:
        return False
    else:
        return True


def not_gate(self, modules=None):
    inputs = self.get_inputs()[0].get_connections()
    for input_obj in inputs:
        if input_obj.parent.cached_state:
            return False
    return True


def relay_gate(self, modules=None):
    inputs = self.get_inputs()[0].get_connections()
    for input_obj in inputs:
        if input_obj.parent.cached_state:
            return True
    return False


def on_gate(self, modules=None):
    return True


def off_gate(self, modules=None):
    return False


# Expose functions in a dictionary so that it can be easily referenced by index
mod_exports = {
    "and_gate": and_gate,
    "nand_gate": nand_gate,
    "nor_gate": nor_gate,
    "not_gate": not_gate,
    "or_gate": or_gate,
    "relay_gate": relay_gate,
    "off_gate": off_gate,
    "on_gate": on_gate,
    "xor_gate": xor_gate
}
