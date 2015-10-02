from wtforms import Form, validators
from wtformsparsleyjs import BooleanField, StringField


class CreateBoardForm(Form):
    title = StringField('Title', [validators.length(min=4, max=50)])
    name = StringField('Name', [validators.length(min=4, max=32),
                                validators.regexp('^[\w\d_-]*$',  # Alphanumeric and underscore
                                                  message='Names must only use English letters, numbers and underscores and be between 4 and 32 characters long.')])
    private = BooleanField('Private')


class CreatePostForm(Form):
    title = StringField('Title', [validators.length(min=6, max=128)])
    url = StringField('URL', [validators.length(min=11, max=512),
                               validators.url()])
