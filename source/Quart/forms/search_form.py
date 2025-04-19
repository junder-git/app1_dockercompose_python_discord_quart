"""
Form for searching YouTube
"""
from quart_wtf import QuartForm
from wtforms import StringField, SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Optional

class SearchForm(QuartForm):
    """Form for searching YouTube"""
    query = StringField('Search', validators=[DataRequired()])
    search_type = SelectField('Search Type', 
                             choices=[
                                 ('video', 'Videos'), 
                                 ('playlist', 'Playlists'),
                                 ('artist', 'Artists'),
                                 ('comprehensive', 'All Types')
                             ],
                             default='comprehensive')
    channel_id = HiddenField('Channel ID', validators=[Optional()])
    submit = SubmitField('Search')