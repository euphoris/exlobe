""":mod:`exlobe.web` --- Web Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import sys

from flask import Flask, redirect, render_template, request, url_for

from .primitives import Idea, Page


app = Flask(__name__)


@app.route('/page', methods=['GET'])
def get_page_list():
    pages = Page.list()
    return render_template('page_list.html', pages=pages)


@app.route('/page', methods=['POST'])
def new_page():
    page = Page.new()
    return redirect(url_for('get_page', page_id=page.id))


@app.route('/page/<int:page_id>/title', methods=['POST'])
def page_title(page_id):
    title = request.form['title'].strip()
    Page.reset_title(page_id, title)
    return title


@app.route('/page/<int:page_id>', methods=['GET'])
def get_page(page_id):
    page = Page.get(page_id)
    page_list = Page.list()
    return render_template('page.html', page_id=page_id, pages=[page],
        page_list=page_list)


@app.route('/page/<int:page1_id>/<int:page2_id>', methods=['GET'])
def get_pages(page1_id, page2_id):
    page1 = Page.get(page1_id)
    page2 = Page.get(page2_id)
    return render_template('page.html', pages=[page1, page2])


@app.route('/page/<int:page_id>', methods=['POST'])
def new_idea(page_id):
    content = request.form['content'].strip()
    Idea.new(page_id, content)
    return redirect(url_for('get_page', page_id=page_id))


@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('get_page_list'))


def main():
    port = int(sys.argv[1])
    app.debug = True
    app.run(port=port)
