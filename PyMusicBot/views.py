from PyMusicBot import logger
from PyMusicBot.models import Music, User
from PyMusicBot.forms import AddMusicForm, EditMusicForm, DeleteMusicForm, AuthForm
from PyMusicBot.repositories import SQLAlchemyRepository, MediaDirRepository

from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user
from flask.views import View, MethodView

from werkzeug.datastructures import FileStorage
from flask_sqlalchemy import Pagination, BaseQuery
from typing import Union, Dict


class BasePage(MethodView):
    decorators: list = [login_required]
    template: str = ''

    def get(self) -> Union[redirect, render_template]:
        context: dict = self.get_context()
        if 'page_title' not in context:
            context['page_title'] = 'Admin Page'

        return self.render_template(context)

    def post(self) -> Union[None, redirect]:
        pass

    def render_template(self, context) -> render_template:
        return render_template(self.template, **context)

    def get_context(self) -> dict:
        raise NotImplementedError


class Auth(BasePage):
    decorators: list = []
    template: str = 'auth.html'

    def get(self) -> Union[redirect, render_template]:
        if current_user.is_authenticated:
            return redirect(url_for('admin_music_list'))

        return self.render_template(self.get_context())

    def post(self) -> redirect:
        form = AuthForm(request.form)
        if form.validate():
            user = User.query.filter_by(name=request.form['login']).first()
            if user and user.check_password(request.form['password']):
                login_user(user, remember=True)
                return redirect(url_for('admin_music_list'))
            else:
                flash('Incorrect login or password!')

        return redirect(url_for('auth'))

    def get_context(self) -> Dict[str, Union[str, AuthForm]]:
        context: Dict[str, Union[str, AuthForm]] = {'page_title': 'Log in',
                                                    'auth_form': AuthForm()}

        return context


class Logout(View):
    decorators: list = [login_required]

    def dispatch_request(self) -> redirect:
        logout_user()

        return redirect(url_for('auth'))


class MusicList(BasePage):
    decorators = [login_required]
    template = 'music_list.html'

    @staticmethod
    def get_search() -> Union[None, str]:
        return request.args.get('search')

    def get_pages(self) -> Pagination:
        current_page: int = self.get_current_page()
        music_list: BaseQuery = self.get_music_list()

        return music_list.paginate(page=current_page, per_page=10)

    @staticmethod
    def get_current_page() -> int:
        current_page: Union[int, str, None] = request.args.get('page')

        if current_page and current_page.isdigit():
            current_page = int(current_page)
        else:
            current_page = 1

        return current_page

    def get_music_list(self) -> BaseQuery:
        search: Union[None, str] = self.get_search()
        if search:
            return Music.query.filter(Music.title.ilike(f'%{search}%'))
        else:
            return Music.query.order_by(Music.pub_date.desc())

    def get_context(self) -> Dict[str, Union[str, Pagination, None]]:
        context: Dict[str, Union[str, Pagination, None]] = {'content_title': 'Music list',
                                                            'search': self.get_search(),
                                                            'pages': self.get_pages()}

        return context


class AddMusic(BasePage):
    decorators = [login_required]
    template: str = 'add_music.html'

    def post(self) -> redirect:
        form = AddMusicForm(request.files)
        if form.music.data:
            if form.music.data.filename.endswith('.mp3') and form.music.data.mimetype == 'audio/mpeg':
                music_title: str = request.form.get('title', '')
                music_file: FileStorage = request.files.get('music', None)

                if MediaDirRepository().save(music_title, music_file) and SQLAlchemyRepository().save(music_title):
                    return redirect(url_for('admin_music_list'))
                else:
                    logger.warning('Unsuccessful attempt to add music')
                    flash('Something went wrong...')
            else:
                flash('The music file must be .mp3!')

        return redirect(url_for('admin_add_music'))

    def get_context(self) -> Dict[str, Union[str, AddMusicForm]]:
        context: Dict[str, Union[str, AddMusicForm]] = {'content_title': 'Add music',
                                                        'add_music_form': AddMusicForm()}

        return context


class EditMusic(BasePage):
    template: str = 'edit_music.html'

    def post(self) -> Union[redirect, None]:
        form = EditMusicForm(request.form)
        if form.validate():
            try:
                music_id: str = request.form['id']
                music_title: str = request.form['title']
            except AttributeError:
                flash('No music with that ID')
                return redirect(url_for('admin_edit_music'))

            if MediaDirRepository().edit(music_title, music_id) and SQLAlchemyRepository().edit(music_title, music_id):
                return redirect(url_for('admin_music_list'))
            else:
                logger.warning('Unsuccessful attempt to edit music')
                flash('Server error!')
        else:
            flash('Incorrect data!')

        return redirect(url_for('admin_edit_music'))

    def get_context(self) -> Dict[str, Union[str, EditMusicForm]]:
        context: Dict[str, Union[str, EditMusicForm]] = {'content_title': 'Edit music',
                                                         'edit_music_form': EditMusicForm()}

        return context


class DeleteMusic(BasePage):
    template: str = 'delete_music.html'

    def post(self) -> redirect:
        form = DeleteMusicForm(request.form)
        if form.validate():
            try:
                music_id: str = request.form['id']
            except AttributeError:
                flash('No music with that ID')
                return redirect(url_for('admin_delete_music'))

            if MediaDirRepository().delete(music_id) and SQLAlchemyRepository().delete(music_id):
                return redirect(url_for('admin_music_list'))
            else:
                logger.warning('Unsuccessful attempt to delete music')
                flash('Server error!')
        else:
            flash('Incorrect ID!')

        return redirect(url_for('admin_delete_music'))

    def get_context(self) -> Dict[str, Union[str, DeleteMusicForm]]:
        context: Dict[str, Union[str, DeleteMusicForm]] = {'content_title': 'Delete music',
                                                           'delete_music_form': DeleteMusicForm()}

        return context
