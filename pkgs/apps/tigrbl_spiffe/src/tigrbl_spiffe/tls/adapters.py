from __future__ import annotations

import httpx
from typing import Any


async def httpx_client_with_tls(base_url: str, tls_helper: Any) -> httpx.AsyncClient:
    """Return an AsyncClient configured with TLS contexts built by tls_helper.

    Client certificate/key installation is owned by the TLS helper so callers can
    supply environment-specific SPIFFE material without coupling this adapter to
    a particular workload API implementation.

    """
    context = await tls_helper.client_context()
    return httpx.AsyncClient(base_url=base_url, timeout=10.0, verify=context)
