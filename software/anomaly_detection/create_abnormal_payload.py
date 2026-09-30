import os
import csv


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

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "abnormal_payload.csv"
)


# ============================================================
# CREATE DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# SETTINGS
# ============================================================

TOTAL_FRAMES = 10

# Frame containing the abnormal payload
ABNORMAL_FRAME = 6


# ============================================================
# HEADER
# ============================================================

print("==============================================")
print("      ABNORMAL PAYLOAD DATA GENERATOR")
print("==============================================")
print()

print(
    "Total frames       :",
    TOTAL_FRAMES
)

print(
    "Abnormal frame     :",
    ABNORMAL_FRAME
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


    for counter in range(
        1,
        TOTAL_FRAMES + 1
    ):

        # ----------------------------------------------------
        # NORMAL BUTTON BYTE
        # ----------------------------------------------------

        button_byte = "00"

        button_state = "RELEASED"


        # ----------------------------------------------------
        # CREATE ABNORMAL PAYLOAD
        # ----------------------------------------------------

        if counter == ABNORMAL_FRAME:

            # 0xFF is not a valid button state
            button_byte = "FF"

            # Keep CSV label normal because the IDS
            # must detect the payload itself.
            button_state = "RELEASED"


        # ----------------------------------------------------
        # PACKET COUNTER
        # ----------------------------------------------------

        counter_bytes = counter.to_bytes(
            4,
            byteorder="big"
        )


        # ----------------------------------------------------
        # EVENT TIME
        # ----------------------------------------------------

        event_time = counter * 500

        time_bytes = event_time.to_bytes(
            3,
            byteorder="big"
        )


        # ----------------------------------------------------
        # CREATE 8-BYTE CAN PAYLOAD
        # ----------------------------------------------------

        data = [
            button_byte,

            f"{counter_bytes[0]:02X}",
            f"{counter_bytes[1]:02X}",
            f"{counter_bytes[2]:02X}",
            f"{counter_bytes[3]:02X}",

            f"{time_bytes[0]:02X}",
            f"{time_bytes[1]:02X}",
            f"{time_bytes[2]:02X}"
        ]


        can_data = " ".join(data)


        # ----------------------------------------------------
        # WRITE CSV
        # ----------------------------------------------------

        writer.writerow([
            counter,
            event_time,
            "0x101",
            8,
            can_data,
            button_state,
            counter
        ])


# ============================================================
# RESULT
# ============================================================

print("==============================================")
print("             GENERATION COMPLETE")
print("==============================================")

print()
print("Output file:")
print(OUTPUT_FILE)

print()
print(
    "Abnormal payload frame:",
    ABNORMAL_FRAME
)

print(
    "Abnormal byte value   :",
    "FF"
)

print("==============================================")