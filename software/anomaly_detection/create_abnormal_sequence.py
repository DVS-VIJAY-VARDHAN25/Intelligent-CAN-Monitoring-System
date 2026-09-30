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
    "abnormal_sequence.csv"
)


# ============================================================
# CREATE ABNORMAL SEQUENCE DATA
# ============================================================

# Packet 4 is intentionally missing.
packet_counters = [
    1,
    2,
    3,
    5,
    6,
    7,
    8
]

rows = []

event_time = 1000

for counter in packet_counters:

    # Button byte = 00 (RELEASED)
    button = "00"

    # Counter = 4 bytes
    counter_hex = f"{counter:08X}"

    counter_bytes = [
        counter_hex[0:2],
        counter_hex[2:4],
        counter_hex[4:6],
        counter_hex[6:8]
    ]

    # Event time = 3 bytes
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
        "CAN ID": "0x101",
        "DLC": 8,
        "CAN Data": can_data,
        "Button State": "RELEASED",
        "Packet Counter": counter
    })

    event_time += 200


# ============================================================
# SAVE CSV
# ============================================================

df = pd.DataFrame(rows)

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("==============================================")
print("     ABNORMAL SEQUENCE DATASET CREATED")
print("==============================================")
print()

print("Output file:")
print(OUTPUT_FILE)

print()
print("Packet sequence:")
print("1 → 2 → 3 → 5 → 6 → 7 → 8")

print()
print("Missing packet:")
print("4")

print()
print("Total frames:")
print(len(df))

print()
print("Dataset created successfully!")