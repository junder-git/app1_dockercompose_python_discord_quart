"""
Form for clearing the music queue
"""
from quart_wtf import QuartForm
from wtforms import HiddenField, SubmitField
from wtforms.validators import DataRequired

class ClearQueueForm(QuartForm):
    """Form for clearing the music queue"""
    guild_id = HiddenField('Guild ID', validators=[DataRequired()])
    submit = SubmitField('Clear Queue')