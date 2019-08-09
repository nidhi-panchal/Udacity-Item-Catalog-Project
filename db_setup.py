import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)

    name = Column(String(250), nullable=False)

    email = Column(String(250), nullable=False)

    picture = Column(String(250))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture
        }


class Artist(Base):

    __tablename__ = 'artist'

    style = Column(String(80), nullable=False)

    id = Column(Integer, primary_key=True)

    @property
    def serialize(self):
        return {
            'style': self.style,
            'id': self.id
        }


class Name(Base):

    __tablename__ = 'name'

    name = Column(String(80), nullable=False)

    id = Column(Integer, primary_key=True)

    description = Column(String(250))

    type_id = Column(Integer, ForeignKey('artist.id'))

    artist = relationship(Artist)

    user_id = Column(Integer, ForeignKey('user.id'))

    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'type_id': self.type_id,
            'artist': self.artist.style
        }


engine = create_engine('sqlite:///artists.db')

Base.metadata.create_all(engine)
