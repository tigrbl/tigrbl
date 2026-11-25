from tigrbl_concrete.factories.callback import DefineCallback


def callback_ctx(**kwargs):
    """Declare a callback whose decorated function builds the payload."""

    def decorate(builder):
        builder = getattr(builder, "__func__", builder)
        builder.__tigrbl_callback_method__ = True
        return DefineCallback(payload=builder, **kwargs)

    return decorate


__all__ = ["callback_ctx"]
