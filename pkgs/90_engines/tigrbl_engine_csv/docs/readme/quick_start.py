from pathlib import Path
from tempfile import TemporaryDirectory

from tigrbl_engine_csv import csv_engine

with TemporaryDirectory() as directory:
    path = Path(directory) / "example.csv"
    path.write_text("id,value\n1,3\n2,5\n", encoding="utf-8")
    _, session_factory = csv_engine(mapping={"path": str(path)})
    session = session_factory()
    print(session.query("value > 3").to_dict(orient="records"))
    # [{'id': 2, 'value': 5}]
