import os
import pickle
import tkinter as tk
import tkinter as ttk
from tkinter import filedialog

from PIL import ImageTk, Image
import utils
from simulation import calculate_logic, Connector
from utils import get_image

print("Loaded Interface.py")


# Define the main window class that inherits from the base tkInter Frame widget
class MainWindow(tk.Frame):
    def __init__(self, master, canvas_objects: dict, connectors, modules, available_objects, used_ids):
        super().__init__()
        # Declare self properties from init parameters
        self.connectors = connectors
        self.loaded_modules = modules
        self.used_ids = used_ids
        self.canvas_objects = canvas_objects
        self.available_objects = available_objects
        self.master = master

        # Declare self properties to be overridden by parent script
        self.current_action = None
        self.current_object = None
        self.currently_selected = None

        # Define child widgets as instances of their respective classes
        self.menu_frame = MenuFrame(self)
        self.gates_frame = GatesFrame(self)
        self.canvas_frame = CanvasFrame(self)

        # Default gates_panel state is active
        self.gates_panel = True

    # Function to close/open the gates toolbar
    def toggle_gates(self, e: tk.Event = None):
        if self.gates_panel:
            self.gates_frame.canvas.config(width=0)
            self.gates_frame.scrollbar.config(width=0)
            self.canvas_frame.config(width=799)  # This should be 800, but apparently the scrollbar width is still 1px.
            self.gates_panel = False
            if e is not None:
                self.current_action.val = None
        else:
            self.gates_frame.canvas.config(width=133)
            self.gates_frame.scrollbar.config(width=17)
            self.canvas_frame.config(width=650)
            self.gates_panel = True
            self.current_action.val = "Gates"

    # Function to save the current canvas_objects and connectors to a binary file
    def save_file(self):
        # Prompt the user for a save location and file name
        filename = filedialog.asksaveasfilename(title="Save File", filetypes=[("Logical Simulator files", "*.logisim")])
        if filename != "":
            # Make sure file name has the correct extension
            if not filename.endswith(".logisim"):
                filename += ".logisim"
            # Compile crucial data into a pickle-able object to be dumped into a file
            save_data = {
                "gates": [],
                "connectors": []
            }
            for object_key in self.canvas_objects:
                object_data = self.canvas_objects[object_key]
                object_var = {
                    "position": object_data.position,
                    "name": object_data.name,
                    "module": object_data.module_name,
                    "id": object_key
                }
                save_data["gates"].append(object_var)
            for connector in self.connectors:
                object_var = {
                    "input": {
                        "object_id": connector.input.parent.id,
                        "connection_name": connector.input.name
                    },
                    "output": {
                        "object_id": connector.output.parent.id,
                        "connection_name": connector.output.name
                    }
                }
                save_data["connectors"].append(object_var)
            outfile = open(filename, "wb")
            pickle.dump(save_data, outfile)
            outfile.close()
            print("Saved File to", filename)

    def load_file(self):
        # Prompt user to open an existing save file.
        filename = filedialog.askopenfilename(title="Open Saved File",
                                              filetypes=[("Logical Simulator files", "*.logisim")])
        if filename != "":
            # Ensure file ending has correct extension
            if not filename.endswith(".logisim"):
                filename += ".logisim"
            infile = open(filename, "rb")
            save_data = pickle.load(infile)
            objects_to_delete = []
            for object_key in self.canvas_objects:
                objects_to_delete.append(object_key)
            for object_key in objects_to_delete:
                del self.canvas_objects[object_key]
            connectors_to_delete = []
            for connector in self.connectors:
                connectors_to_delete.append(connector)
            for connector in connectors_to_delete:
                self.connectors.remove(connector)
            ids_to_delete = []
            for used_id in self.used_ids:
                ids_to_delete.append(used_id)
            for used_id in ids_to_delete:
                self.used_ids.remove(used_id)

            infile.close()

            # Load save data into canvas by recreating objects
            for object_data in save_data["gates"]:
                if object_data["module"] not in self.loaded_modules:
                    raise Exception("Missing module from save data:", object_data["module"])
                gate = next((x for x in self.available_objects if x["name"] == object_data["name"]), None)
                new_gate = gate["class"](self.canvas_objects, object_data["position"], self.connectors)
                old_id = new_gate.id
                self.used_ids.remove(new_gate.id)
                new_gate.id = object_data["id"]
                self.canvas_objects[new_gate.id] = new_gate
                del self.canvas_objects[old_id]
                self.used_ids.append(new_gate.id)

            for object_data in save_data["connectors"]:
                gate_in = self.canvas_objects[object_data["input"]["object_id"]]
                connection_in = gate_in.get_connection_by_name(object_data["input"]["connection_name"])
                gate_out = self.canvas_objects[object_data["output"]["object_id"]]
                connection_out = gate_out.get_connection_by_name(object_data["output"]["connection_name"])
                Connector(connection_in, connection_out, self.connectors)
            print("Loaded file from", filename)


