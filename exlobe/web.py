""":mod:`exlobe.web` --- Web Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import os
import re
import sys

from flask import Flask, redirect, render_template, request, url_for

from .primitives import init_db, Idea, Page, Session


class Exlobe(Flask):
    def __init__(self, name, uri, echo):
        super(Exlobe, self).__init__(name)
        self.db_engine = init_db(uri, echo=echo)


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
    Page.update(page_id, title=title)
    return title


def valid_tree(struct):
    depth = 0

    if struct.strip() == '':
        return True

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


def struct_to_set(struct):
    s = set()

    ideas = struct.strip().split(' ')
    for idea_id in ideas:
        if idea_id not in '[]':
            s.add(int(idea_id))

    return s


@srg.route('/page/<int:page_id>/save', methods=['POST'])
def save_page(page_id):
    struct = request.form['struct']
    if valid_tree(struct):

        session = Session()
        with session.begin():
            page = session.query(Page).get(page_id)

            page_set = struct_to_set(page.struct)
            new_set = struct_to_set(struct)

            removed = page_set - new_set
            for idea_id in removed:
                idea = session.query(Idea).get(idea_id)
                page.ideas.remove(idea)
                idea.reference_count -= 1
                session.merge(idea)

            appended = new_set - page_set
            for idea_id in appended:
                idea = session.query(Idea).get(idea_id)
                page.ideas.append(idea)
                idea.reference_count += 1
                session.merge(idea)

            page.struct = struct
            session.merge(page)

    return 'ok'

idea_format = u"""
    <li id="{}">
        <div class="idea">
            <div class="handle"></div>
            <span class="content">{}</span>
        </div>
"""
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
                tree += idea_format.format(i, ideas[i])
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
    idea_id = Idea.new(page_id, content)
    return idea_format.format(idea_id, content)


paragraph_re = re.compile(r'[\r\n][\r\n]+')
sentence_re = re.compile(r'([^.])[.]\s+')

@srg.route('/page/import', methods=['POST'])
def import_text():
    page = Page.new()
    text = request.form['text']

    struct = ''
    paragraphs = paragraph_re.split(text)

    for p in paragraphs:
        p = re.sub(r'\n', '', p).strip()
        sentences = sentence_re.sub(r'\1.\n', p).split('\n')
        is_first = True
        for s in sentences:
            idea = Idea.new(page.id, s)
            struct += '{} '.format(idea)
            if is_first:
                struct += '[ '
                is_first = False
        struct += '] '

    Page.update(page.id, struct=struct)

    return redirect(url_for('get_page', page_id=page.id))


@srg.route('/idea/<int:idea_id>', methods=['POST'])
def edit_idea(idea_id):
    content = request.form['content'].strip()
    Idea.update(idea_id, content=content)
    return 'ok'


@srg.route('/garbage')
def list_garbage():
    session = Session()
    ideas = session.query(Idea).filter_by(reference_count=0)
    return render_template('garbage.html', ideas=ideas)


@srg.route('/garbage', methods=['POST'])
def clear_garbage():
    session = Session()
    with session.begin():
        session.query(Idea).filter_by(reference_count=0).delete()
    return redirect(url_for('get_page_list'))


@srg.route('/', methods=['GET'])
def home():
    return redirect(url_for('get_page_list'))


def create_app(uri, echo=True):
    app = Exlobe(__name__, uri, echo)
    srg.incarnate(app)
    return app


def main():
    port = int(sys.argv[1])
    db = os.environ['EXLOBE_DATABASE']
    app = create_app(db)
    app.debug = True
    app.run(port=port)
