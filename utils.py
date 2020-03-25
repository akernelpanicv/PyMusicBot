import re
import os

from app import db
from models import Music

from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename, escape


class SecureMusicCRUD:
    """CRUD secure implementation for music.

    Note: CRUD - Create, Read, Update, Delete."""
    def __init__(self, **kwargs) -> None:
        """
        :param kwargs['url_root']: request.url_root object
        :param kwargs['new_music_title']: title of music

        :var self.media_root: media/ directory
        :var self.media_root_url: absolutely URL to media/ directory
        """
        self.media_root: str = 'media'

        if 'url_root' in kwargs:
            self.media_root_url: str = f'{kwargs["url_root"]}{self.media_root}/'

        if 'new_music_title' in kwargs:
            self.new_music_title = kwargs['new_music_title']

            self.__get_clean_music_title()
            self.__get_correct_music_title()

    def __get_clean_music_title(self) -> None:
        self.new_music_title: str = escape(self.new_music_title)
        self.new_music_title: str = secure_filename(self.new_music_title)

    def __get_correct_music_title(self) -> None:
        if not self.new_music_title:
            self.new_music_title = 'Unknown - Unknown.mp3'

        if not re.search(r'^.+\.mp3$', self.new_music_title):
            self.new_music_title: str = f'{self.new_music_title}.mp3'

    def save_to_dir(self, music_file) -> bool:
        music_file.save(f'{self.media_root}/{self.new_music_title}')

        return True

    def save_to_db(self) -> bool:
        try:
            music = Music(title=self.new_music_title, url=f'{self.media_root_url}{self.new_music_title}')
            db.session.add(music)
            db.session.commit()

            return True
        except SQLAlchemyError:
            return False

    def rename_music_file_in_dir(self, old_music_title) -> bool:
        if os.path.exists(f'{self.media_root}/{old_music_title}'):
            os.rename(f'{self.media_root}/{old_music_title}', f'{self.media_root}/{self.new_music_title}')

            return True
        else:
            return False

    def edit_music_in_db(self, music_id) -> bool:
        try:
            music = Music.query.filter_by(id=music_id).first()
            music.title = self.new_music_title
            music.url = f'{self.media_root_url}{self.new_music_title}'

            db.session.commit()

            return True
        except SQLAlchemyError:
            return False
