"""
Login form for JBot Quart application
"""
from quart_wtf import QuartForm
from wtforms import SubmitField, HiddenField

class LoginForm(QuartForm):
    """Login form"""
    next = HiddenField()
    submit = SubmitField('Login with Discord')