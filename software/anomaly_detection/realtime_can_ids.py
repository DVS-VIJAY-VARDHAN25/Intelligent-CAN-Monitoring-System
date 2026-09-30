import os
import json
import pandas as pd
import sys
import time
from datetime import datetime


# ============================================================
# PATH SETUP
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

BASELINE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "normal_baseline.json"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "ids_alerts.csv"
)


# ============================================================
# INPUT DATASET
# ============================================================

if len(sys.argv) > 1:

    CSV_FILE = os.path.abspath(
        sys.argv[1]
    )

else:

    CSV_FILE = os.path.join(
        BASE_DIR,
        "can_log.csv"
    )


# ============================================================
# HEADER
# ============================================================

print("==============================================")
print("       REAL-TIME CAN INTRUSION DETECTION")
print("                    V1.0")
print("==============================================")
print()


# ============================================================
# LOAD BASELINE
# ============================================================

print("Loading normal CAN baseline...")

if not os.path.exists(BASELINE_FILE):

    print("ERROR: Baseline file not found!")
    print(BASELINE_FILE)
    exit()

with open(
    BASELINE_FILE,
    "r"
) as file:

    baseline = json.load(file)

print("Baseline loaded successfully.")
print()


allowed_ids = set(
    str(x).strip()
    for x in baseline["can_ids"]
)

allowed_dlc = set(
    int(x)
    for x in baseline["allowed_dlc"]
)

allowed_data_lengths = set(
    int(x)
    for x in baseline["allowed_data_lengths"]
)

expected_counter_increment = (
    baseline["packet_counter"]["expected_increment"]
)

minimum_interval_ms = (
    baseline["timing"]["minimum_interval_ms"]
)


# ============================================================
# LOAD DATASET
# ============================================================

print("Loading CAN dataset...")

if not os.path.exists(CSV_FILE):

    print("ERROR: CAN dataset not found!")
    print(CSV_FILE)
    exit()

df = pd.read_csv(
    CSV_FILE
)

print("Dataset loaded successfully.")
print(
    "Total frames:",
    len(df)
)

print()


# ============================================================
# SEVERITY FUNCTION
# ============================================================

def get_severity(reason):

    if "UNEXPECTED CAN ID" in reason:
        return "HIGH"

    if "PACKET SEQUENCE ERROR" in reason:
        return "HIGH"

    if "HIGH TRAFFIC RATE" in reason:
        return "HIGH"

    if "UNEXPECTED DLC" in reason:
        return "MEDIUM"

    if "UNEXPECTED DATA LENGTH" in reason:
        return "MEDIUM"

    if "INVALID PAYLOAD" in reason:
        return "MEDIUM"

    return "LOW"


# ============================================================
# VARIABLES
# ============================================================

previous_counter = None
previous_event_time = None

current_session = 1

alerts = []


# ============================================================
# START MONITORING
# ============================================================

print("==============================================")
print("          LIVE CAN MONITORING")
print("==============================================")
print()

print("Monitoring started...")
print("Press Ctrl+C to stop.")
print()


