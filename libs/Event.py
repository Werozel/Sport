from globals import db, timestamp
from libs.EventMember import EventMember

class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(100), nullable=False)
    description = db.Column(db.VARCHAR(300), nullable=True)
    sport = db.Column(db.VARCHAR(50), nullable=False)
    group_id = db.Column(db.BigInteger, db.ForeignKey('groups.id'), nullable=True)
    creation_time = db.Column(db.TIMESTAMP, default=timestamp())
    time = db.Column(db.TIMESTAMP, nullable=True)
    # TODO добавить карту
    # TODO добавить повторы

    event_members_rel = db.relationship('EventMember', backref='event', lazy=True)

    @staticmethod
    def get(id):
        try:
            id = int(id)
        except:
            raise TypeError("Not valid id")
        return Event.query.filter_by(id=id).first()

