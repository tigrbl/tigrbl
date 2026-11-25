from tigrbl_concrete._concrete._callback import Callback


def DefineCallback(**kwargs):
    """Declare callback behavior for a model operation."""
    return Callback(**kwargs)


__all__ = ["DefineCallback"]
