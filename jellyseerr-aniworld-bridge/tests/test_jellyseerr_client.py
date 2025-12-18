import httpx
import respx

@respx.mock
def test_get_pending_requests(respx_mock):
    """
    Tests that the Jellyseerr client can successfully fetch pending requests.
    """
    from jellyseerr_aniworld_bridge.jellyseerr_client import JellyseerrClient
    mock_response = {
        "results": [
            {"id": 1, "media": {"name": "Test Show"}}
        ]
    }
    # Match the exact URL with query parameters
    url = "http://localhost:5055/api/v1/request?take=100&skip=0&filter=approved&sort=added"
    respx_mock.get(url).mock(return_value=httpx.Response(200, json=mock_response))

    client = JellyseerrClient(base_url="http://localhost:5055", api_key="test_key")
    requests = client.get_pending_requests()

    assert len(requests) == 1
    assert requests[0]["id"] == 1

@respx.mock
def test_mark_request_as_available(respx_mock):
    """
    Tests that the Jellyseerr client can successfully mark a request as available.
    """
    from jellyseerr_aniworld_bridge.jellyseerr_client import JellyseerrClient
    url = "http://localhost:5055/api/v1/request/1/available"
    respx_mock.post(url).mock(return_value=httpx.Response(200, json={"status": "ok"}))

    client = JellyseerrClient(base_url="http://localhost:5055", api_key="test_key")
    result = client.mark_request_as_available(1)

    assert result is not None
