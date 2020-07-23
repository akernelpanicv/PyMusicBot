from PyMusicBot import db
from PyMusicBot.models import User


def init():
    db.create_all()

    user1 = User(name='user1')
    user1.set_password('very_bad_password')

    db.session.add(user1)
    db.session.commit()


def drop():
    db.drop_all()
