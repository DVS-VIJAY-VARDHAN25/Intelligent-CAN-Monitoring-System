import csv
import json
import os


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

CSV_FILE = os.path.join(
    BASE_DIR,
    "can_log.csv"
)

BASELINE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "normal_baseline.json"
)


# --------------------------------------------------
# LOAD NORMAL BASELINE
# --------------------------------------------------

print("==============================================")
print("          CAN ANOMALY DETECTOR V1")
print("==============================================")
print()

print("Loading normal baseline...")

try:
    with open(BASELINE_FILE, "r") as file:
        baseline = json.load(file)

except FileNotFoundError:
    print("ERROR: normal_baseline.json not found!")
    print("Check that the file exists in:")
    print("data/processed/")
    raise SystemExit


allowed_ids = set(baseline["can_ids"])
allowed_dlc = set(baseline["allowed_dlc"])
allowed_data_lengths = set(
    baseline["allowed_data_lengths"]
)
allowed_button_states = set(
    baseline["allowed_button_states"]
)


print("Baseline loaded successfully.")
print()

print("Normal CAN configuration:")
print("----------------------------------------------")
print("Allowed CAN IDs       :", allowed_ids)
print("Allowed DLC           :", allowed_dlc)
print("Allowed data lengths  :", allowed_data_lengths)
print("Allowed button states :", allowed_button_states)
print("----------------------------------------------")
print()


# --------------------------------------------------
# LOAD CAN LOG
# --------------------------------------------------

print("Loading CAN log...")

try:
    with open(CSV_FILE, "r", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

except FileNotFoundError:
    print("ERROR: can_log.csv not found!")
    print("Check that the CSV file exists in:")
    print("data/raw/")
    raise SystemExit


print("CAN log loaded successfully.")
print("Total frames:", len(rows))
print()


# --------------------------------------------------
# ANOMALY COUNTERS
# --------------------------------------------------

total_anomalies = 0
id_anomalies = 0
dlc_anomalies = 0
data_length_anomalies = 0
button_anomalies = 0


# --------------------------------------------------
# ANALYZE EACH FRAME
# --------------------------------------------------

print("==============================================")
print("             FRAME ANALYSIS")
print("==============================================")

for index, row in enumerate(rows, start=1):

    anomalies = []

    can_id = row["CAN ID"].strip()
    button_state = row["Button State"].strip()

    # ----------------------------------------------
    # CAN ID CHECK
    # ----------------------------------------------

    if can_id not in allowed_ids:
        anomalies.append("UNEXPECTED CAN ID")
        id_anomalies += 1


    # ----------------------------------------------
    # DLC CHECK
    # ----------------------------------------------

    try:
        dlc = int(row["DLC"])
    except ValueError:
        dlc = -1

    if dlc not in allowed_dlc:
        anomalies.append("UNEXPECTED DLC")
        dlc_anomalies += 1


    # ----------------------------------------------
    # DATA LENGTH CHECK
    # ----------------------------------------------

    data_field = row["CAN Data"].strip()

    if data_field:
        data_bytes = data_field.split()
        data_length = len(data_bytes)
    else:
        data_length = 0

    if data_length not in allowed_data_lengths:
        anomalies.append("UNEXPECTED DATA LENGTH")
        data_length_anomalies += 1


    # ----------------------------------------------
    # BUTTON STATE CHECK
    # ----------------------------------------------

    if button_state not in allowed_button_states:
        anomalies.append("UNEXPECTED BUTTON STATE")
        button_anomalies += 1


    # ----------------------------------------------
    # FRAME RESULT
    # ----------------------------------------------

    if anomalies:

        total_anomalies += 1

        print()
        print("🚨 ANOMALY DETECTED")
        print("----------------------------------------------")
        print("Frame       :", index)
        print("CAN ID      :", can_id)
        print("DLC         :", dlc)
        print("Data Length :", data_length)
        print("Button      :", button_state)

        print("Reason(s):")

        for anomaly in anomalies:
            print("  →", anomaly)

        print("----------------------------------------------")

    else:

        print(
            f"Frame {index:3d} → NORMAL"
        )


# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

print()
print("==============================================")
print("            ANOMALY ANALYSIS SUMMARY")
print("==============================================")

print("Total frames analyzed :", len(rows))
print("Total anomalous frames:", total_anomalies)

print()
print("CAN ID anomalies      :", id_anomalies)
print("DLC anomalies         :", dlc_anomalies)
print("Data length anomalies :", data_length_anomalies)
print("Button state anomalies:", button_anomalies)

print("----------------------------------------------")

if total_anomalies == 0:
    print("RESULT: NO STRUCTURAL ANOMALIES DETECTED")
else:
    print("RESULT: ANOMALIES DETECTED")

print("==============================================")