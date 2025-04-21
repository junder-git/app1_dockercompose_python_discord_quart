"""
Form for adding videos by URL
"""
from quart_wtf import QuartForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired, URL

class UrlForm(QuartForm):
    """Form for adding videos by URL"""
    url = StringField('YouTube URL', validators=[DataRequired(), URL()])
    channel_id = HiddenField('Channel ID', validators=[DataRequired()])
    submit = SubmitField('Add to Queue')