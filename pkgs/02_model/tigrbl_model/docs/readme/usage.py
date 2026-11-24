from tigrbl_model import Field, Model


class Widget(Model):
    name: str
    quantity: int = Field(default=0, ge=0)


widget = Widget.model_validate_json('{"name":"bolt","quantity":2}')
assert widget.model_dump() == {"name": "bolt", "quantity": 2}
assert Widget.model_validate_yaml(widget.model_dump_yaml()) == widget
assert Widget.model_validate_toml(widget.model_dump_toml()) == widget
