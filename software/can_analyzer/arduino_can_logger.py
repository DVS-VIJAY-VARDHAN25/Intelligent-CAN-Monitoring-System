import serial
import csv
import re
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

SERIAL_PORT = "COM3"
BAUD_RATE = 115200

OUTPUT_FILE = "can_log.csv"

# ============================================================
# SERIAL CONNECTION
# ============================================================

print("==============================================")
print("       ARDUINO CAN SENSOR LOGGER V2")
print("==============================================")
print()
print(f"Opening serial port: {SERIAL_PORT}")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except serial.SerialException as e:
    print("ERROR: Could not open serial port.")
    print(e)
    print()
    print("Make sure Arduino Serial Monitor is CLOSED.")
    raise SystemExit

print("Serial connection established.")
print()
print("Waiting for CAN frames...")
print("Press Ctrl+C to stop logging.")
print()

# ============================================================
# CSV FILE
# ============================================================

csv_file = open(
    OUTPUT_FILE,
    mode="w",
    newline=""
)

writer = csv.writer(csv_file)

writer.writerow([
    "PC Timestamp",
    "Event Time (ms)",
    "CAN ID",
    "DLC",
    "CAN Data",
    "Button State",
    "ADC Value",
    "Packet Counter"
])

# ============================================================
# LOGGING
# ============================================================

frame_count = 0

try:

    while True:

        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line:
            continue

        # ----------------------------------------------------
        # Look for CAN DATA line
        #
        # Example:
        # DATA   : 00 0B 5A 00 01 00 03 E8
        # ----------------------------------------------------

        if line.startswith("DATA"):

            match = re.search(
                r"DATA\s*:\s*((?:[0-9A-Fa-f]{2}\s*)+)",
                line
            )

            if not match:
                continue

            data_string = match.group(1).strip()

            data_bytes = data_string.split()

            # We expect 8 bytes
            if len(data_bytes) != 8:
                print("WARNING: Unexpected CAN data length")
                continue

            # ------------------------------------------------
            # Convert bytes from HEX
            # ------------------------------------------------

            data = [
                int(byte, 16)
                for byte in data_bytes
            ]

            # ------------------------------------------------
            # Decode CAN payload
            # ------------------------------------------------

            # Byte 0
            button_state = data[0]

            if button_state == 1:
                button_text = "PRESSED"

            elif button_state == 0:
                button_text = "RELEASED"

            else:
                button_text = "INVALID"

            # Bytes 1-2
            adc_value = (
                (data[1] << 8)
                | data[2]
            )

            # Bytes 3-4
            packet_counter = (
                (data[3] << 8)
                | data[4]
            )

            # Bytes 5-7
            event_time = (
                (data[5] << 16)
                | (data[6] << 8)
                | data[7]
            )

            # ------------------------------------------------
            # Current PC timestamp
            # ------------------------------------------------

            pc_timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]

            # ------------------------------------------------
            # CAN information
            # ------------------------------------------------

            can_id = "0x101"
            dlc = 8

            # ------------------------------------------------
            # Write CSV
            # ------------------------------------------------

            writer.writerow([
                pc_timestamp,
                event_time,
                can_id,
                dlc,
                data_string.upper(),
                button_text,
                adc_value,
                packet_counter
            ])

            csv_file.flush()

            frame_count += 1

            # ------------------------------------------------
            # Display
            # ------------------------------------------------

            print("----------------------------------------------")
            print(f"Frame         : {frame_count}")
            print(f"PC Timestamp  : {pc_timestamp}")
            print(f"CAN ID        : {can_id}")
            print(f"DLC           : {dlc}")
            print(f"CAN Data      : {data_string.upper()}")
            print(f"Button        : {button_text}")
            print(f"ADC Value     : {adc_value}")
            print(f"Packet Counter: {packet_counter}")
            print(f"Event Time    : {event_time} ms")


except KeyboardInterrupt:

    print()
    print()
    print("==============================================")
    print("             LOGGING STOPPED")
    print("==============================================")
    print(f"Frames logged : {frame_count}")
    print(f"CSV file      : {OUTPUT_FILE}")


finally:

    csv_file.close()
    ser.close()

    print()
    print("Serial connection closed.")