import os

import pytest

from kispy.auth import AuthAPI


@pytest.fixture(scope="session")
def auth():
    app_key = os.getenv("KISPY_APP_KEY")
    secret = os.getenv("KISPY_APP_SECRET")
    account_no = os.getenv("KISPY_ACCOUNT_NO")
    assert app_key and secret and account_no, "KISPY_APP_KEY, KISPY_APP_SECRET, KISPY_ACCOUNT_NO must be set"
    return AuthAPI(app_key=app_key, secret=secret, account_no=account_no, is_real=True)
