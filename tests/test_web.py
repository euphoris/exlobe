from tempfile import NamedTemporaryFile

from flask import url_for

from exlobe.primitives import Idea, Page, Session
from exlobe.web import create_app, struct_to_set, valid_tree

HTTP_OK = 200
HTTP_REDIRECT = 302

class TestBase(object):
    def setup_method(self, method):
        self.f = NamedTemporaryFile()
        uri = 'sqlite:///' + self.f.name
        self.app = create_app(uri, echo=False)
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
        Idea.new(1, 'hello')
        Idea.new(2, 'hello')
        Idea.new(2, 'hello')
        Idea.new(2, 'hello')

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
        page = Page.get(1)
        assert page.struct == '1 '
        assert struct_to_set(page.struct) == set([1])

        struct = '2 [ 3 [ 4 ] ] '
        rv = self.post('save_page', data=dict(struct=struct), page_id=1)
        assert rv.status_code == HTTP_OK

        assert struct_to_set(struct) == set([2,3,4])
        assert Page.get(1).struct == struct

        session = Session()
        assert session.query(Idea).get(1).reference_count == 0
        assert session.query(Idea).get(2).reference_count == 2

        # malformed
        rv = self.post('save_page', data=dict(struct=struct[:-2]), page_id=1)
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
        before = Idea.count()
        rv = self.post('new_idea', page_id=1, data=dict(content=content))
        after = Idea.count()
        assert rv.status_code == HTTP_OK
        assert before + 1 == after

    def test_remove_idea(self):
        rv = self.post('save_page', page_id=1, data=dict(struct=''))

        assert rv.status_code == HTTP_OK
        assert Idea.get(1).reference_count == 0

    def test_list_garbage(self):
        rv = self.get('list_garbage')
        assert rv.status_code == HTTP_OK

    def test_clear_garbage(self):
        session = Session()
        with session.begin():
            idea = Idea(content='', reference_count=0)
            session.add(idea)
        count = session.query(Idea).filter_by(reference_count=0).count()
        assert count > 0

        rv = self.post('clear_garbage')
        assert rv.status_code == HTTP_REDIRECT

        session = Session()
        count = session.query(Idea).filter_by(reference_count=0).count()
        assert count == 0

    def test_home(self):
        rv = self.get('home')
        assert rv.status_code == HTTP_REDIRECT
        assert rv.headers['location'].endswith('/page')


def test_valid_tree():
    assert valid_tree('1 [ 2 ] 3 [ 4 [ 5 ] ] 6')
