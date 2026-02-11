import requests

class AuthExpired(Exception):
    """Raised when access token is expired / blacklisted"""
    pass


class ApiError(Exception):
    """Raised for network / invalid API responses"""
    pass


def api_call(
    stdscr,
    method,
    url,
    headers=None,
    params=None,
    json=None,
    files=None,
    message="Loading..."
):
    """
    Centralized API caller.
    ALWAYS returns dict OR raises exception.
    """

    # Simple loader screen
    if stdscr:
        stdscr.clear()
        stdscr.addstr(5, 4, message)
        stdscr.addstr(7, 6, "Please wait...")
        stdscr.refresh()

    try:
        res = requests.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json,
            files=files,
            verify=False,
            timeout=20
        )
    except Exception as e:
        raise ApiError(f"Network error: {e}")

    # 🔒 Auth expired
    if res.status_code in (401, 403):
        raise AuthExpired("Session expired")

    # ❌ Empty response
    if not res.text:
        raise ApiError("Empty response from server")

    # ❌ Non-JSON response
    try:
        data = res.json()
    except Exception:
        raise ApiError("Server returned non-JSON response")

    if not isinstance(data, dict):
        raise ApiError("Invalid response structure")

    return data
