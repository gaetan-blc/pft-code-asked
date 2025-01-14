#!/usr/bin/env python3

import sys
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

DB_NAME = "runner.db"

def initialize_db(db_name=DB_NAME):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            duration REAL NOT NULL,
            distance REAL NOT NULL,
            perceived_effort INTEGER
        )
    """)
    conn.commit()
    conn.close()

def add_run(db_name=DB_NAME):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    date_str = input("Enter date (YYYY-MM-DD): ")
    duration_str = input("Enter duration (minutes): ")
    distance_str = input("Enter distance (kilometers): ")
    effort_str = input("Enter perceived effort (1-10): ")

    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print("[Error] Invalid date format. Please use YYYY-MM-DD.")
        conn.close()
        return

    try:
        duration_val = float(duration_str)
        distance_val = float(distance_str)
        effort_val = int(effort_str)
        if not (1 <= effort_val <= 10):
            raise ValueError("Effort must be between 1 and 10.")
    except ValueError as e:
        print(f"[Error] Invalid number format: {e}")
        conn.close()
        return

    cursor.execute("""
        INSERT INTO runs (date, duration, distance, perceived_effort)
        VALUES (?, ?, ?, ?)
    """, (date_str, duration_val, distance_val, effort_val))

    conn.commit()
    conn.close()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Run entry saved successfully.")

def get_weekly_progress(conn, reference_date=None):
    if reference_date is None:
        reference_date = datetime.now().date()

    if isinstance(reference_date, str):
        reference_date = datetime.strptime(reference_date, '%Y-%m-%d').date()

    start_of_week = reference_date - timedelta(days=6)

    query = """
        SELECT
            SUM(distance) as total_distance,
            SUM(duration) as total_duration,
            AVG(distance / (duration / 60.0)) as avg_speed,
            AVG(perceived_effort) as avg_effort
        FROM runs
        WHERE date >= ? AND date <= ?
    """
    cursor = conn.cursor()
    cursor.execute(query, (start_of_week.isoformat(), reference_date.isoformat()))
    row = cursor.fetchone()

    if not row or row[0] is None:
        return {
            'total_distance': 0.0,
            'total_duration': 0.0,
            'avg_speed': 0.0,
            'avg_effort': 0.0
        }

    total_distance, total_duration, avg_speed, avg_effort = row
    return {
        'total_distance': total_distance or 0.0,
        'total_duration': total_duration or 0.0,
        'avg_speed': avg_speed or 0.0,
        'avg_effort': avg_effort or 0.0
    }

def show_weekly_stats(db_name=DB_NAME):
    conn = sqlite3.connect(db_name)
    reference_date = datetime.now().date()
    progress = get_weekly_progress(conn, reference_date=reference_date)
    conn.close()

    start_of_week = reference_date - timedelta(days=6)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Weekly Stats ({start_of_week} to {reference_date}):")
    print(f"  - Total Distance: {progress['total_distance']:.2f} km")
    print(f"  - Total Duration: {progress['total_duration']:.1f} min")
    print(f"  - Avg Speed: {progress['avg_speed']:.2f} km/h")
    print(f"  - Avg Effort: {progress['avg_effort']:.1f}")

def visualize(db_name=DB_NAME):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    today = datetime.now().date()
    start_of_week = today - timedelta(days=6)
    all_days = [start_of_week + timedelta(days=i) for i in range(7)]

    cursor.execute(
        """
        SELECT date, SUM(distance) as daily_distance
        FROM runs
        WHERE date >= ? AND date <= ?
        GROUP BY date
        ORDER BY date
        """,
        (start_of_week.isoformat(), today.isoformat())
    )
    data = cursor.fetchall()
    conn.close()

    # Prepare a dict of all days -> 0.0
    distance_map = {d.strftime('%Y-%m-%d'): 0.0 for d in all_days}

    # Populate with real distances
    for (date_str, daily_distance) in data:
        distance_map[date_str] = daily_distance

    x_dates = []
    y_distances = []

    for key_date in sorted(distance_map.keys()):
        x_dates.append(datetime.strptime(key_date, '%Y-%m-%d').date())
        y_distances.append(distance_map[key_date])

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x_dates, y_distances, color='blue', alpha=0.7)
    ax.set_title("Daily Distance Over the Past 7 Days")
    ax.set_xlabel("Date")
    ax.set_ylabel("Distance (km)")

    # Configure date axis
    ax.xaxis.set_major_locator(mdates.DayLocator())  # one tick per day
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    plt.tight_layout()
    filename = f"weekly_performance_{today.isoformat()}.png"
    plt.savefig(filename)
    plt.close()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Chart created: {filename}")

def main():
    initialize_db(DB_NAME)

    if len(sys.argv) < 2:
        print("Usage: python run_tracker.py [add-run | weekly-stats | visualize]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "add-run":
        add_run(DB_NAME)
    elif command == "weekly-stats":
        show_weekly_stats(DB_NAME)
    elif command == "visualize":
        visualize(DB_NAME)
    else:
        print(f"Unknown command: {command}")
        print("Usage: python run_tracker.py [add-run | weekly-stats | visualize]")

if __name__ == "__main__":
    main()


