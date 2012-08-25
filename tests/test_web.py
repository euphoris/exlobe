from tempfile import NamedTemporaryFile

from flask import url_for

from exlobe.primitives import Idea, Page
from exlobe.web import create_app, valid_tree

HTTP_OK = 200
HTTP_REDIRECT = 302

class TestBase(object):
    def setup_method(self, method):
        self.f = NamedTemporaryFile()
        uri = 'sqlite:///' + self.f.name
        self.app = create_app(uri)
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def teardown_method(self, method):
        self.ctx.pop()
        self.f.close()

    def get(self, view_func, **kwargs):
        return self.client.get(url_for(view_func, **kwargs))

    def post(self, view_func, **kwargs):
        if 'data' in kwargs:
            data = kwargs['data']
            del kwargs['data']
        else:
            data = {}
        return self.client.post(url_for(view_func, **kwargs), data=data)


class TestGet(TestBase):
    def setup_method(self, method):
        super(TestGet, self).setup_method(method)
        Page.new()
        Page.new()

    def test_get_page_list(self):
        rv = self.get('get_page_list')
        assert rv.status_code == HTTP_OK

    def test_new_page(self):
        before = Page.count()
        rv = self.post('new_page')
        after = Page.count()

        assert rv.status_code == HTTP_REDIRECT
        assert before + 1 == after

    def test_page_title(self):
        title = 'new_title'
        rv = self.post('page_title', data=dict(title=title), page_id=1)
        assert rv.status_code == HTTP_OK
        assert rv.data == title
        assert Page.get(1).title == title

    def test_save_page(self):
        struct = '1 [ 2 ] 3 [ 4 [ 5 6 ] ]'
        rv = self.post('save_page', data=dict(struct=struct), page_id=1)
        assert rv.status_code == HTTP_OK
        assert Page.get(1).struct == struct

        # malformed
        rv = self.post('save_page', data=dict(struct=struct[:-1]), page_id=1)
        assert rv.status_code == HTTP_OK
        assert Page.get(1).struct == struct

        # invalid token
        rv = self.post('save_page', data=dict(struct='hello world'), page_id=1)
        assert rv.status_code == HTTP_OK
        assert Page.get(1).struct == struct

    def test_get_page(self):
        rv = self.get('get_page', page_id=1)
        assert rv.status_code == HTTP_OK

    def test_get_pages(self):
        rv = self.get('get_pages', page1_id=1, page2_id=2)
        assert rv.status_code == HTTP_OK

    def test_new_idea(self):
        content = 'hello world'
        rv = self.post('new_idea', page_id=1, data=dict(content=content))
        assert rv.status_code == HTTP_REDIRECT
        assert Idea.count() == 1

    def test_home(self):
        rv = self.get('home')
        assert rv.status_code == HTTP_REDIRECT
        assert rv.headers['location'].endswith('/page')


def test_valid_tree():
    assert valid_tree('1 [ 2 ] 3 [ 4 [ 5 ] ] 6')
