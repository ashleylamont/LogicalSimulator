import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import moduleloader
import utils

# Attempt to import PIL/Pillow, and prompt the user to auto-install if the module is not present.
try:
    from PIL import ImageTk, Image
except ModuleNotFoundError:
    choice = ""
    while choice not in ["y", "n"]:
        choice = input("You are missing required modules, would you like to install them now? [y/n] ")
    if choice == "n":
        print("Ok, the program will exit now.")
        sys.exit()
    else:
        # Remove PIL, update PIP and install Pillow by calling the python executable.
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "PIL"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "--force-reinstall",
                               "--no-cache-dir", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "--force-reinstall",
                               "--no-cache-dir", "Pillow"])
        from PIL import ImageTk, Image
finally:
    import interface

# Define the global list of used IDs and duplicate the reference to the utils file where IDs are generated.
used_ids = []
utils.default_used_ids = used_ids

# Define the canvas_objects, connectors and available objects variables.
canvas_objects = {}
connectors = []
available_objects = []

# Load in modules
modules = moduleloader.load_modules(available_objects)

# Create main window
root = tk.Tk()
# Fixed width and height
root.resizable(False, False)
# Instantiate the interface module with all of the necessary parameters.
main_window = interface.MainWindow(root, canvas_objects, connectors, modules, available_objects, used_ids)

# Create current_object and current_action variables from respective classes and bind properties in main_window class
current_object = utils.CurrentGate(main_window, available_objects)
current_action = utils.CurrentAction(main_window)
main_window.current_action = current_action
main_window.current_object = current_object

# Begin animation subroutine
main_window.canvas_frame.animate_frame()

# Create buttons in gates toolbar for each object registered by module loader
for available_object in available_objects:
    main_window.gates_frame.new_item(available_object, current_object)
# Hide the gates toolbar
main_window.toggle_gates()
# Show welcome message
messagebox.showinfo(title="Welcome", message="Welcome to Logical Simulator!\nPlease ensure you have read the "
                                             "instructions/manual as there are important things to note when using "
                                             "this program. Also please ensure that you do not create looped connect"
                                             "ions as this will cause the program to repeat indefinitely and crash.")
# Start tkinter event loop
root.mainloop()
