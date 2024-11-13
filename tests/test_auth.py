import pytest
from pytest_mock import MockerFixture

from kispy.auth import KisAuth
from kispy.exceptions import KispyException


@pytest.fixture
def auth_api():
    return KisAuth(
        app_key="app_key",
        secret="app_secret",
        account_no="account_no-01",
        is_real=True,
    )


def _patch_requests(mocker: MockerFixture, status_code: int, json: dict, headers: dict):
    mock_response = mocker.Mock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json
    mock_response.headers = headers

    mocker.patch("requests.request", return_value=mock_response)


def test_auth_get_token(auth_api: KisAuth, mocker: MockerFixture):
    """성공"""
    content = {
        "access_token": "token",
        "access_token_token_expired": "2024-08-06 14:55:16",
        "token_type": "Bearer",
        "expires_in": 86400,
    }
    _patch_requests(mocker, 200, content, {})

    token = auth_api._get_token()

    assert token.access_token == content["access_token"]
    assert token.access_token_token_expired.strftime("%Y-%m-%d %H:%M:%S") == content["access_token_token_expired"]


def test_auth_get_token_invalid_app_key(auth_api: KisAuth, mocker: MockerFixture):
    """
    잘못된 app_key를 사용했을 때 에러를 발생시킨다.
    """
    # given
    content = {"error_description": "유효하지 않은 AppKey입니다.", "error_code": "EGW00103"}
    _patch_requests(mocker, 401, content, {})

    # when
    with pytest.raises(KispyException) as e:
        auth_api._get_token()

    # then
    assert "유효하지 않은 AppKey입니다." in str(e.value)


def test_auth_get_token_invalid_app_secret(auth_api: KisAuth, mocker: MockerFixture):
    """
    잘못된 app_secret를 사용했을 때 에러를 발생시킨다.
    """
    content = {"error_description": "유효하지 않은 AppSecret입니다.", "error_code": "EGW00105"}
    _patch_requests(mocker, 403, content, {})

    with pytest.raises(KispyException) as e:
        auth_api._get_token()

    assert "유효하지 않은 AppSecret입니다." in str(e.value)


def test_auth_get_token_short_interval(auth_api: KisAuth, mocker: MockerFixture):
    """
    너무 자주 토큰을 요청했을 때 에러를 발생시킨다.
    """
    content = {"error_description": "접근토큰 발급 잠시 후 다시 시도하세요(1분당 1회)", "error_code": "EGW00133"}
    _patch_requests(mocker, 403, content, {})

    with pytest.raises(KispyException) as e:
        auth_api._get_token()

    assert "접근토큰 발급 잠시 후 다시 시도하세요(1분당 1회)" in str(e.value)
