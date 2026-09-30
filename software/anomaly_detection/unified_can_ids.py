import pandas as pd
import json
import os
import sys
from datetime import datetime


# ============================================================
# FILE PATHS
# ============================================================

BASELINE_FILE = "data/processed/normal_baseline.json"
SENSOR_BASELINE_FILE = "data/processed/sensor_baseline.json"

DEFAULT_INPUT_FILE = "can_log.csv"

OUTPUT_FILE = "data/processed/ids_alerts.csv"


# ============================================================
# HEADER
# ============================================================

print("==============================================")
print("          CAN IDS ALERT LOGGER")
print("                    V2.0")
print("==============================================")


# ============================================================
# LOAD CAN BASELINE
# ============================================================

print("\nLoading normal CAN baseline...")

with open(BASELINE_FILE, "r") as file:
    baseline = json.load(file)

print("Normal CAN baseline loaded successfully.")


# ============================================================
# LOAD SENSOR BASELINE
# ============================================================

print("\nLoading sensor baseline...")

with open(SENSOR_BASELINE_FILE, "r") as file:
    sensor_baseline = json.load(file)

print("Sensor baseline loaded successfully.")


# ============================================================
# SENSOR LIMITS
# ============================================================

sensor_info = sensor_baseline["adc_sensor"]

NORMAL_ADC_MIN = float(
    sensor_info["normal_min"]
)

NORMAL_ADC_MAX = float(
    sensor_info["normal_max"]
)


# ============================================================
# CAN BASELINE
# ============================================================

allowed_can_ids = {
    str(value).strip().upper()
    for value in baseline["can_ids"]
}

allowed_dlc = set(
    baseline["allowed_dlc"]
)

allowed_data_lengths = set(
    baseline["allowed_data_lengths"]
)

expected_counter_increment = int(
    baseline["packet_counter"]["expected_increment"]
)

minimum_interval = float(
    baseline["timing"]["minimum_interval_ms"]
)


# ============================================================
# INPUT DATASET
# ============================================================

if len(sys.argv) > 1:
    INPUT_FILE = sys.argv[1]
else:
    INPUT_FILE = DEFAULT_INPUT_FILE


print("\nLoading CAN dataset...")
print(f"Dataset: {INPUT_FILE}")

df = pd.read_csv(INPUT_FILE)

print("CAN dataset loaded successfully.")
print(f"Total frames: {len(df)}")


# ============================================================
# SESSION VARIABLES
# ============================================================

session = 1

previous_counter = None
previous_event_time = None


# ============================================================
# ALERT STORAGE
# ============================================================

alerts = []


# ============================================================
# PROCESS EACH FRAME
# ============================================================

