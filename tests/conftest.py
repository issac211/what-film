import os
import tempfile

import pytest

import app


@pytest.fixture()
def page_client():
    db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True

    with app.app.test_client() as page_client:
        yield page_client

    os.close(db_fd)
    os.unlink(app.app.config['DATABASE'])


@pytest.fixture(scope="module")
def login_client():
    db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
    app.app.config['TESTING'] = True

    with app.app.test_client() as login_client:
        yield login_client

    os.close(db_fd)
    os.unlink(app.app.config['DATABASE'])