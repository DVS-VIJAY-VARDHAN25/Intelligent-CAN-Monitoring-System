import pandas as pd
import numpy as np
from pathlib import Path


# ============================================================
# CAN TRAFFIC ANALYZER V3
# SESSION-AWARE CAN TRAFFIC ANALYSIS
# ============================================================

print("=" * 60)
print("             CAN TRAFFIC ANALYZER V3")
print("          SESSION-AWARE CAN ANALYSIS")
print("=" * 60)
print()


# ------------------------------------------------------------
# LOAD CSV
# ------------------------------------------------------------

project_root = Path(__file__).resolve().parents[2]
csv_file = project_root / "can_log.csv"

if not csv_file.exists():
    print("ERROR: can_log.csv not found!")
    print(f"Expected location: {csv_file}")
    raise SystemExit

df = pd.read_csv(csv_file)

print("Dataset loaded successfully.")
print(f"Total logged CAN events: {len(df)}")
print()


# ------------------------------------------------------------
# CHECK REQUIRED COLUMNS
# ------------------------------------------------------------

required_columns = [
    "PC Timestamp",
    "Event Time (ms)",
    "CAN ID",
    "DLC",
    "CAN Data",
    "Button State",
    "Packet Counter"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    print("ERROR: Missing required columns:")
    for column in missing_columns:
        print(f"- {column}")
    raise SystemExit


# ------------------------------------------------------------
# CONVERT DATA TYPES
# ------------------------------------------------------------

df["PC Timestamp"] = pd.to_datetime(
    df["PC Timestamp"],
    errors="coerce"
)

df["Event Time (ms)"] = pd.to_numeric(
    df["Event Time (ms)"],
    errors="coerce"
)

df["Packet Counter"] = pd.to_numeric(
    df["Packet Counter"],
    errors="coerce"
)

df["DLC"] = pd.to_numeric(
    df["DLC"],
    errors="coerce"
)


# ------------------------------------------------------------
# SESSION DETECTION
# ------------------------------------------------------------
#
# A new session is detected when:
#
# 1. Arduino Event Time decreases
# OR
# 2. Packet Counter decreases
#
# This normally means the Arduino restarted.
# ------------------------------------------------------------

event_time_diff = df["Event Time (ms)"].diff()
packet_diff = df["Packet Counter"].diff()

arduino_reset = (
    (event_time_diff < 0) |
    (packet_diff < 0)
)

# First row always belongs to Session 1
df["Session"] = arduino_reset.cumsum() + 1


# ------------------------------------------------------------
# 1. BASIC DATASET INFORMATION
# ------------------------------------------------------------

print("-" * 60)
print("1. BASIC DATASET INFORMATION")
print("-" * 60)

print(f"Total CAN frames : {len(df)}")
print(f"Unique CAN IDs   : {df['CAN ID'].nunique()}")
print(f"Testing sessions : {df['Session'].nunique()}")

print()


# ------------------------------------------------------------
# 2. SESSION ANALYSIS
# ------------------------------------------------------------

print("-" * 60)
print("2. SESSION ANALYSIS")
print("-" * 60)

for session_number, session_data in df.groupby("Session"):

    print(
        f"Session {session_number} : "
        f"{len(session_data)} event(s)"
    )

    first_time = session_data["PC Timestamp"].iloc[0]
    last_time = session_data["PC Timestamp"].iloc[-1]

    print(f"  Start : {first_time}")
    print(f"  End   : {last_time}")

    print()


# ------------------------------------------------------------
# 3. CAN ID ANALYSIS
# ------------------------------------------------------------

print("-" * 60)
print("3. CAN ID ANALYSIS")
print("-" * 60)

id_counts = df["CAN ID"].value_counts()

for can_id, count in id_counts.items():
    print(f"CAN ID {can_id} : {count} frame(s)")

print()


# ------------------------------------------------------------
# 4. DLC ANALYSIS
# ------------------------------------------------------------

print("-" * 60)
print("4. DLC ANALYSIS")
print("-" * 60)

dlc_counts = df["DLC"].value_counts()

for dlc, count in dlc_counts.items():
    print(f"DLC {dlc} : {count} frame(s)")

print()


# ------------------------------------------------------------
# 5. BUTTON EVENT ANALYSIS
# ------------------------------------------------------------

print("-" * 60)
print("5. BUTTON EVENT ANALYSIS")
print("-" * 60)

pressed = (
    df["Button State"] == "PRESSED"
).sum()

released = (
    df["Button State"] == "RELEASED"
).sum()

print(f"PRESSED  : {pressed} event(s)")
print(f"RELEASED : {released} event(s)")

print()
print(f"Total button presses  : {pressed}")
print(f"Total button releases : {released}")

print()


# ------------------------------------------------------------
# 6. SESSION-AWARE PC TIMING
# ------------------------------------------------------------

print("-" * 60)
print("6. SESSION-AWARE PC TIMING ANALYSIS")
print("-" * 60)

# Calculate PC timestamp differences
# separately for each session.

df["PC Interval (ms)"] = (
    df.groupby("Session")["PC Timestamp"]
    .diff()
    .dt.total_seconds()
    * 1000
)

pc_intervals = df["PC Interval (ms)"].dropna()

if len(pc_intervals) > 0:

    print(
        f"Average interval     : "
        f"{pc_intervals.mean():.2f} ms"
    )

    print(
        f"Minimum interval     : "
        f"{pc_intervals.min():.2f} ms"
    )

    print(
        f"Maximum interval     : "
        f"{pc_intervals.max():.2f} ms"
    )

    print(
        f"Standard deviation   : "
        f"{pc_intervals.std():.2f} ms"
    )

    print()
    print(
        "Session-to-session gaps "
        "were excluded from timing analysis."
    )

else:

    print("Not enough data for timing analysis.")

print()


# ------------------------------------------------------------
# 7. EMBEDDED EVENT TIME ANALYSIS
# ------------------------------------------------------------

print("-" * 60)
print("7. EMBEDDED EVENT TIME ANALYSIS")
print("-" * 60)

# Calculate embedded timing separately
# inside every session.

df["Embedded Interval (ms)"] = (
    df.groupby("Session")["Event Time (ms)"]
    .diff()
)

embedded_intervals = (
    df["Embedded Interval (ms)"]
    .dropna()
)

if len(embedded_intervals) > 0:

    print(
        f"Average interval     : "
        f"{embedded_intervals.mean():.2f} ms"
    )

    print(
        f"Minimum interval     : "
        f"{embedded_intervals.min():.2f} ms"
    )

    print(
        f"Maximum interval     : "
        f"{embedded_intervals.max():.2f} ms"
    )

else:

    print("Not enough data for embedded timing analysis.")

print()


# ------------------------------------------------------------
# 8. PACKET COUNTER ANALYSIS
# ------------------------------------------------------------

print("-" * 60)
print("8. PACKET COUNTER ANALYSIS")
print("-" * 60)

missing_count = 0
duplicate_count = 0

for session_number, session_data in df.groupby("Session"):

    counters = (
        session_data["Packet Counter"]
        .dropna()
        .astype(int)
        .tolist()
    )

    if len(counters) == 0:
        continue

    print(
        f"Session {session_number}: "
        f"{counters[0]} → {counters[-1]}"
    )

    for i in range(1, len(counters)):

        difference = counters[i] - counters[i - 1]

        if difference == 1:
            continue

        elif difference == 0:
            duplicate_count += 1

        elif difference > 1:
            missing_count += difference - 1


print()
print(f"Missing counters   : {missing_count}")
print(f"Duplicate counters : {duplicate_count}")

if missing_count == 0:
    print("Packet continuity  : NO MISSING COUNTERS")
else:
    print("Packet continuity  : MISSING COUNTERS DETECTED")

print()


# ------------------------------------------------------------
# 9. CAN DATA LENGTH ANALYSIS
# ------------------------------------------------------------

print("-" * 60)
print("9. CAN DATA LENGTH ANALYSIS")
print("-" * 60)

data_lengths = (
    df["CAN Data"]
    .astype(str)
    .apply(lambda x: len(x.split()))
)

print(
    f"Average data bytes : "
    f"{data_lengths.mean():.2f}"
)

print(
    f"Minimum data bytes : "
    f"{data_lengths.min()}"
)

print(
    f"Maximum data bytes : "
    f"{data_lengths.max()}"
)

print()


# ------------------------------------------------------------
# 10. CAN BUS HEALTH CHECK
# ------------------------------------------------------------

print("-" * 60)
print("10. CAN BUS HEALTH CHECK")
print("-" * 60)

issues = []

# Check DLC
if (df["DLC"] < 0).any() or (df["DLC"] > 8).any():
    issues.append("Invalid DLC detected")

# Check data length
invalid_data_length = (
    data_lengths != df["DLC"]
).any()

if invalid_data_length:
    issues.append("DLC/data length mismatch detected")

# Check missing packets
if missing_count > 0:
    issues.append("Missing packet counters detected")

# Report
if issues:

    print("Potential issues detected:")

    for issue in issues:
        print(f"- {issue}")

else:

    print("No basic CAN data integrity issues detected.")

print()


# ------------------------------------------------------------
# 11. EVENT RATE
# ------------------------------------------------------------

print("-" * 60)
print("11. EVENT RATE")
print("-" * 60)

for session_number, session_data in df.groupby("Session"):

    if len(session_data) < 2:
        print(
            f"Session {session_number}: "
            "Not enough events"
        )
        continue

    start = session_data["PC Timestamp"].iloc[0]
    end = session_data["PC Timestamp"].iloc[-1]

    duration_seconds = (
        end - start
    ).total_seconds()

    if duration_seconds > 0:

        rate = (
            len(session_data) /
            duration_seconds
        )

        print(
            f"Session {session_number}: "
            f"{rate:.3f} events/second"
        )

    else:

        print(
            f"Session {session_number}: "
            "Unable to calculate"
        )

print()


# ------------------------------------------------------------
# FINAL SUMMARY
# ------------------------------------------------------------

print("=" * 60)
print("                    ANALYSIS SUMMARY")
print("=" * 60)

print(f"Total CAN frames     : {len(df)}")
print(f"Unique CAN IDs       : {df['CAN ID'].nunique()}")
print(f"Testing sessions     : {df['Session'].nunique()}")
print(f"Button presses       : {pressed}")
print(f"Button releases      : {released}")
print(f"Missing counters     : {missing_count}")
print(f"Duplicate counters   : {duplicate_count}")

if len(pc_intervals) > 0:

    print(
        f"Average event gap   : "
        f"{pc_intervals.mean():.2f} ms"
    )

print()
print("CAN Traffic Analysis V3 Complete.")
print("=" * 60)