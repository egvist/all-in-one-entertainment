import pytest
from mediaatlas.api.igdb_client import IGDBClient
import httpx
from unittest.mock import patch


def test_empty_search_title():
    client = IGDBClient("fake_id", "fake_secret")

    with pytest.raises(ValueError):
        client.search_games("")


def test_invalid_page():
    client = IGDBClient("fake_id", "fake_secret")

    with pytest.raises(ValueError):
        client.search_games("Mario", page=0)


def test_invalid_page_size():
    client = IGDBClient("fake_id", "fake_secret")

    with pytest.raises(ValueError):
        client.search_games("Mario", page_size=51)


def test_boolean_page():
    client = IGDBClient("fake_id", "fake_secret")

    with pytest.raises(ValueError):
        client.search_games("Mario", page=True)






def test_search_games_retries_after_401():
    client = IGDBClient("fake_id", "fake_secret")

    request = httpx.Request(
        "POST",
        "https://api.igdb.com/v4/games"
    )

    unauthorized_response = httpx.Response(
        status_code=401,
        request=request
    )

    success_response = httpx.Response(
        status_code=200,
        json=[{"id": 456, "name": "Mario"}],
        request=request
    )

    with patch.object(
        client,
        "_get_access_token",
        side_effect=["old_token", "new_token"]
    ) as mock_token:

        with patch(
            "mediaatlas.api.igdb_client.httpx.Client"
        ) as mock_client_class:

            mock_http = (
                mock_client_class.return_value
                .__enter__.return_value
            )

            # First 401, Second 200
            mock_http.post.side_effect = [
                unauthorized_response,
                success_response
            ]

            games = client.search_games("Mario")

    # 2 Http request must be made
    assert mock_http.post.call_count == 2

    # Token should be called 2 times
    assert mock_token.call_count == 2

    # must be true
    assert len(games) == 1
    assert games[0].title == "Mario"
    assert games[0].external_id == "456"




def test_search_games_fails_after_two_401():
    client = IGDBClient("fake_id", "fake_secret")

    request = httpx.Request(
        "POST",
        "https://api.igdb.com/v4/games"
    )

    unauthorized_response = httpx.Response(
        status_code=401,
        request=request
    )

    with patch.object(
        client,
        "_get_access_token",
        side_effect=["old_token", "new_token"]
    ) as mock_token:

        with patch(
            "mediaatlas.api.igdb_client.httpx.Client"
        ) as mock_client_class:

            mock_http = (
                mock_client_class.return_value
                .__enter__.return_value
            )

            mock_http.post.side_effect = [
                unauthorized_response,
                unauthorized_response
            ]

            with pytest.raises(httpx.HTTPStatusError) as exc:
                client.search_games("Mario")

    assert exc.value.response.status_code == 401
    assert mock_http.post.call_count == 2
    assert mock_token.call_count == 2


def test_search_games_rate_limit():
    client = IGDBClient("fake_id", "fake_secret")

    request = httpx.Request(
        "POST",
        "https://api.igdb.com/v4/games"
    )

    rate_limit_response = httpx.Response(
        status_code=429,
        request=request
    )

    with patch.object(
        client,
        "_get_access_token",
        return_value="fake_token"
    ):
        with patch(
            "mediaatlas.api.igdb_client.httpx.Client"
        ) as mock_client_class:

            mock_http = (
                mock_client_class.return_value
                .__enter__.return_value
            )

            mock_http.post.return_value = rate_limit_response

            with pytest.raises(httpx.HTTPStatusError) as exc:
                client.search_games("Mario")

    assert exc.value.response.status_code == 429
    mock_http.post.assert_called_once()


def test_search_games_timeout():
    client = IGDBClient("fake_id", "fake_secret")

    request = httpx.Request(
        "POST",
        "https://api.igdb.com/v4/games"
    )

    timeout_error = httpx.ReadTimeout(
        "Request timed out",
        request=request
    )

    with patch.object(
        client,
        "_get_access_token",
        return_value="fake_token"
    ):
        with patch(
            "mediaatlas.api.igdb_client.httpx.Client"
        ) as mock_client_class:

            mock_http = (
                mock_client_class.return_value
                .__enter__.return_value
            )

            mock_http.post.side_effect = timeout_error

            with pytest.raises(httpx.ReadTimeout):
                client.search_games("Mario")

    mock_http.post.assert_called_once()


def test_invalidate_access_token():
    client = IGDBClient("fake_id", "fake_secret")

    client._access_token = "old_token"
    client._token_expires_at = 999999999.0

    client._invalidate_access_token()

    assert client._access_token is None
    assert client._token_expires_at == 0.0
