""":mod:`exlobe.primitives` --- DB Tables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sqlalchemy import create_engine, desc, Column
from sqlalchemy.types import Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.schema import ForeignKey, Table


__all__ = ('Idea', 'Session', 'User')


Base = declarative_base()
engine = create_engine('sqlite:///db.sql', echo=True)
Session = sessionmaker(bind=engine)


association_table = Table('association', Base.metadata,
    Column('parent_id', Integer, ForeignKey('idea.id')),
    Column('child_id', Integer, ForeignKey('idea.id'))
)


class Idea(Base):
    __tablename__ = 'idea'

    id = Column(Integer, primary_key=True)
    content = Column(String)
    children = relationship("Idea",
                        secondary=association_table,
                        primaryjoin=id==association_table.c.parent_id,
                        secondaryjoin=id==association_table.c.child_id,
                        backref="parents",
                        order_by=desc('idea.id'))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey(Idea.id))
    idea = relationship(Idea)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    session = Session(autocommit=True)

    with session.begin():
        idea = Idea(content='')
        session.add(idea)

    with session.begin():
        user = User(idea=idea)
        session.add(user)
