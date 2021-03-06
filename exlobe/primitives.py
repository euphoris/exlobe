""":mod:`exlobe.primitives` --- DB Tables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from flask import current_app
from sqlalchemy import create_engine, Column
from sqlalchemy.types import Boolean, Integer, String, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session, relationship
from sqlalchemy.schema import ForeignKey, Table


__all__ = ('Idea', 'Page', 'Session')


Base = declarative_base()


def Session(**kwargs):
    return create_session(bind=current_app.db_engine, **kwargs)


association_table = Table('association', Base.metadata,
    Column('page_id', Integer, ForeignKey('page.id')),
    Column('idea_id', Integer, ForeignKey('idea.id'))
)


class Managed(object):
    @classmethod
    def get(cls, id):
        session = Session()
        item = session.query(cls).filter_by(id=id).one()
        return item

    @classmethod
    def count(cls):
        session = Session()
        return session.query(cls).count()

    @classmethod
    def update(cls, id, **kwargs):
        session = Session()
        session.begin()
        session.query(cls).filter_by(id=id).update(kwargs)
        session.commit()


class Idea(Base, Managed):
    __tablename__ = 'idea'

    id = Column(Integer, primary_key=True)
    content = Column(String)
    reference_count = Column(Integer, default=1)
    hidden = Column(Boolean, default=False)

    @classmethod
    def new(cls, page_id, content):
        session = Session()
        with session.begin():
            page = session.query(Page).get(page_id)
            idea = Idea(content=content)
            page.ideas.append(idea)

        with session.begin():
            page.struct = '{} {}'.format(idea.id, page.struct)
            session.merge(page)

        return idea


class Page(Base, Managed):
    __tablename__ = 'page'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    struct = Column(TEXT)
    ideas = relationship("Idea",
                        secondary=association_table,
                        backref="pages")

    @classmethod
    def new(cls):
        session = Session()
        with session.begin():
            page = Page(title='(no title)', struct='')
            session.add(page)
        return page

    @classmethod
    def get(cls, page_id):
        session = Session()
        page = session.query(Page).filter_by(id=page_id).one()
        page.ideas
        return page

    @classmethod
    def list(cls):
        session = Session()
        return session.query(Page)

    @classmethod
    def delete(cls, page_id):
        session = Session()
        session.begin()
        page = session.query(Page).filter_by(id=page_id).one()

        for idea in page.ideas:
            idea.reference_count -= 1
            session.merge(idea)

        session.delete(page)
        session.commit()


def init_db(uri, **kwargs):
    engine = create_engine(uri, **kwargs)
    Base.metadata.create_all(engine)
    return engine
