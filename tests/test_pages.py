import pytest


page_info = [
    ('/', b'login'),
    ('/search/?film-title=matrix&page=1', b'matrix'),
    ('/search/?film-title=matrix&page=1', b'Movies Found'),
    ('/search/?film-title=&page=1', b'Try writing the name of the movie you want to search for'),
    ('/The Matrix/', b'The Matrix'),
    ('/The Matrix/', b'Plot'),
    ('/login/', b'Login'),
    ('/register/', b'Register'),
    ('/log-out/', b'to Home'),
    ('/delete-user/', b'to Home'),
    ('/favorites/', b'to Home'),
    ('/change-password/', b'to Home'),
]


@pytest.mark.pages
@pytest.mark.parametrize("page, info", page_info)
def test_page(page_client, page, info):
    rv = page_client.get(page, follow_redirects=True)
    assert rv.status_code == 200
    assert info in rv.data