"""
Form for reordering tracks in the queue
"""
from quart_wtf import QuartForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired

class ReorderQueueForm(QuartForm):
    """Form for reordering tracks in the queue"""
    channel_id = HiddenField('Channel ID', validators=[DataRequired()])
    old_index = StringField('Old Index', validators=[DataRequired()])
    new_index = StringField('New Index', validators=[DataRequired()])
    submit = SubmitField('Reorder')