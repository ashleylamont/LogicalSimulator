import json
import os

import simulation
import utils

print("Loaded ModuleLoader.py")


def load_modules(available_objects):
    root_dir = os.path.dirname(__file__)
    modules_dir = os.path.join(root_dir, 'modules')
    modules = os.listdir(modules_dir)

    loaded_modules = []

    # Fetch all items in ./modules/ folder and iterate through them if they have a module.json file inside the folder.
    for module in modules:
        module_path = os.path.join(modules_dir, module)
        if os.path.isdir(module_path):
            json_file_path = os.path.join(module_path, 'module.json')
            if os.path.isfile(json_file_path):
                # Read data from module.json and module.py, appending available_objects accordingly.
                with open(json_file_path) as f:
                    data = json.load(f)
                print("==========================================")
                print(">> Loading Module", data["module_name"])
                loaded_modules.append(data["safe_name"])
                print(">> Created by", data["author"])

                module_script = __import__("modules.%s.module" % module, fromlist=["modules.%s" % module])

                for module_object in data["gates"]:
                    print("Found new available_object:", module_object["name"])

                    new_object = {"name": module_object["name"],
                                  "class": create_gate(module_object, module_script, data, module_path),
                                  "tooltip": module_object["tooltip"], "image": module_object["image"],
                                  "package_dir": module_path}
                    available_objects.append(new_object)

                print("==========================================")

    return loaded_modules


# Factory function to create gate classes without causing issues such as setting all gates to the same class.
def create_gate(module_object, module_script, module_data, module_path):
    class Gate(simulation.Object):
        def __init__(self, canvas_objects: dict, position: utils.Vector, connectors: list):
            super().__init__(canvas_objects, position)
            self.name = module_object["name"]
            self.module_name = module_data["safe_name"]
            self.raw_connections = module_object["connections"]
            self.connections = []
            for raw_connection in self.raw_connections:
                connection = simulation.Connection(self, raw_connection["position"],
                                                   raw_connection["name"], raw_connection["conn_type"],
                                                   connectors)
                self.connections.append(connection)

            # Load dependencies using function in utils
            for dependency in module_data["dependencies"]:
                print("Installing module dependency", dependency)
                module = utils.install(dependency)
                self.modules[dependency] = module

            self.size = module_object["size"]
            self.image = module_object["image"]
            self.package_dir = module_path
            self.tooltip = simulation.Tooltip(module_object["tooltip"]["name"],
                                              module_object["tooltip"]["description"],
                                              module_object["tooltip"]["image"])

        calc_function = module_script.mod_exports[module_object["function_name"]]

    return Gate
