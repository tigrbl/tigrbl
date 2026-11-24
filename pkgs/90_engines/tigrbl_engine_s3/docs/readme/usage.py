import importlib

package = importlib.import_module("tigrbl_engine_s3")
assert package.__name__ == "tigrbl_engine_s3"
