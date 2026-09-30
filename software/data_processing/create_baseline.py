import pandas as pd
import json
from pathlib import Path


# ============================================================
# NORMAL CAN TRAFFIC BASELINE GENERATOR
# ============================================================

print("=" * 60)
print("          NORMAL CAN TRAFFIC BASELINE")
print("=" * 60)
print()


# ------------------------------------------------------------
# PROJECT PATHS
# ------------------------------------------------------------

project_root = Path(__file__).resolve().parents[2]

csv_file = project_root / "can_log.csv"

output_dir = project_root / "data" / "processed"

output_dir.mkdir(
    parents=True,
    exist_ok=True
)

baseline_file = output_dir / "normal_baseline.json"


# ------------------------------------------------------------
# CHECK CSV
# ------------------------------------------------------------

if not csv_file.exists():

    print("ERROR: can_log.csv not found!")
    print(f"Expected location: {csv_file}")

    raise SystemExit


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

df = pd.read_csv(csv_file)

print("Dataset loaded successfully.")
print(f"Total CAN events: {len(df)}")
print()


# ------------------------------------------------------------
# BASIC VALIDATION
# ------------------------------------------------------------

required_columns = [
    "CAN ID",
    "DLC",
    "CAN Data",
    "Button State",
    "Packet Counter",
    "Event Time (ms)"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("ERROR: Missing columns:")

    for column in missing_columns:
        print(f"- {column}")

    raise SystemExit


# ------------------------------------------------------------
# CAN ID BASELINE
# ------------------------------------------------------------

can_ids = (
    df["CAN ID"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


# ------------------------------------------------------------
# DLC BASELINE
# ------------------------------------------------------------

dlc_values = (
    pd.to_numeric(
        df["DLC"],
        errors="coerce"
    )
    .dropna()
    .astype(int)
    .unique()
    .tolist()
)


# ------------------------------------------------------------
# DATA LENGTH BASELINE
# ------------------------------------------------------------

data_lengths = (
    df["CAN Data"]
    .astype(str)
    .apply(
        lambda x: len(x.split())
    )
)

allowed_data_lengths = (
    data_lengths
    .unique()
    .tolist()
)


# ------------------------------------------------------------
# BUTTON STATE BASELINE
# ------------------------------------------------------------

button_states = (
    df["Button State"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


# ------------------------------------------------------------
# EVENT TIMING
# ------------------------------------------------------------

df["Event Time (ms)"] = pd.to_numeric(
    df["Event Time (ms)"],
    errors="coerce"
)

df["Packet Counter"] = pd.to_numeric(
    df["Packet Counter"],
    errors="coerce"
)


# Detect Arduino resets
event_diff = df["Event Time (ms)"].diff()

reset_detected = event_diff < 0

df["Session"] = (
    reset_detected
    .cumsum()
    + 1
)


# Calculate intervals only within sessions
df["Event Interval (ms)"] = (
    df.groupby("Session")[
        "Event Time (ms)"
    ].diff()
)

valid_intervals = (
    df["Event Interval (ms)"]
    .dropna()
)

if len(valid_intervals) > 0:

    average_interval = float(
        valid_intervals.mean()
    )

    minimum_interval = float(
        valid_intervals.min()
    )

    maximum_interval = float(
        valid_intervals.max()
    )

else:

    average_interval = 0
    minimum_interval = 0
    maximum_interval = 0


# ------------------------------------------------------------
# EVENT RATE
# ------------------------------------------------------------

if average_interval > 0:

    average_event_rate = (
        1000 /
        average_interval
    )

else:

    average_event_rate = 0


# ------------------------------------------------------------
# PACKET COUNTER
# ------------------------------------------------------------

packet_diff = (
    df.groupby("Session")[
        "Packet Counter"
    ].diff()
)

valid_packet_diff = (
    packet_diff
    .dropna()
)

normal_packet_increment = 1

if len(valid_packet_diff) > 0:

    normal_packet_increment = int(
        valid_packet_diff.mode().iloc[0]
    )


# ------------------------------------------------------------
# CREATE BASELINE
# ------------------------------------------------------------

baseline = {

    "baseline_name":
        "Normal CAN Traffic Baseline",

    "version":
        "1.0",

    "source_dataset":
        "can_log.csv",

    "total_frames":
        int(len(df)),

    "can_ids":
        can_ids,

    "allowed_dlc":
        dlc_values,

    "allowed_data_lengths":
        allowed_data_lengths,

    "allowed_button_states":
        button_states,

    "timing": {

        "average_interval_ms":
            round(
                average_interval,
                2
            ),

        "minimum_interval_ms":
            round(
                minimum_interval,
                2
            ),

        "maximum_interval_ms":
            round(
                maximum_interval,
                2
            ),

        "average_event_rate_per_second":
            round(
                average_event_rate,
                4
            )
    },

    "packet_counter": {

        "expected_increment":
            normal_packet_increment
    }

}


# ------------------------------------------------------------
# SAVE BASELINE
# ------------------------------------------------------------

with open(
    baseline_file,
    "w"
) as file:

    json.dump(
        baseline,
        file,
        indent=4
    )


# ------------------------------------------------------------
# DISPLAY BASELINE
# ------------------------------------------------------------

print("-" * 60)
print("NORMAL CAN BASELINE")
print("-" * 60)

print()
print("Allowed CAN IDs:")

for can_id in can_ids:
    print(f"  {can_id}")

print()

print("Allowed DLC values:")

for dlc in dlc_values:
    print(f"  {dlc}")

print()

print("Allowed data lengths:")

for length in allowed_data_lengths:
    print(f"  {length} byte(s)")

print()

print("Allowed button states:")

for state in button_states:
    print(f"  {state}")

print()

print("Timing baseline:")

print(
    f"  Average interval : "
    f"{average_interval:.2f} ms"
)

print(
    f"  Minimum interval : "
    f"{minimum_interval:.2f} ms"
)

print(
    f"  Maximum interval : "
    f"{maximum_interval:.2f} ms"
)

print(
    f"  Average rate     : "
    f"{average_event_rate:.4f} events/sec"
)

print()

print("Packet counter:")

print(
    f"  Expected increment : "
    f"{normal_packet_increment}"
)

print()


# ------------------------------------------------------------
# FINAL
# ------------------------------------------------------------

print("=" * 60)

print("NORMAL BASELINE CREATED SUCCESSFULLY.")

print()
print(f"Saved to:")
print(baseline_file)

print("=" * 60)
