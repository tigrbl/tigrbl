import importlib

package = importlib.import_module("tigrbl_engine_s3fs")
assert package.__name__ == "tigrbl_engine_s3fs"
