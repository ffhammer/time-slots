from flask import Flask, g, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
import click
from db import create_tables, get_db, get_bookings_inbetween

app = Flask(__name__)
DATABASE = "booking_app.db"
START_DAY = 8
END_DAY = 22


@app.cli.command("init-db")
def init_db():
    """Initialize the database."""
    create_tables()
    click.echo("Database initialized.")


@app.cli.command("fill-samples")
def generate_sample_data() -> None:
    db: sqlite3.Connection = get_db()
    users = [
        ("José", "Alvarado", "hash1"),
        ("María", "Castro", "hash2"),
        ("Carlos", "Méndez", "hash3"),
    ]
    for firstname, lastname, password_hash in users:
        db.execute(
            "INSERT OR IGNORE INTO users (firstname, lastname, password_hash) VALUES (?, ?, ?)",
            (firstname, lastname, password_hash),
        )
    cur = db.execute("SELECT user_id, firstname, lastname FROM users")
    user_ids = {f"{row[1]} {row[2]}": row[0] for row in cur.fetchall()}
    tomorrow = (datetime.now() + timedelta(days=1)).date()
    bookings = [
        (user_ids["José Alvarado"], f"{tomorrow} 10:00:00", f"{tomorrow} 10:30:00"),
        (user_ids["María Castro"], f"{tomorrow} 11:00:00", f"{tomorrow} 11:15:00"),
        (user_ids["Carlos Méndez"], f"{tomorrow} 14:00:00", f"{tomorrow} 15:00:00"),
    ]
    for user_id, start_time, end_time in bookings:
        db.execute(
            "INSERT INTO bookings (user_id, start_time, end_time) VALUES (?, ?, ?)",
            (user_id, start_time, end_time),
        )
    db.commit()


@app.teardown_appcontext
def close_db(_: Exception = None) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def get_availability() -> dict:
    today = datetime.now().date()
    avail: dict[str, list] = {}
    for offset in range(7):
        day = today + timedelta(days=offset)
        day_str = day.strftime("%Y-%m-%d")
        day_start = datetime(day.year, day.month, day.day, START_DAY)
        day_end = datetime(day.year, day.month, day.day, END_DAY)
        blocks = []
        current = day_start
        for res_start, res_end, user_name in get_bookings_inbetween(day_start, day_end):

            if current < res_start:
                block = {"start": current, "end": res_start, "status": "free"}
                block["offset"] = int((current - day_start).total_seconds() / 60)
                block["duration"] = int((res_start - current).total_seconds() / 60)
                blocks.append(block)
            block = {
                "start": res_start,
                "end": res_end,
                "status": "reserved",
                "name": user_name,
            }
            block["offset"] = int((res_start - day_start).total_seconds() / 60)
            block["duration"] = int((res_end - res_start).total_seconds() / 60)
            blocks.append(block)
            current = res_end
        if current < day_end:
            block = {"start": current, "end": day_end, "status": "free"}
            block["offset"] = int((current - day_start).total_seconds() / 60)
            block["duration"] = int((day_end - current).total_seconds() / 60)
            blocks.append(block)
        avail[day_str] = blocks
    return avail


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    if request.method == "POST":
        user_id = 1
        date_sel = request.form.get("date")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        if date_sel and start_time and end_time:
            start_dt = f"{date_sel} {start_time}:00"
            end_dt = f"{date_sel} {end_time}:00"
            db = get_db()
            db.execute(
                "INSERT INTO bookings (user_id, start_time, end_time) VALUES (?, ?, ?)",
                (user_id, start_dt, end_dt),
            )
            db.commit()
        return redirect(url_for("index"))
    dates = [
        (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)
    ]
    availability = get_availability()

    return render_template(
        "index.html",
        title="Soccer Field Booking",
        dates=dates,
        availability=availability,
        START_DAY=START_DAY,
        END_DAY=END_DAY,
    )


if __name__ == "__main__":
    app.run(debug=True)
