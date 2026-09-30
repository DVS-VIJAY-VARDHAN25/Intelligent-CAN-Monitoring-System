import os
import json
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
    "data",
    "abnormal",
    "abnormal_payload.csv"
)


# ============================================================
# HEADER
# ============================================================

print("==============================================")
print("       CAN IDS — PAYLOAD ANOMALY TEST")
print("==============================================")
print()


# ============================================================
# LOAD BASELINE
# ============================================================

print("Loading normal baseline...")

with open(
    BASELINE_FILE,
    "r"
) as file:

    baseline = json.load(file)

print("Baseline loaded successfully.")
print()


# ============================================================
# NORMAL PAYLOAD PARAMETERS
# ============================================================

allowed_button_states = set(
    baseline["allowed_button_states"]
)

print("Normal payload configuration:")
print("----------------------------------------------")

print(
    "Allowed button states:",
    allowed_button_states
)

print("----------------------------------------------")
print()


# ============================================================
# LOAD DATA
# ============================================================

print("Loading abnormal payload data...")

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

payload_anomalies = 0
total_anomalies = 0


# ============================================================
# FRAME ANALYSIS
# ============================================================

print("==============================================")
print("             FRAME ANALYSIS")
print("==============================================")


for index, row in df.iterrows():

    frame_number = index + 1

    reasons = []


    # --------------------------------------------------------
    # READ CAN DATA
    # --------------------------------------------------------

    can_data = str(
        row["CAN Data"]
    ).strip()

    data_bytes = can_data.split()


    # --------------------------------------------------------
    # PAYLOAD CHECK
    #
    # Byte 0 = Button state
    #
    # 00 = RELEASED
    # 01 = PRESSED
    # --------------------------------------------------------

    if len(data_bytes) >= 1:

        button_byte = data_bytes[0].upper()

        if button_byte not in [
            "00",
            "01"
        ]:

            reasons.append(
                "INVALID PAYLOAD "
                f"(button byte = {button_byte})"
            )

            payload_anomalies += 1


    else:

        reasons.append(
            "EMPTY PAYLOAD"
        )

        payload_anomalies += 1


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
                f"              └─ {reason}"
            )


# ============================================================
# SUMMARY
# ============================================================

print()
print("==============================================")
print("            PAYLOAD TEST SUMMARY")
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
    "Payload anomalies     :",
    payload_anomalies
)

print("----------------------------------------------")


if total_anomalies > 0:

    print(
        "RESULT: PAYLOAD ANOMALY DETECTED"
    )

else:

    print(
        "RESULT: NO PAYLOAD ANOMALIES DETECTED"
    )

print("==============================================")