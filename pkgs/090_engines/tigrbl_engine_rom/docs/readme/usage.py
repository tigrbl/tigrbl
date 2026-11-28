from tigrbl_engine_rom import build_rom

engine, sessionmaker = build_rom(
    mapping={
        "rows": [
            {"code": "US", "name": "United States"},
            {"code": "CA", "name": "Canada"},
        ],
        "primary_key": "code",
    }
)

session = sessionmaker()
assert session.get_row("CA")["name"] == "Canada"
