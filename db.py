from flask import g
import sqlite3
import click
from glob import glob
from pathlib import Path
from datetime import datetime
from typing import Optional

DATABASE = "booking_app.db"


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def create_tables() -> None:
    db = get_db()
    cur = db.cursor()

    for path in glob("sql/*.sql"):

        path: Path = Path(path)
        table_name = path.with_suffix("").name

        with open(path, "r") as f:
            cur.execute(f.read())
        click.echo(f"Created Table {table_name}")

    db.commit()
    click.echo("Database Created")


def get_bookings_inbetween(
    start: datetime, end: datetime
) -> list[tuple[datetime, datetime, str]]:
    db = get_db()

    cur = db.execute(
        "SELECT start_time, end_time, user_id FROM bookings WHERE start_time >= ? AND end_time <= ? ORDER BY start_time ASC;",
        (start, end),
    )

    bookings = []
    for row in cur.fetchall():

        username = get_user_name(row[2]) or "Unknown"

        bookings.append(
            (
                datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S"),
                datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S"),
                username,
            )
        )

    return bookings


def get_user_name(user_id) -> Optional[str]:
    db = get_db()
    cur = db.execute("SELECT lastname FROM users WHERE user_id = ?", (user_id,))
    user_name = cur.fetchone()
    return user_name[0] if user_name else None
