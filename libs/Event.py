from globals import db, timestamp
from libs.EventMember import EventMember

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(100), nullable=False)
    description = db.Column(db.VARCHAR(300), nullable=True)
    sport = db.Column(db.VARCHAR(50), nullable=False)
    group_id = db.Column(db.BigInteger, db.ForeignKey('groups.id'), nullable=True)
    creation_time = db.Column(db.TIMESTAMP, default=timestamp())
    creator = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
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


    def add_member(self, user):
        res = EventMember.query.filter_by(event_id=self.id, user_id=user.id).first()
        if res is not None:
            return
        new_member = EventMember(event_id=self.id, user_id=user.id, time=timestamp())
        db.session.add(new_member)
        db.session.commit()


    def get_members(self):
        return [i.user for i in EventMember.query.filter_by(event_id=self.id).all()]

    def remove_member(self, user):
        res = EventMember.query.filter_by(event_id=self.id, user_id=user.id).first()
        if res is not None:
            db.session.delete(res)
            db.session.commit()