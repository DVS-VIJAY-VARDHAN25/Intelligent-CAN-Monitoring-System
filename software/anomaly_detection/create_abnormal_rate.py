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
    "abnormal_rate.csv"
)


# ============================================================
# CREATE ABNORMAL HIGH-RATE DATASET
# ============================================================

rows = []

number_of_frames = 100

# Deliberately very small interval
interval_ms = 5

event_time = 1000


for counter in range(1, number_of_frames + 1):

    # Normal CAN ID
    can_id = "0x101"

    # Normal button state
    button = "00"

    # 4-byte packet counter
    counter_hex = f"{counter:08X}"

    counter_bytes = [
        counter_hex[0:2],
        counter_hex[2:4],
        counter_hex[4:6],
        counter_hex[6:8]
    ]

    # 3-byte event time
    event_hex = f"{event_time:06X}"

    event_bytes = [
        event_hex[0:2],
        event_hex[2:4],
        event_hex[4:6]
    ]

    # 8-byte CAN payload
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

    # Next frame arrives after only 5 ms
    event_time += interval_ms


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
print("       ABNORMAL RATE DATASET CREATED")
print("==============================================")
print()

print("Output file:")
print(OUTPUT_FILE)

print()
print("Number of frames :", number_of_frames)
print("Frame interval   :", interval_ms, "ms")
print("Approximate rate :", 1000 / interval_ms, "frames/sec")

print()
print("Normal minimum interval :", 146, "ms")

print()
print("Dataset created successfully!")