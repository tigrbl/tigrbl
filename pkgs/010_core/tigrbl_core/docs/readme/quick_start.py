import importlib

module = importlib.import_module("tigrbl_core._spec")
print(module.__name__)