# Top toolbar class, inherits from tkinter frame
class MenuFrame(tk.Frame):
    def __init__(self, master: MainWindow):
        super().__init__()
        self.master = master

        self.config(bg="gray")
        self.config(height=64)
        self.config(width=800)

        self.images = {}
        self.buttons = {}

        # Initialise buttons in toolbar
        for button_name in ["Gates", "Cursor", "Connect", "Erase", "Save", "Open"]:
            self.images[button_name] = get_image("icons/" + button_name + ".png")
            self.buttons[button_name] = tk.Button(self, height=64, width=64, relief=tk.FLAT, bg="gray",
                                                  image=self.images[button_name],
                                                  activebackground="black")
            # Array to control alignment of buttons
            left_gates = ["Gates", "Cursor", "Connect", "Erase"]
            self.buttons[button_name].pack(side=tk.LEFT if button_name in left_gates else tk.RIGHT)
            if button_name in left_gates:
                self.buttons[button_name].bind("<Button-1>", self.base_button_function)

        self.buttons["Gates"].bind("<Button-1>", master.toggle_gates)
        self.buttons["Save"].config(command=master.save_file)
        self.buttons["Open"].config(command=master.load_file)

        self.simulation_name = tk.StringVar(self)
        self.simulation_name.set("Logical Simulator")

        self.project_title = tk.Label(self, bg="gray", fg="white", font=("Segoe UI", 20, "bold"),
                                      textvariable=self.simulation_name)
        self.project_title.pack(fill=tk.BOTH, side=tk.BOTTOM, pady=(0, 15))

        self.pack(side=tk.TOP, fill=tk.X, expand=True)

    # Default button interaction to set current action and close gates toolbar
    def base_button_function(self, event):
        button_name = None
        for button in self.buttons:
            if self.buttons[button] == event.widget:
                button_name = button
        event.widget.master.master.current_action.val = button_name
        if event.widget.master.master.gates_panel:
            event.widget.master.master.toggle_gates()


# Class for the gates toolbar. Inherits from tkinter frame
class GatesFrame(ttk.Frame):
    def __init__(self, master: MainWindow):
        super().__init__(bg="white")
        self.master = master

        self.canvas = tk.Canvas(self, bg="white")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.config(bg="white")

        # Scrollbar function
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.config(width=133)
        self.canvas.config(height=600)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.pack(side=tk.LEFT)

        self.objects = {}

    # Add gate to gates toolbar
    def new_item(self, item: dict, current_object: utils.CurrentGate):
        new_frame = tk.Frame(self.scrollable_frame, bg="white")
        new_frame.data = item
        new_frame.current_object = current_object
        new_frame.photo = tk.PhotoImage(
            file=os.path.join(item["package_dir"], "images", item["image"]))
        new_frame.photo = new_frame.photo.subsample(8, 8)
        new_frame.icon = ttk.Label(new_frame, image=new_frame.photo, bg="white")
        new_frame.icon.pack(anchor=tk.W, fill=tk.X)
        new_frame.icon.bind("<Button-3>", show_tooltip)
        new_frame.icon.bind("<Button-1>", select_item)
        new_frame.pack()
        self.objects[item["name"]] = new_frame
        self.pack()


# Select item in gates toolbar
def select_item(event):
    data = event.widget.master.data
    current_gate = event.widget.master.current_object
    current_gate.val = data["name"]


# Show info popup in gates toolbar
def show_tooltip(event):
    data = event.widget.master.data
    popup = tk.Toplevel()
    popup.wm_title(data["tooltip"]["name"])
    title = ttk.Label(popup, text=data["tooltip"]["name"], font="Helvetica 12 bold")
    title.pack(side="top", fill="x", pady=10)
    description = ttk.Label(popup, text=data["tooltip"]["description"], font="Helvetica 10")
    description.pack(side="top", fill="x", pady=10, padx=10)
    print("Loaded tooltip image", os.path.join(data["package_dir"], "images", data["tooltip"]["image"]))
    photo = ttk.PhotoImage(file=os.path.join(data["package_dir"], "images", data["tooltip"]["image"]))
    photo = photo.subsample(7, 7)
    icon = ttk.Label(popup, image=photo)
    icon.pack(anchor=tk.W, fill=tk.X)
    button = ttk.Button(popup, text="Okay", command=popup.destroy)
    button.pack(side="bottom", fill="x", pady=10, padx=10)
    popup.mainloop()


