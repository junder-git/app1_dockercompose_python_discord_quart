"""
Form for adding a single video to the queue
"""
from quart_wtf import QuartForm
from wtforms import HiddenField, SubmitField
from wtforms.validators import DataRequired

class AddToQueueForm(QuartForm):
    """Form for adding a single video to the queue"""
    channel_id = HiddenField('Channel ID', validators=[DataRequired()])
    video_id = HiddenField('Video ID', validators=[DataRequired()])
    video_title = HiddenField('Video Title', validators=[DataRequired()])
    return_to = HiddenField('Return To', default='dashboard')
    submit = SubmitField('Add to Queue')