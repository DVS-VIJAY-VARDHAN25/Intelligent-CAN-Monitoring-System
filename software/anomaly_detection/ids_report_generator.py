import os
import json
from datetime import datetime
import pandas as pd


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

BASELINE_FILE = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "normal_baseline.json"
)

CSV_FILE = os.path.join(
    BASE_DIR,
    "can_log.csv"
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "processed"
)

REPORT_FILE = os.path.join(
    REPORT_DIR,
    "ids_report.json"
)


# ============================================================
# HEADER
# ============================================================

print("==============================================")
print("       CAN IDS AUTOMATED REPORT GENERATOR")
print("                    V1.0")
print("==============================================")
print()


# ============================================================
# LOAD BASELINE
# ============================================================

print("Loading normal baseline...")

if not os.path.exists(BASELINE_FILE):
    print("ERROR: normal_baseline.json not found!")
    print(BASELINE_FILE)
    exit()

with open(
    BASELINE_FILE,
    "r"
) as file:

    baseline = json.load(file)

print("Baseline loaded successfully.")
print()


# ============================================================
# BASELINE PARAMETERS
# ============================================================

allowed_ids = set(
    baseline["can_ids"]
)

allowed_dlc = set(
    baseline["allowed_dlc"]
)

allowed_data_lengths = set(
    baseline["allowed_data_lengths"]
)

allowed_button_states = set(
    baseline["allowed_button_states"]
)

expected_counter_increment = (
    baseline["packet_counter"]
    ["expected_increment"]
)

minimum_interval_ms = (
    baseline["timing"]
    ["minimum_interval_ms"]
)


# ============================================================
# LOAD CAN LOG
# ============================================================

print("Loading CAN log...")

if not os.path.exists(CSV_FILE):
    print("ERROR: can_log.csv not found!")
    print(CSV_FILE)
    exit()

df = pd.read_csv(
    CSV_FILE
)

print("CAN log loaded successfully.")
print(
    "Total frames:",
    len(df)
)
print()


# ============================================================
# COUNTERS
# ============================================================

total_anomalous_frames = 0

can_id_anomalies = 0
dlc_anomalies = 0
data_length_anomalies = 0
payload_anomalies = 0
sequence_anomalies = 0
rate_anomalies = 0


# ============================================================
# STATE
# ============================================================

previous_counter = None
previous_event_time = None


# ============================================================
# ANOMALOUS FRAME DETAILS
# ============================================================

anomaly_details = []


# ============================================================
# FRAME ANALYSIS
# ============================================================

print("==============================================")
print("             FRAME ANALYSIS")
print("==============================================")


for index, row in df.iterrows():

    frame_number = index + 1

    reasons = []


    # ========================================================
    # CAN ID CHECK
    # ========================================================

    can_id = str(
        row["CAN ID"]
    ).strip()

    if can_id not in allowed_ids:

        reasons.append(
            "UNEXPECTED CAN ID"
        )

        can_id_anomalies += 1


    # ========================================================
    # DLC CHECK
    # ========================================================

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

        dlc_anomalies += 1


    # ========================================================
    # DATA LENGTH CHECK
    # ========================================================

    can_data = str(
        row["CAN Data"]
    ).strip()

    data_bytes = can_data.split()

    data_length = len(
        data_bytes
    )

    if data_length not in allowed_data_lengths:

        reasons.append(
            "UNEXPECTED DATA LENGTH"
        )

        data_length_anomalies += 1


    # ========================================================
    # PAYLOAD CHECK
    # ========================================================

    if data_length >= 1:

        button_byte = (
            data_bytes[0].upper()
        )

        if button_byte == "00":

            payload_button_state = "RELEASED"

        elif button_byte == "01":

            payload_button_state = "PRESSED"

        else:

            payload_button_state = "INVALID"

            reasons.append(
                "INVALID PAYLOAD "
                f"(button byte = {button_byte})"
            )

            payload_anomalies += 1

    else:

        payload_button_state = "INVALID"

        reasons.append(
            "EMPTY PAYLOAD"
        )

        payload_anomalies += 1


    # ========================================================
    # PACKET COUNTER
    # ========================================================

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


    # ========================================================
    # SEQUENCE CHECK
    # ========================================================

    if current_counter is not None:

        if previous_counter is not None:

            expected_counter = (
                previous_counter
                + expected_counter_increment
            )

            if current_counter != expected_counter:

                reasons.append(
                    "PACKET SEQUENCE ERROR "
                    f"(expected {expected_counter}, "
                    f"received {current_counter})"
                )

                sequence_anomalies += 1

        previous_counter = current_counter


    # ========================================================
    # EVENT TIME
    # ========================================================

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


    # ========================================================
    # RATE CHECK
    # ========================================================

    if current_event_time is not None:

        if previous_event_time is not None:

            interval_ms = (
                current_event_time
                - previous_event_time
            )

            if interval_ms > 0:

                if interval_ms < minimum_interval_ms:

                    reasons.append(
                        "HIGH TRAFFIC RATE "
                        f"(interval {interval_ms} ms)"
                    )

                    rate_anomalies += 1

        previous_event_time = current_event_time


    # ========================================================
    # FRAME RESULT
    # ========================================================

    if len(reasons) == 0:

        print(
            f"Frame {frame_number:3d} → NORMAL"
        )

    else:

        total_anomalous_frames += 1

        print(
            f"Frame {frame_number:3d} → ANOMALY"
        )

        for reason in reasons:

            print(
                f"              └─ {reason}"
            )


        # ----------------------------------------------------
        # SAVE ANOMALY DETAILS
        # ----------------------------------------------------

        anomaly_details.append({

            "frame_number": frame_number,

            "can_id": can_id,

            "dlc": dlc,

            "can_data": can_data,

            "button_state": str(
                row["Button State"]
            ),

            "packet_counter": current_counter,

            "event_time_ms": current_event_time,

            "reasons": reasons

        })


