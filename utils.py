import importlib
import os
import random
import subprocess
import sys
import tkinter as tk
import typing

print("Loaded Utils.py")


# Define an install package function to be used in the module loader
def install(package):
    module = None
    try:
        module = importlib.import_module(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        module = importlib.import_module(package)
    finally:
        return module


# Define a vector type for positions and sizes
Vector = typing.List[int]

# Declare default used_ids variable
default_used_ids = None


# Function to generate an 8-digit hexadecimal id for an available_object.
# Has a maximum of 4.3 Billion possible IDs, so that way they can be unique.
def generate_id(existing_ids=None):
    # Run a check to test if the arg was passed through as empty, in which case the default value an empty array.
    if existing_ids is None:
        global default_used_ids
        existing_ids = default_used_ids
    # Generate 8-digit hex strings until a unique value is found
    generated_id = '%08x' % random.randrange(16 ** 8)
    while generated_id in existing_ids:
        generated_id = '%08x' % random.randrange(16 ** 8)
    existing_ids.append(generated_id)
    return generated_id


# Helper function to find an object's class in an array by its name
def get_object_class(object_name, available_objects):
    i = 0
    while i < len(available_objects):
        if object_name == available_objects[i]["name"]:
            return available_objects[i]["class"]
        i += 1
    return


# Variant of the above function that returns the object containing the class
def get_object(object_name, available_objects):
    i = 0
    while i < len(available_objects):
        if object_name == available_objects[i]["name"]:
            return available_objects[i]
        i += 1
    return None


# Helper function that finds a program image's path from its name.
def get_image(path: str):
    file_dir = os.path.dirname(__file__)
    path_to_image = os.path.join(file_dir, 'images', path)
    print("Loaded image", path_to_image)
    return tk.PhotoImage(file=path_to_image)


# Class with property decorators because python is weird and you can't just define getter/setter functions on a var.
class CurrentGate:
    def __init__(self, main_window, available_objects: list):
        self.main_window = main_window
        self.available_objects = available_objects
        self.val = None

    # Getter function
    @property
    def val(self):
        return self._val

    # Setter function
    @val.setter
    def val(self, value):
        if isinstance(value, str):
            if value not in list(map(lambda val: val["name"], self.available_objects)):
                raise Exception("Specified string not a valid object name")
            else:
                self._val = next((x for x in self.available_objects if x["name"] == value), None)
        elif value is None:
            self._val = None
        else:
            raise TypeError("Invalid type given to setter function. Must be string or Nonetype.")
        self.set_active_item()

    # Updates currently highlighted UI widgets in the gates toolbar
    def set_active_item(self):
        for gate_button in self.main_window.gates_frame.objects:
            if self.val is None:
                self.main_window.gates_frame.objects[gate_button].icon.config(bg="white")
            elif gate_button == self.val["name"]:
                self.main_window.gates_frame.objects[gate_button].icon.config(bg="gray")
            else:
                self.main_window.gates_frame.objects[gate_button].icon.config(bg="white")


# Class with property decorators because python is weird and you can't just define getter/setter functions on a var.
class CurrentAction:
    def __init__(self, main_window):
        self.main_window = main_window
        self.options = ["Gates", "Cursor", "Connect", "Erase", "Save", "Open"]
        self.val = None

    # Getter function
    @property
    def val(self):
        return self._val

    # Setter function
    @val.setter
    def val(self, value):
        if value not in self.options and value is not None:
            raise Exception("Invalid action assigned to CurrentAction instance. Must be valid action string or "
                            "nonetype.")
        self._val = value
        self.main_window.currently_selected = None
        self.set_active_item()

    # Update highlighted UI widget in toolbar
    def set_active_item(self):
        for menu_button in self.main_window.menu_frame.buttons:
            if menu_button == self.val:
                self.main_window.menu_frame.buttons[menu_button].config(bg="#666666")
            else:
                self.main_window.menu_frame.buttons[menu_button].config(bg="gray")
