""":mod:`exlobe.web` --- Web Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import sys

from flask import Flask, redirect, render_template, request, url_for

from .primitives import init_db, Idea, Page


class Exlobe(Flask):
    def __init__(self, name, uri):
        super(Exlobe, self).__init__(name)
        self.db_engine = init_db(uri, echo=True)


class Surrogate(object):
    def __init__(self):
        self._route = []
        self._filter = []

    def route(self, url, **kwargs):
        def append(f):
            self._route.append((url, kwargs, f))
            return f
        return append

    def template_filter(self, name, **kwargs):
        def append(f):
            self._filter.append((name, kwargs, f))
            return f
        return append

    def incarnate(self, app):
        for url, kwargs, f in self._route:
            app.route(url, **kwargs)(f)

        for name, kwargs, f in self._filter:
            app.template_filter(name, **kwargs)(f)


srg = Surrogate()


@srg.route('/page', methods=['GET'])
def get_page_list():
    pages = Page.list()
    return render_template('page_list.html', pages=pages)


@srg.route('/page', methods=['POST'])
def new_page():
    page = Page.new()
    return redirect(url_for('get_page', page_id=page.id))


@srg.route('/page/<int:page_id>/title', methods=['POST'])
def page_title(page_id):
    title = request.form['title'].strip()
    Page.update(page_id, dict(title=title))
    return title


def valid_tree(struct):
    depth = 0
    struct = struct.strip().split(' ')
    for s in struct:
        if s == '[':
            depth += 1
        elif s == ']':
            depth -= 1
        else:
            try:
                int(s)
            except ValueError:
                return False
    return depth == 0


@srg.route('/page/<int:page_id>/save', methods=['POST'])
def save_page(page_id):
    struct = request.form['struct']
    if valid_tree(struct):
        Page.update(page_id, dict(struct=struct))
    return 'ok'


@srg.template_filter('render_page')
def render_page(page):
    ideas = {}
    for idea in page.ideas:
        ideas[idea.id] = idea.content

    tree = ''
    struct = page.struct.strip().split()
    for s in struct:
        if s == '[':
            tree += u'<ol>'
        elif s == ']':
            tree += u'</ol>'
        else:
            i = int(s)
            try:
                tree += u'<li id="{}"><div class="idea">{}</div>'\
                    .format(i, ideas[i])
            except KeyError:
                pass
    return tree


@srg.route('/page/<int:page_id>', methods=['GET'])
def get_page(page_id):
    page = Page.get(page_id)
    page_list = Page.list()
    return render_template('page.html', page_id=page_id, pages=[page],
        page_list=page_list)


@srg.route('/page/<int:page1_id>/<int:page2_id>', methods=['GET'])
def get_pages(page1_id, page2_id):
    page1 = Page.get(page1_id)
    page2 = Page.get(page2_id)
    return render_template('page.html', pages=[page1, page2])


@srg.route('/page/<int:page_id>/delete', methods=['POST'])
def delete_page(page_id):
    Page.delete(page_id)
    return redirect(url_for('get_page_list'))


@srg.route('/page/<int:page_id>', methods=['POST'])
def new_idea(page_id):
    content = request.form['content'].strip()
    Idea.new(page_id, content)
    return redirect(url_for('get_page', page_id=page_id))


@srg.route('/', methods=['GET'])
def home():
    return redirect(url_for('get_page_list'))


def create_app(uri):
    app = Exlobe(__name__, uri)
    srg.incarnate(app)
    return app


def main():
    port = int(sys.argv[1])
    app = create_app('sqlite:///db.sql')
    app.debug = True
    app.run(port=port)
