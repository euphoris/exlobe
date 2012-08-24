""":mod:`exlobe.web` --- Web Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import sys

from flask import Flask, redirect, render_template, request, url_for

from .primitives import Idea, Session, User


app = Flask(__name__)


def save_idea(request, parent_id):
    content = request.form['content'].strip()
    session = Session(autocommit=True)
    with session.begin():
        parent = session.query(Idea).filter_by(id=parent_id).one()
        idea = Idea(content=content)
        session.add(idea)
        parent.children.append(idea)

    return session, idea


@app.route('/<int:idea_id>', methods=['POST'])
def post_idea(idea_id):
    save_idea(request, idea_id)
    return redirect(url_for('get_idea', idea_id=idea_id))


@app.route('/', methods=['POST'])
def post_home():
    session = Session()
    parent = session.query(User).first().idea
    save_idea(request, parent.id)
    return redirect(url_for('get_home'))


@app.route('/<int:idea_id>')
def get_idea(idea_id):
    session = Session()
    parent = session.query(Idea).filter_by(id=idea_id).one()
    children = parent.children
    return render_template('home.html', parent=parent, children=children)


@app.route('/')
def get_home():
    session = Session()
    parent = session.query(User).first().idea
    children = parent.children
    return render_template('home.html', parent=parent, children=children)


def main():
    port = int(sys.argv[1])
    app.debug = True
    app.run(port=port)
