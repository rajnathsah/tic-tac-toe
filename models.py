from app import db

class TicTac(db.Model):
    __tablename__ = 'tictactoe'

    id = db.Column('roomno', db.Integer, primary_key=True)
    player1_name = db.Column(db.String(50))
    player2_name = db.Column(db.String(50))
    player1_id = db.Column(db.String(1))
    player2_id = db.Column(db.String(1))
    col1 = db.Column(db.String(1))
    col2 = db.Column(db.String(1))
    col3 = db.Column(db.String(1))
    col4 = db.Column(db.String(1))
    col5 = db.Column(db.String(1))
    col6 = db.Column(db.String(1))
    col7 = db.Column(db.String(1))
    col8 = db.Column(db.String(1))
    col9 = db.Column(db.String(1))
    winner = db.Column(db.String(1))
    turn = db.Column(db.String(1))
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<id {}>'.format(self.id)


class VotingResult(db.Model):
    __tablename__ = 'voteresults'

    id = db.Column('id', db.Integer, primary_key=True)
    vote = db.Column('data', db.Integer)