# Main canvas/work area. Inherits from tkinter canvas class.
class CanvasFrame(tk.Canvas):
    def __init__(self, master: MainWindow):
        super().__init__()
        self.master = master

        self.config(height=600)
        self.config(width=650)

        self.frame = 0

        self.images = {}

        self.bind("<Button-1>", self.canvas_interaction)
        self.bind("<Button-3>", self.canvas_alt_interaction)

        self.pack(side=tk.RIGHT)

    # Function called whenever a user left clicks on the canvas
    # noinspection DuplicatedCode
    def canvas_interaction(self, event):
        # Places a gate if there is one selected
        if self.master.current_action.val == "Gates" and self.master.current_object.val is not None:
            self.master.current_object.val["class"](self.master.canvas_objects, [event.x, event.y],
                                                    self.master.connectors)
            self.master.current_object.val = None
        # Erases a gate if erase tool is selected and a gate is under the cursor
        elif self.master.current_action.val == "Erase":
            items_to_delete = []
            for object_key in self.master.canvas_objects:
                object_data = self.master.canvas_objects[object_key]
                object_min_x = object_data.position[0]
                object_min_y = object_data.position[1]
                object_max_x = object_min_x + object_data.size[0]
                object_max_y = object_min_y + object_data.size[1]
                if object_min_x < event.x < object_max_x and object_min_y < event.y < object_max_y:
                    items_to_delete.append(object_key)
                    connectors_to_delete = []
                    for connector in self.master.connectors:
                        if connector.input.parent == object_data or connector.output.parent == object_data:
                            connectors_to_delete.append(connector)
                    for connector in connectors_to_delete:
                        self.master.connectors.remove(connector)
            if len(items_to_delete) > 0:
                self.master.current_action.val = None
            for object_key in items_to_delete:
                del self.master.canvas_objects[object_key]
        # Selects and moves a gate if select tool is active and a gate is under the cursor or selected.
        elif self.master.current_action.val == "Cursor":
            if self.master.currently_selected is None:
                for object_key in self.master.canvas_objects:
                    object_data = self.master.canvas_objects[object_key]
                    object_min_x = object_data.position[0]
                    object_min_y = object_data.position[1]
                    object_max_x = object_min_x + object_data.size[0]
                    object_max_y = object_min_y + object_data.size[1]
                    if object_min_x < event.x < object_max_x and object_min_y < event.y < object_max_y:
                        self.master.currently_selected = object_key
                        break
            else:
                self.master.canvas_objects[self.master.currently_selected].position = [event.x, event.y]
                self.master.currently_selected = None
                self.master.current_action.val = None
        # Selects and connects two connection points on gates
        elif self.master.current_action.val == "Connect":
            if self.master.currently_selected is None:
                for object_key in self.master.canvas_objects:
                    object_data = self.master.canvas_objects[object_key]
                    object_min_x = object_data.position[0]
                    object_min_y = object_data.position[1]
                    object_max_x = object_min_x + object_data.size[0]
                    object_max_y = object_min_y + object_data.size[1]
                    if object_min_x < event.x < object_max_x and object_min_y < event.y < object_max_y:
                        nearby_connections = {}
                        for connection in object_data.connections:
                            nearby_connections[connection] = ((abs((connection.parent.position[0] +
                                                                    connection.parent.size[0] / 2 +
                                                                    connection.position[0]) - event.x)) ** 2
                                                              + (abs((connection.parent.position[1] +
                                                                      connection.parent.size[1] / 2 +
                                                                      connection.position[1]) - event.y)) ** 2) ** 0.5
                        lowest = 999999999999999999  # Large number to be overridden as program finds gate with lowest
                        # distance to cursor.
                        lowest_connection = None
                        for connection in nearby_connections:
                            if nearby_connections[connection] < lowest:
                                lowest = nearby_connections[connection]
                                lowest_connection = connection
                        self.master.currently_selected = lowest_connection
            else:
                for object_key in self.master.canvas_objects:
                    object_data = self.master.canvas_objects[object_key]
                    object_min_x = object_data.position[0]
                    object_min_y = object_data.position[1]
                    object_max_x = object_min_x + object_data.size[0]
                    object_max_y = object_min_y + object_data.size[1]
                    if object_min_x < event.x < object_max_x and object_min_y < event.y < object_max_y:
                        nearby_connections = {}
                        for connection in object_data.connections:
                            nearby_connections[connection] = ((abs((connection.parent.position[0] +
                                                                    connection.parent.size[0] / 2 +
                                                                    connection.position[0]) - event.x)) ** 2
                                                              + (abs((connection.parent.position[1] +
                                                                      connection.parent.size[1] / 2 +
                                                                      connection.position[1]) - event.y)) ** 2) ** 0.5
                        lowest = 999999999999999999  # Large number to be overridden as program finds gate with lowest
                        # distance to cursor.
                        lowest_connection = None
                        for connection in nearby_connections:
                            if nearby_connections[connection] < lowest:
                                lowest = nearby_connections[connection]
                                lowest_connection = connection
                        # Prevent connecting gates to themselves
                        if self.master.currently_selected.parent == lowest_connection.parent:
                            self.master.currently_selected = None
                            self.master.current_action.val = None
                            raise Exception("Tried to connect a gate to itself. Stopped connection to prevent crashes.")
                        # Prevent connecting inputs to inputs and outputs to outputs.
                        elif self.master.currently_selected.conn_type == lowest_connection.conn_type:
                            self.master.currently_selected = None
                            self.master.current_action.val = None
                            raise Exception("Tried to connect an input/output to another input/output respectively. "
                                            "Doesn't make sense.")
                        # Enforce connection order as input->output
                        elif self.master.currently_selected.conn_type == "Input":
                            Connector(lowest_connection, self.master.currently_selected, self.master.connectors)
                        else:
                            Connector(self.master.currently_selected, lowest_connection, self.master.connectors)
                        self.master.currently_selected = None
                        self.master.current_action.val = None

    # Function for user right clicking on canvas
    def canvas_alt_interaction(self, event):
        # Clear connections from object
        if self.master.current_action.val == "Erase":
            items_affected = False
            for object_key in self.master.canvas_objects:
                object_data = self.master.canvas_objects[object_key]
                object_min_x = object_data.position[0]
                object_min_y = object_data.position[1]
                object_max_x = object_min_x + object_data.size[0]
                object_max_y = object_min_y + object_data.size[1]
                if object_min_x < event.x < object_max_x and object_min_y < event.y < object_max_y:
                    connectors_to_delete = []
                    items_affected = True
                    for connector in self.master.connectors:
                        if connector.input.parent == object_data or connector.output.parent == object_data:
                            connectors_to_delete.append(connector)
                    for connector in connectors_to_delete:
                        self.master.connectors.remove(connector)
            if items_affected:
                self.master.current_action.val = None

    # noinspection DuplicatedCode
    # Animation subroutine to generate a new frame
    def animate_frame(self):
        self.delete("all")
        self.frame += 1  # Frame counter for flashes
        calculate_logic(self.master.canvas_objects)  # Calculate circuit logic and states
        # Draw gates on canvas
        for object_key in self.master.canvas_objects:
            object_data = self.master.canvas_objects[object_key]
            if object_key not in self.images:
                print("Loading object image:", os.path.join(object_data.package_dir, "images", object_data.image))
                img = Image.open(os.path.join(object_data.package_dir, "images", object_data.image))
                img = img.resize((object_data.size[0], object_data.size[1]), resample=Image.LANCZOS)
                img = ImageTk.PhotoImage(img)
                self.images[object_key] = img
            self.create_image(object_data.position[0], object_data.position[1],
                              anchor=tk.NW, image=self.images[object_key])
            # Draw green/red rectangle around gate to indicate on/off state
            self.create_rectangle(
                object_data.position[0],
                object_data.position[1],
                object_data.position[0] + object_data.size[0],
                object_data.position[1] + object_data.size[1],
                dash=[2, 2],
                outline="green" if object_data.cached_state else "red"
            )

            # Draw blinking black rectangle around selected gates with 0.5s interval.
            if object_key == self.master.currently_selected and self.frame % 60 > 30:
                self.create_rectangle(
                    object_data.position[0] - 2,
                    object_data.position[1] - 2,
                    object_data.position[0] + object_data.size[0] + 2,
                    object_data.position[1] + object_data.size[1] + 2,
                    outline="gray"
                )

        # Draw connections on canvas
        for connector in self.master.connectors:
            pos_start = [connector.input.position[0] + connector.input.parent.position[0]
                         + connector.input.parent.size[0] / 2,
                         connector.input.position[1] + connector.input.parent.position[1]
                         + connector.input.parent.size[1] / 2]
            pos_end = [connector.output.position[0] + connector.output.parent.position[0]
                       + connector.output.parent.size[0] / 2,
                       connector.output.position[1] + connector.output.parent.position[1]
                       + connector.output.parent.size[1] / 2]

            # Color line green if carrying on signal, else red.
            self.create_line(pos_start[0], pos_start[1], pos_end[0], pos_end[1],
                             fill="green" if connector.input.parent.cached_state else "red", width=2, smooth=True)

        # Draw new frame after 15ms. Results in approximately 60fps animation.
        self.after(15, self.animate_frame)
