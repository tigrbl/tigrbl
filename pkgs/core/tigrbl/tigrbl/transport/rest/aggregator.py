from tigrbl_concrete.transport._deprecation import (
    REST_WARNING,
    warn_deprecated_transport_module,
)
from tigrbl_concrete.transport.rest.aggregator import *  # noqa: F401,F403

warn_deprecated_transport_module(REST_WARNING, __name__)
