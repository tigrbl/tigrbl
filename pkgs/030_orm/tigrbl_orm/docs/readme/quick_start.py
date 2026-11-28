import importlib

module = importlib.import_module("tigrbl_orm.orm")
print(module.__name__)
