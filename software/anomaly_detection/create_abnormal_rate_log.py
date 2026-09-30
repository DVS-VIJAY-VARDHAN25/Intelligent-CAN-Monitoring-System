import os
import csv
import time


# ============================================================
# CONFIGURATION
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

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "abnormal_rate.csv"
)


# ============================================================
# SETTINGS
# ============================================================

TOTAL_FRAMES = 100
INTERVAL_MS = 5


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# HEADER
# ============================================================

print("==============================================")
print("       ABNORMAL RATE DATA GENERATOR")
print("==============================================")

print()
print("Frames        :", TOTAL_FRAMES)
print("Interval      :", INTERVAL_MS, "ms")
print(
    "Target rate   :",
    1000 / INTERVAL_MS,
    "frames/sec"
)
print()


# ============================================================
# CREATE CSV
# ============================================================

with open(
    OUTPUT_FILE,
    "w",
    newline=""
) as file:

    writer = csv.writer(file)

    writer.writerow([
        "PC Timestamp",
        "Event Time (ms)",
        "CAN ID",
        "DLC",
        "CAN Data",
        "Button State",
        "Packet Counter"
    ])

    event_time = 0

    start_time = time.time()

    for counter in range(
        1,
        TOTAL_FRAMES + 1
    ):

        # ----------------------------------------------------
        # CAN PAYLOAD
        #
        # Byte 0      = Button state
        # Bytes 1-4   = packet counter
        # Bytes 5-7   = event time
        # ----------------------------------------------------

        button_state = "RELEASED"

        button_byte = "00"

        counter_hex = counter.to_bytes(
            4,
            byteorder="big"
        )

        time_hex = event_time.to_bytes(
            3,
            byteorder="big"
        )

        data = [
            button_byte,
            f"{counter_hex[0]:02X}",
            f"{counter_hex[1]:02X}",
            f"{counter_hex[2]:02X}",
            f"{counter_hex[3]:02X}",
            f"{time_hex[0]:02X}",
            f"{time_hex[1]:02X}",
            f"{time_hex[2]:02X}"
        ]

        can_data = " ".join(data)

        # ----------------------------------------------------
        # WRITE ROW
        # ----------------------------------------------------

        writer.writerow([
            time.time(),
            event_time,
            "0x101",
            8,
            can_data,
            button_state,
            counter
        ])

        event_time += INTERVAL_MS

        time.sleep(
            INTERVAL_MS / 1000
        )


elapsed = time.time() - start_time

actual_rate = (
    TOTAL_FRAMES / elapsed
)


# ============================================================
# RESULT
# ============================================================

print()
print("==============================================")
print("             GENERATION COMPLETE")
print("==============================================")

print(
    "Frames generated :",
    TOTAL_FRAMES
)

print(
    "Target interval  :",
    INTERVAL_MS,
    "ms"
)

print(
    "Target rate      :",
    1000 / INTERVAL_MS,
    "frames/sec"
)

print(
    "Actual generation rate :",
    round(actual_rate, 2),
    "frames/sec"
)

print()
print("Output file:")
print(OUTPUT_FILE)

print("==============================================")