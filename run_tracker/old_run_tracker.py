#!/usr/bin/env python3

import sys
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import os

DB_NAME = "runner.db"

def initialize_db(db_name=DB_NAME):
    """
    Creates the 'runs' table if it doesn't already exist.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            duration REAL NOT NULL,    -- duration in minutes
            distance REAL NOT NULL,    -- distance in kilometers
            perceived_effort INTEGER   -- from 1 to 10
        )
    """)
    conn.commit()
    conn.close()

def add_run(db_name=DB_NAME):
    """
    Prompts user for run details and inserts a new row into the 'runs' table.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Prompt user for run details
    date_str = input("Enter date (YYYY-MM-DD): ")
    duration_str = input("Enter duration (minutes): ")
    distance_str = input("Enter distance (kilometers): ")
    effort_str = input("Enter perceived effort (1-10): ")

    # Validate or parse inputs as needed
    try:
        # Attempt to parse the date
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

    # Insert into the table
    cursor.execute("""
        INSERT INTO runs (date, duration, distance, perceived_effort)
        VALUES (?, ?, ?, ?)
    """, (date_str, duration_val, distance_val, effort_val))

    conn.commit()
    conn.close()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Run entry saved successfully.")

def get_weekly_progress(conn, reference_date=None):
    """
    Calculates running progress for the 7-day period ending on `reference_date`.
    If no reference_date is provided, uses today's date as the end of the 7-day period.

    Returns a dictionary with total distance, total duration, average speed,
    and average perceived effort for the past 7 days.
    """
    if reference_date is None:
        reference_date = datetime.now().date()

    # Convert reference_date to date object if given as a string
    if isinstance(reference_date, str):
        reference_date = datetime.strptime(reference_date, '%Y-%m-%d').date()

    # We'll look at the week window from reference_date - 6 days, inclusive
    start_of_week = reference_date - timedelta(days=6)

    query = """
        SELECT
            SUM(distance) as total_distance,
            SUM(duration) as total_duration,
            AVG(distance / (duration / 60.0)) as avg_speed,  -- distance / hours
            AVG(perceived_effort) as avg_effort
        FROM runs
        WHERE date >= ? AND date <= ?
    """

    cursor = conn.cursor()
    cursor.execute(query, (start_of_week.isoformat(), reference_date.isoformat()))
    row = cursor.fetchone()

    # row is a tuple (total_distance, total_duration, avg_speed, avg_effort)
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
    """
    Prints summary of the past week's stats in the console.
    """
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
    """
    Generates a basic matplotlib chart (daily total distance over the past 7 days)
    and saves it as 'weekly_performance_<YYYY-MM-DD>.png'.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # We'll consider daily totals for the last 7 days (including today).
    today = datetime.now().date()
    start_of_week = today - timedelta(days=6)

    # Query daily distance sums
    cursor.execute("""
        SELECT date, SUM(distance) as daily_distance
        FROM runs
        WHERE date >= ? AND date <= ?
        GROUP BY date
        ORDER BY date
    """, (start_of_week.isoformat(), today.isoformat()))

    data = cursor.fetchall()
    conn.close()

    # data is a list of tuples (date_str, daily_distance)
    dates = []
    distances = []
    for row in data:
        date_str, dist = row
        # Convert string date to a datetime.date object for plotting labels
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        dates.append(date_obj)
        distances.append(dist)

    if not dates:
        print("[Info] No runs found in the last 7 days to visualize.")
        return

    # Sort by date just to be safe (though the ORDER BY above should handle it)
    dates, distances = zip(*sorted(zip(dates, distances), key=lambda x: x[0]))

    # Create plot
    plt.figure(figsize=(8, 4))
    plt.bar(dates, distances, color='blue', alpha=0.7)
    plt.title("Daily Distance Over the Past 7 Days")
    plt.xlabel("Date")
    plt.ylabel("Distance (km)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save plot
    filename = f"weekly_performance_{today.isoformat()}.png"
    plt.savefig(filename)
    plt.close()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Chart created: {filename}")

def main():
    """
    Main entry point for the command-line interface.
    Usage:
        python run_tracker.py add-run
        python run_tracker.py weekly-stats
        python run_tracker.py visualize
    """
    # Initialize the database (create table if needed)
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



