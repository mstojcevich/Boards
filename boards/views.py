from flask import render_template, request, redirect
from flask.ext.user import login_required, current_user

from sqlalchemy import desc

from boards import database
from boards.application import app
from boards.forms import CreatePostForm, CreateBoardForm
from boards.models import Board, Moderator, Post
from boards.thumbnail import create_thumbnail


@app.route('/b/<board_name>/')
def view_board(board_name):
    board_query = database.session.query(Board).filter(Board.name == board_name)
    if board_query.count() == 1:
        board = board_query.all().pop()
        posts = database.session.query(Post).filter(Post.board_id == board.id).order_by(desc(Post.posted_at)).limit(
            20).all()
        return render_template('board.html', board_name=board_name, board_title=board.title, posts=posts,
                               sidebar_markdown=board.sidebar_markdown)
    else:
        return render_template('error_page.html', error=format('Board "%s" does not exist.' % board_name))


@app.route('/b/<board_name>/post/create/', methods=['GET', 'POST'])
@login_required
def create_post(board_name):
    board_query = database.session.query(Board).filter(Board.name == board_name)
    if board_query.count() == 1:
        board = board_query.all().pop()
        form = CreatePostForm(request.form)
        if request.method == 'POST' and form.validate():
            post = Post(
                title=form.title.data,
                url=form.url.data,
                board_id=board.id,
                user_id=current_user.id
            )
            database.session.add(post)
            database.session.commit()
            from boards.application import thumbnail_create_queue
            thumbnail_create_queue.enqueue_call(
                func=create_thumbnail,
                args=(form.url.data, post.id),
                timeout=5)
            return redirect('/b/' + board_name)
        else:
            board_title = board.title
            return render_template("create_post.html", form=form, board_title=board_title)
    else:
        return render_template('error_page.html', error=format('Board "%s" does not exist.' % board_name))


@app.route('/board/create/', methods=['GET', 'POST'])
@login_required
def create_board():
    form = CreateBoardForm(request.form)
    if request.method == 'POST' and form.validate():
        # TODO check if already exists using a custom wtforms validator
        board = Board(
            name=form.name.data,
            title=form.title.data,
            private=form.private.data
        )
        database.session.add(board)
        database.session.commit()
        database.session.add(
            Moderator(
                board_id=board.id,
                user_id=current_user.id
            )
        )
        database.session.commit()
        return redirect('/b/' + form.name.data)
    return render_template("create_board.html", form=form)
