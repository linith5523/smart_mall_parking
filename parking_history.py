import csv
import os
from datetime import datetime


# -----------------------------
# History File Location
# -----------------------------
PROJECT_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "data"
)

HISTORY_FILE = os.path.join(
    DATA_FOLDER,
    "parking_history.csv"
)


# -----------------------------
# Create History File
# -----------------------------
def initialize_history():

    # Create data folder if it does not exist
    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )

    # Create CSV file if it does not exist
    if not os.path.exists(HISTORY_FILE):

        with open(
            HISTORY_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "vehicle_number",
                "vehicle_type",
                "slot",
                "entry_time",
                "exit_time",
                "status"
            ])


# -----------------------------
# Record Vehicle Entry
# -----------------------------
def record_entry(
    vehicle_number,
    vehicle_type,
    slot
):

    initialize_history()

    entry_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(
        HISTORY_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            vehicle_number,
            vehicle_type,
            slot,
            entry_time,
            "",
            "PARKED"
        ])


# -----------------------------
# Record Vehicle Exit
# -----------------------------
def record_exit(vehicle_number):

    initialize_history()

    rows = []

    with open(
        HISTORY_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if (
                row["vehicle_number"]
                == vehicle_number
                and row["status"]
                == "PARKED"
            ):

                row["exit_time"] = (
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                row["status"] = "EXITED"

            rows.append(row)


    # Rewrite updated CSV
    with open(
        HISTORY_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "vehicle_number",
            "vehicle_type",
            "slot",
            "entry_time",
            "exit_time",
            "status"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(rows)


# -----------------------------
# Read Parking History
# -----------------------------
def get_history():

    initialize_history()

    history = []

    with open(
        HISTORY_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:
            history.append(row)

    return history