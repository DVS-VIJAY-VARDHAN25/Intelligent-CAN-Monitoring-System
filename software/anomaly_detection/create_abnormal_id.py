import os
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

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "data",
    "abnormal"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "abnormal_id.csv"
)


# ============================================================
# CREATE ABNORMAL CAN ID DATASET
# ============================================================

rows = []

event_time = 1000

for counter in range(1, 8):

    # Deliberately abnormal CAN ID
    can_id = "0x555"

    # Normal 8-byte payload
    button = "00"

    counter_hex = f"{counter:08X}"

    counter_bytes = [
        counter_hex[0:2],
        counter_hex[2:4],
        counter_hex[4:6],
        counter_hex[6:8]
    ]

    event_hex = f"{event_time:06X}"

    event_bytes = [
        event_hex[0:2],
        event_hex[2:4],
        event_hex[4:6]
    ]

    can_data = " ".join(
        [button] +
        counter_bytes +
        event_bytes
    )

    rows.append({
        "PC Timestamp": event_time,
        "Event Time (ms)": event_time,
        "CAN ID": can_id,
        "DLC": 8,
        "CAN Data": can_data,
        "Button State": "RELEASED",
        "Packet Counter": counter
    })

    event_time += 200


# ============================================================
# SAVE DATASET
# ============================================================

df = pd.DataFrame(rows)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# RESULT
# ============================================================

print("==============================================")
print("       ABNORMAL CAN ID DATASET CREATED")
print("==============================================")
print()

print("Output file:")
print(OUTPUT_FILE)

print()
print("Normal CAN ID : 0x101")
print("Abnormal CAN ID: 0x555")

print()
print("Total frames:")
print(len(df))

print()
print("Dataset created successfully!")