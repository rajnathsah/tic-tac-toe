from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class Room(FlaskForm):
    '''
    Form for creating game room
    '''
    name = StringField('Name :', [DataRequired(message=('Don\'t be shy!'))])
    createroom = SubmitField('Create Room')

class JoinRoom(FlaskForm):
    '''
    Form for joining room
    '''
    name = StringField('Name :', [DataRequired(message=('Don\'t be shy!'))])
    roomnumber = StringField('Room Number :', [DataRequired(message='Enter room number shared by your friend.')])
    joinroom = SubmitField('Join Room')