import pytest


@pytest.mark.pages
def test_home_page(page_client):
    rav = page_client.get('/')
    assert rav.status_code == 200
    assert b'login' in rav.data


@pytest.mark.pages
def test_search(page_client):
    rv = page_client.get('/search/?film-title=matrix&page=1')
    rv2 = page_client.get('/search/?film-title=&page=1')
    assert rv.status_code == 200
    assert b'matrix' in rv.data
    assert b'Movies Found' in rv.data
    assert b'Try writing the name of the movie you want to search for' in rv2.data


@pytest.mark.pages
def test_film_details(page_client):
    rv = page_client.get('/The Matrix/')
    assert rv.status_code == 200
    assert b'The Matrix' in rv.data
    assert b'Plot' in rv.data


@pytest.mark.pages
def test_login(page_client):
    rv = page_client.get('/login/')
    assert rv.status_code == 200
    assert b'Login' in rv.data


@pytest.mark.pages
def test_register(page_client):
    rv = page_client.get('/register/')
    assert rv.status_code == 200
    assert b'Register' in rv.data


@pytest.mark.pages
def test_log_out_page(page_client):
    rv = page_client.get('/log-out/', follow_redirects=True)
    print(rv)
    assert rv.status_code == 200
    assert b'to Home' in rv.data


@pytest.mark.pages
def test_del_user(page_client):
    rv = page_client.get('/delete-user/', follow_redirects=True)
    assert rv.status_code == 200
    assert b'to Home' in rv.data


@pytest.mark.pages
def test_fav_page(page_client):
    rv = page_client.get('/favorites/', follow_redirects=True)
    assert rv.status_code == 200
    assert b'to Home' in rv.data


@pytest.mark.pages
def test_change_password(page_client):
    rv = page_client.get('/change-password/', follow_redirects=True)
    assert rv.status_code == 200
    assert b'to Home' in rv.data