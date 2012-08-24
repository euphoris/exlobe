""":mod:`exlobe.primitives` --- DB Tables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sqlalchemy import create_engine, Column
from sqlalchemy.types import Integer, String, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.schema import ForeignKey, Table


__all__ = ('Idea', 'Page', 'Session')


Base = declarative_base()
engine = create_engine('sqlite:///db.sql', echo=True)
Session = sessionmaker(bind=engine)


association_table = Table('association', Base.metadata,
    Column('page_id', Integer, ForeignKey('page.id')),
    Column('idea_id', Integer, ForeignKey('idea.id'))
)


class Idea(Base):
    __tablename__ = 'idea'

    id = Column(Integer, primary_key=True)
    content = Column(String)
    reference_count = Column(Integer)

    @classmethod
    def new(cls, page_id, content):
        session = Session(autocommit=True)
        with session.begin():
            page = Page.get(page_id, session)
            idea = Idea(content=content, reference_count=1)
            session.add(idea)
            page.ideas.append(idea)


class Page(Base):
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
        page = Page(title='(no title)', struct='[]')
        session.add(page)
        session.commit()
        return page

    @classmethod
    def get(cls, page_id, session=None):
        if not session:
            session = Session()
        page = session.query(Page).filter_by(id=page_id).one()
        page.ideas
        return page

    @classmethod
    def list(cls):
        session = Session()
        return session.query(Page)

    @classmethod
    def reset_title(cls, page_id, title):
        session = Session()
        session.query(Page).filter_by(id=page_id).update({'title': title})
        session.commit()

    @classmethod
    def delete(cls, page_id):
        session = Session()
        page = session.query(Page).filter_by(id=page_id).one()

        # delete orphaned ideas
        for idea in page.ideas:
            if idea.reference_count <= 1:
                session.delete(idea)

        session.delete(page)
        session.commit()


if __name__ == '__main__':
    Base.metadata.create_all(engine)
