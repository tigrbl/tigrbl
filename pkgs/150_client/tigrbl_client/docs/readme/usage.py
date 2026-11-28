from tigrbl_client import TigrblClient

with TigrblClient("https://api.example.com") as client:
    item = client.get("/items/1")
    created = client.post("/items", data={"name": "example"})
