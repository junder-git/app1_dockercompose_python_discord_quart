"""
Form for shuffling the music queue
"""
from quart_wtf import QuartForm
from wtforms import HiddenField, SubmitField
from wtforms.validators import DataRequired

class ShuffleQueueForm(QuartForm):
    """Form for shuffling the music queue"""
    channel_id = HiddenField('Channel ID', validators=[DataRequired()])
    submit = SubmitField('Shuffle Queue')