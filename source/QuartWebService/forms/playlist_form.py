"""
Form for adding an entire playlist to the queue
"""
from quart_wtf import QuartForm
from wtforms import HiddenField, SubmitField
from wtforms.validators import DataRequired

class PlaylistForm(QuartForm):
    """Form for adding an entire playlist to the queue"""
    channel_id = HiddenField('Channel ID', validators=[DataRequired()])
    playlist_id = HiddenField('Playlist ID', validators=[DataRequired()])
    playlist_title = HiddenField('Playlist Title', default='Unknown Playlist')
    submit = SubmitField('Add Entire Playlist')