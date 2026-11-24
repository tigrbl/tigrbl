import httpx

from tigrbl_client._crud import CRUDMixin


class DummyClient(CRUDMixin):
    pass


def test_process_response_empty_body_returns_none():
    client = DummyClient()
    request = httpx.Request("GET", "http://example.com/empty")
    response = httpx.Response(200, content=b"", request=request)
    assert client._process_response(response) is None


def test_process_response_plain_text_returns_raw_text():
    client = DummyClient()
    request = httpx.Request("GET", "http://example.com/text")
    response = httpx.Response(200, text="plain text", request=request)
    assert client._process_response(response) == "plain text"


def test_process_response_204_with_status_code_returns_none_and_status():
    client = DummyClient()
    request = httpx.Request("DELETE", "http://example.com/items/1")
    response = httpx.Response(204, request=request)
    assert client._process_response(response, status_code=True) == (None, 204)
