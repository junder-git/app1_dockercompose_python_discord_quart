"""
Form for controlling music playback
"""
from quart_wtf import QuartForm
from wtforms import SelectField, HiddenField, SubmitField
from wtforms.validators import DataRequired

class MusicControlForm(QuartForm):
    """Form for controlling music playback"""
    command = SelectField('Command', 
                          choices=[
                              ('join', 'Join'), 
                              ('skip', 'Skip'), 
                              ('pause', 'Pause'), 
                              ('resume', 'Resume'), 
                              ('stop', 'Stop')
                          ],
                          validators=[DataRequired()])
    channel_id = HiddenField('Channel ID', validators=[DataRequired()])
    submit = SubmitField('Execute')