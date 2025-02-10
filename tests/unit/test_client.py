import pytest
from inferra import InferraClient, InferraAPIError, InferraAuthenticationError

def test_client_initialization(test_api_key):
    client = InferraClient(api_key=test_api_key)
    assert client.config.api_key == test_api_key
    assert client.config.base_url == "https://api.inferra.net/v1"
    assert client.config.timeout == 60.0

def test_client_missing_api_key():
    with pytest.raises(ValueError, match="API key must be provided"):
        InferraClient()

@pytest.mark.asyncio
async def test_client_authentication_error(client, mocker):
    mock_response = mocker.Mock()
    mock_response.status = 401
    
    mocker.patch("aiohttp.ClientSession.request", return_value=mock_response)
    
    with pytest.raises(InferraAuthenticationError):
        await client.get("/test")

@pytest.mark.asyncio
async def test_client_rate_limit_error(client, mocker):
    mock_response = mocker.Mock()
    mock_response.status = 429
    mock_response.headers = {"Retry-After": "30"}
    
    mocker.patch("aiohttp.ClientSession.request", return_value=mock_response)
    
    with pytest.raises(InferraAPIError, match="Rate limit exceeded"):
        await client.get("/test")
