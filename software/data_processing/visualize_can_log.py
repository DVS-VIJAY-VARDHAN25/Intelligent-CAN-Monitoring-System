import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# CAN TRAFFIC VISUALIZER V1
# ============================================================

print("=" * 60)
print("             CAN TRAFFIC VISUALIZER")
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
print(f"Total CAN events: {len(df)}")
print()


# ------------------------------------------------------------
# CONVERT DATA
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


# ------------------------------------------------------------
# CREATE SESSION DETECTION
# ------------------------------------------------------------

event_diff = df["Event Time (ms)"].diff()
packet_diff = df["Packet Counter"].diff()

reset_detected = (
    (event_diff < 0) |
    (packet_diff < 0)
)

df["Session"] = reset_detected.cumsum() + 1


# ------------------------------------------------------------
# CREATE OUTPUT DIRECTORY
# ------------------------------------------------------------

output_dir = project_root / "data" / "processed"

output_dir.mkdir(
    parents=True,
    exist_ok=True
)

print(f"Output directory: {output_dir}")
print()


# ============================================================
# GRAPH 1 — CAN EVENTS OVER TIME
# ============================================================

print("Generating Graph 1...")

plt.figure(figsize=(10, 5))

for session, session_data in df.groupby("Session"):

    plt.plot(
        session_data["PC Timestamp"],
        session_data["Packet Counter"],
        marker="o",
        linestyle="-",
        label=f"Session {session}"
    )

plt.xlabel("PC Timestamp")
plt.ylabel("Packet Counter")
plt.title("CAN Packet Activity Over Time")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

graph1 = output_dir / "can_packet_activity.png"

plt.savefig(graph1, dpi=300)
plt.show()

print(f"Saved: {graph1}")
print()


# ============================================================
# GRAPH 2 — BUTTON EVENTS
# ============================================================

print("Generating Graph 2...")

plt.figure(figsize=(10, 5))

button_values = (
    df["Button State"]
    .map({
        "RELEASED": 0,
        "PRESSED": 1
    })
)

plt.step(
    df["PC Timestamp"],
    button_values,
    where="post"
)

plt.xlabel("PC Timestamp")
plt.ylabel("Button State")
plt.yticks(
    [0, 1],
    ["RELEASED", "PRESSED"]
)

plt.title("CAN Button Events Over Time")
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

graph2 = output_dir / "button_events.png"

plt.savefig(graph2, dpi=300)
plt.show()

print(f"Saved: {graph2}")
print()


# ============================================================
# GRAPH 3 — EMBEDDED EVENT INTERVAL
# ============================================================

print("Generating Graph 3...")

df["Event Interval (ms)"] = (
    df.groupby("Session")["Event Time (ms)"]
    .diff()
)

plt.figure(figsize=(10, 5))

for session, session_data in df.groupby("Session"):

    valid_data = session_data.dropna(
        subset=["Event Interval (ms)"]
    )

    if len(valid_data) > 0:

        plt.plot(
            valid_data["PC Timestamp"],
            valid_data["Event Interval (ms)"],
            marker="o",
            linestyle="-",
            label=f"Session {session}"
        )

plt.xlabel("PC Timestamp")
plt.ylabel("Interval (ms)")
plt.title("CAN Event Interval")
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

graph3 = output_dir / "event_interval.png"

plt.savefig(graph3, dpi=300)
plt.show()

print(f"Saved: {graph3}")
print()


# ============================================================
# GRAPH 4 — PACKET COUNTER
# ============================================================

print("Generating Graph 4...")

plt.figure(figsize=(10, 5))

for session, session_data in df.groupby("Session"):

    plt.plot(
        session_data["Packet Counter"],
        marker="o",
        linestyle="-",
        label=f"Session {session}"
    )

plt.xlabel("Event Number")
plt.ylabel("Packet Counter")
plt.title("CAN Packet Counter Sequence")
plt.legend()
plt.grid(True)
plt.tight_layout()

graph4 = output_dir / "packet_counter.png"

plt.savefig(graph4, dpi=300)
plt.show()

print(f"Saved: {graph4}")
print()


# ============================================================
# GRAPH 5 — CAN ID DISTRIBUTION
# ============================================================

print("Generating Graph 5...")

id_counts = df["CAN ID"].value_counts()

plt.figure(figsize=(8, 5))

plt.bar(
    id_counts.index.astype(str),
    id_counts.values
)

plt.xlabel("CAN ID")
plt.ylabel("Number of Frames")
plt.title("CAN ID Distribution")
plt.grid(axis="y")

plt.tight_layout()

graph5 = output_dir / "can_id_distribution.png"

plt.savefig(graph5, dpi=300)
plt.show()

print(f"Saved: {graph5}")
print()


# ============================================================
# FINAL
# ============================================================

print("=" * 60)
print("              VISUALIZATION COMPLETE")
print("=" * 60)
print()

print("Generated graphs:")

print("1. can_packet_activity.png")
print("2. button_events.png")
print("3. event_interval.png")
print("4. packet_counter.png")
print("5. can_id_distribution.png")

print()
print(f"Location: {output_dir}")
print("=" * 60)