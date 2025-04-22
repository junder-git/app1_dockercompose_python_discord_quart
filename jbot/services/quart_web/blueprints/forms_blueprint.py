from quart_wtf import QuartForm
from wtforms import StringField, SelectField, SubmitField, HiddenField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Optional

class MusicControlForm(QuartForm):
    """Form for music control actions"""
    command = SelectField('Command', 
                          choices=[
                              ('join', 'Join'), 
                              ('skip', 'Skip'), 
                              ('pause', 'Pause'), 
                              ('resume', 'Resume'), 
                              ('stop', 'Stop')
                          ],
                          default='join')
    channel_id = HiddenField('Channel ID', validators=[Optional()])
    submit = SubmitField('Execute')

class SearchForm(QuartForm):
    """Form for searching YouTube"""
    query = StringField('Search', validators=[DataRequired()])
    search_type = SelectField('Search Type', 
                             choices=[
                                 ('video', 'Videos'), 
                                 ('playlist', 'Playlists'),
                                 ('comprehensive', 'All Types')
                             ],
                             default='comprehensive')
    channel_id = HiddenField('Channel ID', validators=[Optional()])
    submit = SubmitField('Search')

class UrlForm(QuartForm):
    """Form for adding videos by URL"""
    url = StringField('YouTube URL', validators=[DataRequired()])
    channel_id = HiddenField('Channel ID', validators=[Optional()])
    submit = SubmitField('Add to Queue')

class ClearQueueForm(QuartForm):
    """Form for clearing the queue"""
    guild_id = HiddenField('Guild ID', validators=[DataRequired()])
    submit = SubmitField('Clear Queue')

class ShuffleQueueForm(QuartForm):
    """Form for shuffling the queue"""
    channel_id = HiddenField('Channel ID', validators=[DataRequired()])
    submit = SubmitField('Shuffle Queue')

class PlaylistManagementForm(QuartForm):
    """Form for managing playlists"""
    name = StringField('Playlist Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    is_public = BooleanField('Make Playlist Public')
    submit = SubmitField('Save Playlist')

class AdvancedSearchForm(QuartForm):
    """Advanced YouTube search form"""
    query = StringField('Search Query', validators=[DataRequired()])
    search_type = SelectField('Search Type', 
                             choices=[
                                 ('video', 'Videos'), 
                                 ('playlist', 'Playlists'),
                                 ('channel', 'Channels'),
                                 ('comprehensive', 'All Types')
                             ],
                             default='comprehensive')
    submit = SubmitField('Advanced Search')

class BotConfigForm(QuartForm):
    """Form for configuring bot settings"""
    prefix = StringField('Command Prefix', validators=[Optional()])
    auto_join = BooleanField('Automatically Join Voice Channel')
    submit = SubmitField('Save Configuration')

class AddMultipleForm(QuartForm):
    """Form for adding multiple videos to the queue"""
    playlist_id = HiddenField('Playlist ID', validators=[Optional()])
    channel_id = HiddenField('Channel ID', validators=[DataRequired()])
    # Note: We'll handle the video selections dynamically with JavaScript
    submit = SubmitField('Add Selected to Queue')