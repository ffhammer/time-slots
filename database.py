from datetime import datetime, timedelta
from typing import List, Tuple

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

from config import TIME_ZONE

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(
        db.String(255), nullable=False
    )  # In production, store a hashed password
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(tz=TIME_ZONE)
    )
    bookings = db.relationship("Booking", backref="user", lazy=True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(tz=TIME_ZONE)
    )


def get_bookings_inbetween(
    start: datetime, end: datetime
) -> List[Tuple[datetime, datetime, str]]:
    bookings = (
        Booking.query.filter(Booking.start_time >= start, Booking.end_time <= end)
        .order_by(Booking.start_time)
        .all()
    )
    result = []
    for booking in bookings:
        username = (
            f"{booking.user.first_name} {booking.user.last_name}"
            if booking.user
            else "Unknown"
        )
        result.append((booking.start_time, booking.end_time, username))
    return result


def fill_with_example_data():
    users = [
        User(
            first_name="José",
            last_name="Alvarado",
            email="jose@example.com",
            password="Password1",
        ),
        User(
            first_name="María",
            last_name="Castro",
            email="maria@example.com",
            password="Password2",
        ),
        User(
            first_name="Carlos",
            last_name="Méndez",
            email="carlos@example.com",
            password="Password3",
        ),
    ]
    for user in users:
        db.session.add(user)
    db.session.commit()
    u1 = User.query.filter_by(email="jose@example.com").first()
    u2 = User.query.filter_by(email="maria@example.com").first()
    u3 = User.query.filter_by(email="carlos@example.com").first()
    tomorrow = (datetime.now(tz=TIME_ZONE) + timedelta(days=1)).date()
    bookings = [
        Booking(
            user_id=u1.id,
            start_time=datetime.combine(
                tomorrow, datetime.strptime("10:00", "%H:%M").time()
            ),
            end_time=datetime.combine(
                tomorrow, datetime.strptime("10:30", "%H:%M").time()
            ),
        ),
        Booking(
            user_id=u2.id,
            start_time=datetime.combine(
                tomorrow, datetime.strptime("11:00", "%H:%M").time()
            ),
            end_time=datetime.combine(
                tomorrow, datetime.strptime("11:15", "%H:%M").time()
            ),
        ),
        Booking(
            user_id=u3.id,
            start_time=datetime.combine(
                tomorrow, datetime.strptime("14:00", "%H:%M").time()
            ),
            end_time=datetime.combine(
                tomorrow, datetime.strptime("15:00", "%H:%M").time()
            ),
        ),
    ]
    for booking in bookings:
        db.session.add(booking)
    db.session.commit()