for index, row in df.iterrows():

    frame_number = index + 1

    # --------------------------------------------------------
    # Basic frame information
    # --------------------------------------------------------

    can_id = str(
        row["CAN ID"]
    ).strip().upper()

    dlc = int(row["DLC"])

    can_data = str(
        row["CAN Data"]
    ).strip()

    data_bytes = can_data.split()

    data_length = len(data_bytes)


    # --------------------------------------------------------
    # Decode V3 payload
    #
    # Byte 0     = Button
    # Bytes 1-2  = ADC
    # Bytes 3-4  = Packet Counter
    # Bytes 5-7  = Event Time
    # --------------------------------------------------------

    button_byte = None
    adc_value = None
    packet_counter = None
    event_time = None


    # ========================================================
    # BUTTON
    # ========================================================

    if data_length >= 1:

        try:
            button_byte = int(
                data_bytes[0],
                16
            )
        except ValueError:
            button_byte = None


    # ========================================================
    # ADC
    # ========================================================

    if data_length >= 3:

        try:

            adc_high = int(
                data_bytes[1],
                16
            )

            adc_low = int(
                data_bytes[2],
                16
            )

            adc_value = (
                (adc_high << 8)
                | adc_low
            )

        except ValueError:

            adc_value = None


    # ========================================================
    # PACKET COUNTER
    # ========================================================

    if data_length >= 5:

        try:

            counter_high = int(
                data_bytes[3],
                16
            )

            counter_low = int(
                data_bytes[4],
                16
            )

            packet_counter = (
                (counter_high << 8)
                | counter_low
            )

        except ValueError:

            packet_counter = None


    # ========================================================
    # EVENT TIME
    # ========================================================

    if data_length >= 8:

        try:

            time_high = int(
                data_bytes[5],
                16
            )

            time_middle = int(
                data_bytes[6],
                16
            )

            time_low = int(
                data_bytes[7],
                16
            )

            event_time = (
                (time_high << 16)
                | (time_middle << 8)
                | time_low
            )

        except ValueError:

            event_time = None


    # ========================================================
    # SESSION DETECTION
    # ========================================================

    if (
        previous_event_time is not None
        and event_time is not None
        and event_time < previous_event_time
    ):

        session += 1

        previous_counter = None
        previous_event_time = None


    # ========================================================
    # HELPER FUNCTION FOR ALERTS
    # ========================================================

    def add_alert(
        severity,
        anomaly_type,
        expected_value,
        actual_value,
        description
    ):

        alerts.append({
            "Alert Timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "Session":
                session,

            "Severity":
                severity,

            "Frame Number":
                frame_number,

            "CAN ID":
                can_id,

            "DLC":
                dlc,

            "Data Length":
                data_length,

            "CAN Data":
                can_data,

            "Anomaly Type":
                anomaly_type,

            "Expected Value":
                expected_value,

            "Actual Value":
                actual_value,

            "Description":
                description,

            "Packet Counter":
                packet_counter,

            "Event Time (ms)":
                event_time,

            "ADC Value":
                adc_value,

            "Alert Status":
                "OPEN"
        })


    # ========================================================
    # 1. CAN ID CHECK
    # ========================================================

    if can_id not in allowed_can_ids:

        add_alert(
            "HIGH",
            "UNEXPECTED CAN ID",
            ", ".join(sorted(allowed_can_ids)),
            can_id,
            "CAN identifier is not part of the normal CAN traffic baseline."
        )


    # ========================================================
    # 2. DLC CHECK
    # ========================================================

    if dlc not in allowed_dlc:

        add_alert(
            "MEDIUM",
            "UNEXPECTED DLC",
            str(sorted(allowed_dlc)),
            str(dlc),
            "CAN frame DLC differs from the normal baseline."
        )


    # ========================================================
    # 3. DATA LENGTH CHECK
    # ========================================================

    if data_length not in allowed_data_lengths:

        add_alert(
            "MEDIUM",
            "UNEXPECTED DATA LENGTH",
            str(sorted(allowed_data_lengths)),
            str(data_length),
            "CAN payload length differs from the normal baseline."
        )


    # ========================================================
    # 4. BUTTON PAYLOAD CHECK
    # ========================================================

    if button_byte is not None:

        if button_byte not in [0, 1]:

            add_alert(
                "MEDIUM",
                "INVALID PAYLOAD",
                "00 or 01",
                data_bytes[0],
                "Button payload contains an invalid value."
            )


    # ========================================================
    # 5. PACKET SEQUENCE CHECK
    # ========================================================

    if (
        packet_counter is not None
        and previous_counter is not None
    ):

        expected_counter = (
            previous_counter
            + expected_counter_increment
        )

        if packet_counter != expected_counter:

            add_alert(
                "HIGH",
                "PACKET SEQUENCE ERROR",
                str(expected_counter),
                str(packet_counter),
                "Packet counter does not follow the expected sequence."
            )


    # ========================================================
    # 6. TRAFFIC RATE CHECK
    # ========================================================

    if (
        event_time is not None
        and previous_event_time is not None
    ):

        interval = (
            event_time
            - previous_event_time
        )

        if (
            interval > 0
            and interval < minimum_interval
        ):

            add_alert(
                "HIGH",
                "HIGH TRAFFIC RATE",
                f">= {minimum_interval:.2f} ms",
                f"{interval} ms",
                "CAN messages are arriving faster than the normal baseline."
            )


    # ========================================================
    # 7. ADS1115 SENSOR CHECK
    # ========================================================

    if adc_value is not None:

        if (
            adc_value < NORMAL_ADC_MIN
            or adc_value > NORMAL_ADC_MAX
        ):

            add_alert(
                "MEDIUM",
                "ABNORMAL ADS1115 VALUE",
                f"{NORMAL_ADC_MIN:.0f}-{NORMAL_ADC_MAX:.0f}",
                str(adc_value),
                "ADS1115 sensor value is outside the learned normal operating range."
            )


    # ========================================================
    # UPDATE PREVIOUS VALUES
    # ========================================================

    if packet_counter is not None:

        previous_counter = packet_counter

    if event_time is not None:

        previous_event_time = event_time


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    "data/processed",
    exist_ok=True
)


# ============================================================
# SAVE ALERTS
# ============================================================

columns = [
    "Alert Timestamp",
    "Session",
    "Severity",
    "Frame Number",
    "CAN ID",
    "DLC",
    "Data Length",
    "CAN Data",
    "Anomaly Type",
    "Expected Value",
    "Actual Value",
    "Description",
    "Packet Counter",
    "Event Time (ms)",
    "ADC Value",
    "Alert Status"
]


alerts_df = pd.DataFrame(
    alerts,
    columns=columns
)

alerts_df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

high_alerts = sum(
    1 for alert in alerts
    if alert["Severity"] == "HIGH"
)

medium_alerts = sum(
    1 for alert in alerts
    if alert["Severity"] == "MEDIUM"
)

low_alerts = sum(
    1 for alert in alerts
    if alert["Severity"] == "LOW"
)


print("\n==============================================")
print("             ALERT LOG SUMMARY")
print("==============================================")

print(
    f"Total frames analyzed : "
    f"{len(df)}"
)

print(
    f"Total alerts generated: "
    f"{len(alerts)}"
)

print(
    f"CAN sessions detected : "
    f"{session}"
)

print("----------------------------------------------")

print(
    f"HIGH alerts           : "
    f"{high_alerts}"
)

print(
    f"MEDIUM alerts         : "
    f"{medium_alerts}"
)

print(
    f"LOW alerts            : "
    f"{low_alerts}"
)

print("----------------------------------------------")

print(
    "Alerts saved to:"
)

print(OUTPUT_FILE)


# ============================================================
# DISPLAY ALERTS
# ============================================================

if alerts:

    print("\nALERTS:")

    for alert in alerts:

        print(
            f"[{alert['Severity']}] "
            f"Frame {alert['Frame Number']} "
            f"→ {alert['Anomaly Type']}"
        )

        print(
            f"    Expected: "
            f"{alert['Expected Value']}"
        )

        print(
            f"    Actual  : "
            f"{alert['Actual Value']}"
        )

else:

    print(
        "\nNo IDS alerts detected."
    )


# ============================================================
# FINAL RESULT
# ============================================================

print("\n==============================================")

if alerts:

    print(
        "RESULT: ALERTS GENERATED"
    )

else:

    print(
        "RESULT: NO ALERTS GENERATED"
    )

print("==============================================")