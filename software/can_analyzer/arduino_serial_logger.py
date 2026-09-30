import serial
import csv
import re
import time
from datetime import datetime

PORT = "COM3"
BAUDRATE = 115200

CSV_FILE = "can_log.csv"

arduino = serial.Serial(
    port=PORT,
    baudrate=BAUDRATE,
    timeout=1
)

time.sleep(2)

print("Connected to Arduino.")
print("Starting CAN data logger...")
print("--------------------------------------")

with open(CSV_FILE, "a", newline="") as file:

    writer = csv.writer(file)

    # Write header only if file is empty
    if file.tell() == 0:
        writer.writerow([
            "PC Timestamp",
            "Event Time (ms)",
            "CAN ID",
            "DLC",
            "Data",
            "Button State",
            "Packet Counter"
        ])

    current_event = {}

    try:

        while True:

            line = arduino.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            print(line)

            # -----------------------------
            # BUTTON EVENT
            # -----------------------------

            if "BUTTON EVENT:" in line:

                if "PRESSED" in line:
                    current_event["button"] = "PRESSED"

                elif "RELEASED" in line:
                    current_event["button"] = "RELEASED"

            # -----------------------------
            # PACKET COUNTER
            # -----------------------------

            elif line.startswith("Packet Counter:"):

                current_event["packet"] = int(
                    line.split(":")[1].strip()
                )

            # -----------------------------
            # EVENT TIME
            # -----------------------------

            elif line.startswith("Event Time:"):

                current_event["event_time"] = int(
                    line.split(":")[1]
                    .replace("ms", "")
                    .strip()
                )

            # -----------------------------
            # CAN ID
            # -----------------------------

            elif line.startswith("CAN ID"):

                current_event["can_id"] = line.split(":")[1].strip()

            # -----------------------------
            # DLC
            # -----------------------------

            elif line.startswith("DLC"):

                current_event["dlc"] = int(
                    line.split(":")[1].strip()
                )

            # -----------------------------
            # CAN DATA
            # -----------------------------

            elif line.startswith("DATA"):

                current_event["data"] = line.split(":")[1].strip()

            # -----------------------------
            # WHEN COMPLETE CAN FRAME
            # -----------------------------

            elif line.startswith("----------------------------"):

                if "can_id" in current_event:

                    writer.writerow([
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S.%f"
                        ),
                        current_event.get("event_time", ""),
                        current_event.get("can_id", ""),
                        current_event.get("dlc", ""),
                        current_event.get("data", ""),
                        current_event.get("button", ""),
                        current_event.get("packet", "")
                    ])

                    file.flush()

                    print(">>> CAN EVENT SAVED TO CSV")

                    current_event = {}

    except KeyboardInterrupt:

        print()
        print("Stopping logger...")

    finally:

        arduino.close()

        print("Arduino serial connection closed.")
        print("CAN logging stopped.")