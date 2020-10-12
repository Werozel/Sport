from globals import db


class EventPlayTimes(db.Model):
    __tablename__ = "event_play_times"

    id = db.Column(db.BigInteger, primary_key=True)
    day_of_week = db.Column(db.Integer)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    address_id = db.Column(db.BigInteger, db.ForeignKey("address_cache.id"), nullable=True)
    location_id = db.Column(db.BigInteger, db.ForeignKey("location_cache.id"), nullable=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey("events.id"), nullable=False)

    @staticmethod
    def get(id: int):
        return EventPlayTimes.query.filter_by(id=id).first()

    @staticmethod
    def get_all_for_event(id: int):
        return EventPlayTimes.query.filter_by(event_id=id).all()