# ============================================================
# CALCULATE STATISTICS
# ============================================================

total_frames = len(df)

if total_frames > 0:

    anomaly_percentage = (
        total_anomalous_frames
        / total_frames
    ) * 100

else:

    anomaly_percentage = 0


# ============================================================
# FINAL RESULT
# ============================================================

if total_anomalous_frames == 0:

    final_result = "NORMAL"

else:

    final_result = "ANOMALIES DETECTED"


# ============================================================
# CREATE REPORT
# ============================================================

report = {

    "report_information": {

        "report_version": "1.0",

        "generated_at": datetime.now().isoformat(),

        "source_file": "can_log.csv",

        "baseline_file":
            "data/processed/normal_baseline.json"

    },


    "analysis_summary": {

        "total_frames": total_frames,

        "total_anomalous_frames":
            total_anomalous_frames,

        "anomaly_percentage":
            round(
                anomaly_percentage,
                2
            ),

        "result": final_result

    },


    "anomaly_breakdown": {

        "can_id_anomalies":
            can_id_anomalies,

        "dlc_anomalies":
            dlc_anomalies,

        "data_length_anomalies":
            data_length_anomalies,

        "payload_anomalies":
            payload_anomalies,

        "sequence_anomalies":
            sequence_anomalies,

        "rate_anomalies":
            rate_anomalies

    },


    "anomalous_frames":
        anomaly_details

}


# ============================================================
# SAVE REPORT
# ============================================================

os.makedirs(
    REPORT_DIR,
    exist_ok=True
)

with open(
    REPORT_FILE,
    "w"
) as file:

    json.dump(
        report,
        file,
        indent=4
    )


# ============================================================
# DISPLAY SUMMARY
# ============================================================

print()
print("==============================================")
print("          IDS ANALYSIS SUMMARY")
print("==============================================")

print(
    "Total frames analyzed :",
    total_frames
)

print(
    "Total anomalous frames:",
    total_anomalous_frames
)

print(
    "Anomaly percentage    :",
    round(
        anomaly_percentage,
        2
    ),
    "%"
)

print()

print("ANOMALY BREAKDOWN")
print("----------------------------------------------")

print(
    "CAN ID anomalies      :",
    can_id_anomalies
)

print(
    "DLC anomalies         :",
    dlc_anomalies
)

print(
    "Data length anomalies :",
    data_length_anomalies
)

print(
    "Payload anomalies     :",
    payload_anomalies
)

print(
    "Sequence anomalies    :",
    sequence_anomalies
)

print(
    "Rate anomalies        :",
    rate_anomalies
)

print("----------------------------------------------")

print(
    "RESULT:",
    final_result
)

print()
print("Report saved to:")
print(REPORT_FILE)

print("==============================================")