import os
import json
import pandas as pd


# ============================================================
# PATHS
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
    "data",
    "abnormal",
    "abnormal_rate.csv"
)


# ============================================================
# LOAD BASELINE
# ============================================================

with open(
    BASELINE_FILE,
    "r"
) as file:

    baseline = json.load(file)


minimum_interval_ms = (
    baseline["timing"]["minimum_interval_ms"]
)

expected_counter_increment = (
    baseline["packet_counter"]["expected_increment"]
)


# ============================================================
# LOAD ABNORMAL DATA
# ============================================================

df = pd.read_csv(
    CSV_FILE
)


# ============================================================
# HEADER
# ============================================================

print("==============================================")
print("       CAN IDS — ABNORMAL RATE TEST")
print("==============================================")

print()
print(
    "Normal minimum interval:",
    minimum_interval_ms,
    "ms"
)

print(
    "Abnormal interval      :",
    "5 ms"
)

print()


# ============================================================
# ANALYSIS
# ============================================================

previous_event_time = None
previous_counter = None

rate_anomalies = 0
sequence_anomalies = 0
total_anomalies = 0


print("==============================================")
print("             FRAME ANALYSIS")
print("==============================================")


for index, row in df.iterrows():

    frame_number = index + 1

    reasons = []


    # --------------------------------------------------------
    # CAN DATA
    # --------------------------------------------------------

    can_data = str(
        row["CAN Data"]
    ).strip()

    data_bytes = can_data.split()


    # --------------------------------------------------------
    # PACKET COUNTER
    # --------------------------------------------------------

    current_counter = int(
        "".join(
            data_bytes[1:5]
        ),
        16
    )


    # --------------------------------------------------------
    # EVENT TIME
    # --------------------------------------------------------

    current_event_time = int(
        "".join(
            data_bytes[5:8]
        ),
        16
    )


    # --------------------------------------------------------
    # SEQUENCE CHECK
    # --------------------------------------------------------

    if previous_counter is not None:

        expected_counter = (
            previous_counter
            + expected_counter_increment
        )

        if current_counter != expected_counter:

            reasons.append(
                f"PACKET SEQUENCE ERROR "
                f"(expected {expected_counter}, "
                f"received {current_counter})"
            )

            sequence_anomalies += 1


    previous_counter = current_counter


    # --------------------------------------------------------
    # RATE CHECK
    # --------------------------------------------------------

    if previous_event_time is not None:

        interval_ms = (
            current_event_time
            - previous_event_time
        )

        if interval_ms < minimum_interval_ms:

            reasons.append(
                f"HIGH TRAFFIC RATE "
                f"(interval {interval_ms} ms)"
            )

            rate_anomalies += 1

    previous_event_time = current_event_time


    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    if len(reasons) == 0:

        print(
            f"Frame {frame_number:3d} → NORMAL"
        )

    else:

        total_anomalies += 1

        print(
            f"Frame {frame_number:3d} → ANOMALY"
        )

        for reason in reasons:

            print(
                "              └─",
                reason
            )


# ============================================================
# SUMMARY
# ============================================================

print()
print("==============================================")
print("            ANOMALY TEST SUMMARY")
print("==============================================")

print(
    "Total frames analyzed :",
    len(df)
)

print(
    "Total anomalous frames:",
    total_anomalies
)

print(
    "Rate anomalies        :",
    rate_anomalies
)

print(
    "Sequence anomalies    :",
    sequence_anomalies
)

print("----------------------------------------------")

if total_anomalies > 0:

    print(
        "RESULT: HIGH-RATE TRAFFIC DETECTED"
    )

else:

    print(
        "RESULT: NO ANOMALIES DETECTED"
    )

print("==============================================")