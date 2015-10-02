from os import getenv
from flask import Flask

from flask.ext.assets import Environment, Bundle
from flask.ext.markdown import Markdown
from webassets.filter import get_filter
from flask.ext.user import SQLAlchemyAdapter, UserManager

from redis import Redis
from rq import Queue

from boards.database import init_db
from boards import database
from boards.models import User

app = Flask(__name__)
from boards import views

app.jinja_env.add_extension('boards.jinja2htmlcompress.HTMLCompress')

app.secret_key = getenv('BOARDS_SECRET_KEY', 'changeMe')

app.config['SASS_STYLE'] = 'compressed'
app.config['USER_SEND_REGISTERED_EMAIL'] = False

Markdown(app)

# load/compile assets
assets = Environment(app)
assets.url = app.static_url_path
# stylesheets
sass_filter = get_filter('sass', as_output=True, load_paths='static/stylesheets')
sass = Bundle('stylesheets/main.sass', filters=(sass_filter,), output='all.css')
assets.register('sass_packed', sass)
# scripts
sass = Bundle('scripts/main.coffee', filters=("coffeescript", "closure_js"), output='all.js')
assets.register('js_packed', sass)

# Setup database
init_db()
# Setup Flask-User
db_adapter = SQLAlchemyAdapter(database, User)
user_manager = UserManager(db_adapter, app)

thumbnail_create_queue = Queue(connection=Redis())


@app.teardown_appcontext
def shutdown_session(exception=None):
    database.session.remove()


if __name__ == '__main__':
    app.run()
