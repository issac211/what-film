import pytest
import app


def login(login_client, username, password):
    return login_client.post('/login/', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)


def register(login_client, username, password):
    return login_client.post('/register/',
    data={
        "username_r": username,
        "password_r": password
    },
        follow_redirects=True)


def logout(login_client):
    return login_client.post(
        '/log-out/',
        content_type='multipart/form-data',
        data={"log-out": "1"},
        follow_redirects=True,
    )


def delete_user(login_client, password):
    return login_client.post('/delete-user/',
    content_type='multipart/form-data',
    data={"password_d": password},
    follow_redirects=True,
    )


def change_password(login_client, c_password, n_password):
    return login_client.post('/change-password/',
    content_type='multipart/form-data',
    data={
        "c_password": c_password,
        "n_password": n_password
    },
    follow_redirects=True,
    )


def add_rem_test_movie(login_client, addres, add_rem):
    return login_client.post(addres,
    content_type='multipart/form-data',
    data={
        "fav_title": "test title",
        "fav_poster": "N/A",
        "fav_type": "test_movie",
        "fav_year": "0000",
        "add_rem": add_rem,
    },
    follow_redirects=True,
    )


@pytest.mark.logged_user
def test_register(login_client):
    rv = register(login_client, "itzik", "12345")
    assert b'user name already exists' in rv.data
    rv = register(login_client, "test", "test")
    assert b'Username must not be inside the password' in rv.data
    rv = register(login_client, "test", "12345")
    assert b'Welcome test!!' in rv.data


@pytest.mark.logged_user
def test_log_out_page(login_client):
    rv = login_client.get('/log-out/')
    assert b'are you sure you want to log out?' in rv.data
    rv = logout(login_client)
    assert b'you have logged out' in rv.data


@pytest.mark.logged_user
def test_login(login_client):
    rv = login_client.get('/')
    assert b'Favorites' not in rv.data
    rv = login(login_client, "", "")
    assert b'username and password need to be entered' in rv.data
    rv = login(login_client, "test", "test")
    assert b'Incorrect username or password' in rv.data
    rv = login(login_client, "test", "12345")
    assert b'Login successfully!!' in rv.data
    rv = login_client.get('/')
    assert b'hii test :->' in rv.data


@pytest.mark.logged_user
def test_log_favorits(login_client):
    rv = login_client.get('/favorites/')
    print(rv)
    assert b'Favorite movies' in rv.data


@pytest.mark.logged_user
def test_log_top_movies(login_client):
    rv = login_client.get('/top-movies/')
    assert b'Top 5 movies' in rv.data


@pytest.mark.logged_user
def test_change_password(login_client):
    rv =  change_password(login_client, "111111", "123456")
    assert b'Incorrect password' in rv.data
    rv =  change_password(login_client, "12345", "123456")
    assert b'Password changed' in rv.data



@pytest.mark.logged_user
def test_search_add_rem(login_client):
    addres = "/search/?film-title=test&page=1"
    rv = add_rem_test_movie(login_client, addres, "add")
    assert b'movie added to your favorites' in rv.data
    rv = add_rem_test_movie(login_client, addres, "rem")
    assert b'Movie deleted from favorites' in rv.data
    rv = add_rem_test_movie(login_client, addres, "non")
    assert b'Unable to add or remove movie to favorites' in rv.data


@pytest.mark.logged_user
def test_film_details_add_rem(login_client):
    addres = "/test film/"
    rv = add_rem_test_movie(login_client, addres, "add")
    assert b'movie added to your favorites' in rv.data
    rv = add_rem_test_movie(login_client, addres, "rem")
    assert b'Movie deleted from favorites' in rv.data
    rv = add_rem_test_movie(login_client, addres, "non")
    assert b'Unable to add or remove movie to favorites' in rv.data



@pytest.mark.logged_user
def test_delete_user(login_client):
    rv =  delete_user(login_client, "12345")
    assert b'Incorrect password' in rv.data
    rv =  delete_user(login_client, "123456")
    assert b'the user test has been deleted' in rv.data