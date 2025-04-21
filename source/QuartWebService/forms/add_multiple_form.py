"""
Form for adding multiple videos to the queue
"""
from quart_wtf import QuartForm
from wtforms import StringField, HiddenField, SubmitField, FieldList
from wtforms.validators import DataRequired, Optional

class AddMultipleForm(QuartForm):
    """Form for adding multiple videos to the queue"""
    channel_id = HiddenField('Channel ID', validators=[DataRequired()])
    playlist_id = HiddenField('Playlist ID', validators=[Optional()])
    page_token = HiddenField('Page Token', validators=[Optional()])
    video_ids = FieldList(StringField('Video ID'), min_entries=0)
    video_titles = FieldList(StringField('Video Title'), min_entries=0)
    submit = SubmitField('Add Selected to Queue')