try:

    for index, row in df.iterrows():

        frame_number = index + 1

        reasons = []


        # ----------------------------------------------------
        # CAN ID
        # ----------------------------------------------------

        can_id = str(
            row["CAN ID"]
        ).strip()

        if can_id not in allowed_ids:

            reasons.append(
                "UNEXPECTED CAN ID"
            )


        # ----------------------------------------------------
        # DLC
        # ----------------------------------------------------

        try:

            dlc = int(
                row["DLC"]
            )

        except:

            dlc = -1

        if dlc not in allowed_dlc:

            reasons.append(
                "UNEXPECTED DLC"
            )


        # ----------------------------------------------------
        # DATA
        # ----------------------------------------------------

        can_data = str(
            row["CAN Data"]
        ).strip()

        data_bytes = can_data.split()

        data_length = len(
            data_bytes
        )


        # ----------------------------------------------------
        # DATA LENGTH
        # ----------------------------------------------------

        if data_length not in allowed_data_lengths:

            reasons.append(
                "UNEXPECTED DATA LENGTH"
            )


        # ----------------------------------------------------
        # PAYLOAD
        # ----------------------------------------------------

        if data_length >= 1:

            button_byte = (
                data_bytes[0].upper()
            )

            if button_byte not in [
                "00",
                "01"
            ]:

                reasons.append(
                    f"INVALID PAYLOAD "
                    f"(button byte = {button_byte})"
                )


        # ----------------------------------------------------
        # PACKET COUNTER
        # ----------------------------------------------------

        current_counter = None

        if data_length >= 5:

            try:

                current_counter = int(
                    "".join(
                        data_bytes[1:5]
                    ),
                    16
                )

            except:

                current_counter = None


        # ----------------------------------------------------
        # EVENT TIME
        # ----------------------------------------------------

        current_event_time = None

        if data_length >= 8:

            try:

                current_event_time = int(
                    "".join(
                        data_bytes[5:8]
                    ),
                    16
                )

            except:

                current_event_time = None


        # ----------------------------------------------------
        # SESSION RESET
        # ----------------------------------------------------

        session_reset = False

        if (
            current_event_time is not None
            and previous_event_time is not None
        ):

            if current_event_time < previous_event_time:

                current_session += 1

                session_reset = True

                previous_counter = None
                previous_event_time = None


        # ----------------------------------------------------
        # SEQUENCE CHECK
        # ----------------------------------------------------

        if current_counter is not None:

            if (
                previous_counter is not None
                and not session_reset
            ):

                expected_counter = (
                    previous_counter
                    + expected_counter_increment
                )

                if (
                    current_counter
                    != expected_counter
                ):

                    reasons.append(
                        "PACKET SEQUENCE ERROR "
                        f"(expected "
                        f"{expected_counter}, "
                        f"received "
                        f"{current_counter})"
                    )

            previous_counter = current_counter


        # ----------------------------------------------------
        # RATE CHECK
        # ----------------------------------------------------

        if current_event_time is not None:

            if (
                previous_event_time is not None
                and not session_reset
            ):

                interval_ms = (
                    current_event_time
                    - previous_event_time
                )

                if (
                    interval_ms > 0
                    and interval_ms
                    < minimum_interval_ms
                ):

                    reasons.append(
                        "HIGH TRAFFIC RATE "
                        f"(interval "
                        f"{interval_ms} ms)"
                    )

            previous_event_time = (
                current_event_time
            )


        # ====================================================
        # DISPLAY FRAME
        # ====================================================

        now = datetime.now().strftime(
            "%H:%M:%S"
        )

        print(
            f"[{now}] Frame "
            f"{frame_number:03d}"
        )

        print(
            f"    CAN ID : {can_id}"
        )

        print(
            f"    DLC    : {dlc}"
        )

        print(
            f"    DATA   : {can_data}"
        )


        # ====================================================
        # NORMAL / ALERT
        # ====================================================

        if len(reasons) == 0:

            print(
                "    STATUS : NORMAL"
            )

        else:

            print(
                "    STATUS : ⚠ ALERT"
            )

            for reason in reasons:

                severity = get_severity(
                    reason
                )

                print(
                    f"    SEVERITY : "
                    f"{severity}"
                )

                print(
                    f"    REASON   : "
                    f"{reason}"
                )

                alert = {

                    "Alert Timestamp":
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "Session":
                        current_session,

                    "Severity":
                        severity,

                    "Frame Number":
                        frame_number,

                    "CAN ID":
                        can_id,

                    "DLC":
                        dlc,

                    "Data Length":
                        data_length,

                    "CAN Data":
                        can_data,

                    "Anomaly Type":
                        reason,

                    "Packet Counter":
                        current_counter,

                    "Event Time (ms)":
                        current_event_time,

                    "Alert Status":
                        "OPEN"
                }

                alerts.append(
                    alert
                )

        print("----------------------------------------------")

        # Small delay to make the monitoring
        # behavior visible during testing.
        time.sleep(0.5)


except KeyboardInterrupt:

    print()
    print(
        "Monitoring stopped by user."
    )


# ============================================================
# SAVE ALERTS
# ============================================================

columns = [
    "Alert Timestamp",
    "Session",
    "Severity",
    "Frame Number",
    "CAN ID",
    "DLC",
    "Data Length",
    "CAN Data",
    "Anomaly Type",
    "Packet Counter",
    "Event Time (ms)",
    "Alert Status"
]


if len(alerts) > 0:

    alert_df = pd.DataFrame(
        alerts,
        columns=columns
    )

else:

    alert_df = pd.DataFrame(
        columns=columns
    )


alert_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("==============================================")
print("          MONITORING SUMMARY")
print("==============================================")

print(
    "Frames analyzed :",
    len(df)
)

print(
    "Alerts generated:",
    len(alerts)
)

print(
    "Alerts saved to :"
)

print(
    OUTPUT_FILE
)

print("----------------------------------------------")

if len(alerts) == 0:

    print(
        "RESULT: NORMAL CAN TRAFFIC"
    )

else:

    print(
        "RESULT: CAN ANOMALIES DETECTED"
    )

print("==============================================")