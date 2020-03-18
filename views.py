from app import app
from models import Music

from flask import render_template


@app.route('/')
def auth():
    context = {'page_title': 'Log in'}

    return render_template('auth.html', context=context)


@app.route('/admin/<slug>')
def admin(slug):
    if slug == 'list':
        content_title = 'Music list'
        music_list = Music.query.all()
    else:
        content_title = f'{slug.title()} music'
        music_list = ''

    context = {'page_title': 'Admin Page',
               'content_title': content_title,
               'music_list': music_list}

    return render_template('admin.html', context=context)
