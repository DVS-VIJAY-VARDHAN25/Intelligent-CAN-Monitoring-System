import csv
import json
import os
from datetime import datetime


# ============================================================
# CAN IDS ALERT LOGGER V2.0
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

NORMAL_BASELINE_FILE = os.path.join(
    BASE_DIR, "data", "processed", "normal_baseline.json"
)

SENSOR_BASELINE_FILE = os.path.join(
    BASE_DIR, "data", "processed", "sensor_baseline.json"
)

CAN_DATASET_FILE = os.path.join(
    BASE_DIR, "can_log.csv"
)

ALERT_OUTPUT_FILE = os.path.join(
    BASE_DIR, "data", "processed", "ids_alerts.csv"
)


# ============================================================
# LOAD NORMAL CAN BASELINE
# ============================================================

print("==============================================")
print("          CAN IDS ALERT LOGGER")
print("                    V2.0")
print("==============================================")
print()

print("Loading normal CAN baseline...")

with open(NORMAL_BASELINE_FILE, "r") as file:
    normal_baseline = json.load(file)

print("Baseline loaded successfully.")
print()


# ============================================================
# LOAD SENSOR BASELINE
# ============================================================

print("Loading sensor baseline...")

with open(SENSOR_BASELINE_FILE, "r") as file:
    sensor_baseline = json.load(file)

print("Sensor baseline loaded successfully.")
print()


# ============================================================
# NORMAL CAN PARAMETERS
# ============================================================

allowed_can_ids = {
    str(value).strip().upper()
    for value in normal_baseline["can_ids"]
}

allowed_dlc = set(
    normal_baseline["allowed_dlc"]
)

allowed_data_lengths = set(
    normal_baseline["allowed_data_lengths"]
)

allowed_button_states = {0, 1}

expected_packet_increment = normal_baseline.get(
    "expected_packet_increment",
    1
)


# ============================================================
# SENSOR PARAMETERS
# ============================================================

adc_sensor = sensor_baseline["adc_sensor"]

normal_adc_min = adc_sensor["normal_min"]
normal_adc_max = adc_sensor["normal_max"]


# ============================================================
# LOAD CAN DATASET
# ============================================================

print("Loading CAN dataset...")

with open(CAN_DATASET_FILE, "r") as file:
    reader = csv.DictReader(file)
    rows = list(reader)

print("CAN dataset loaded successfully.")
print(f"Total frames: {len(rows)}")
print()


# ============================================================
# ALERT STORAGE
# ============================================================

alerts = []

total_frames = len(rows)

can_id_anomalies = 0
dlc_anomalies = 0
data_length_anomalies = 0
payload_anomalies = 0
sequence_anomalies = 0
rate_anomalies = 0
sensor_anomalies = 0

sessions = 1
current_session = 1

previous_event_time = None
previous_packet_counter = None


# ============================================================
# HELPER FUNCTION
# ============================================================

def add_alert(
    frame_number,
    session,
    severity,
    can_id,
    dlc,
    data_length,
    can_data,
    anomaly_type,
    expected_value,
    actual_value,
    description,
    packet_counter,
    event_time,
    adc_value
):

    alert = {
        "Alert Timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "Session": session,

        "Severity": severity,

        "Frame Number": frame_number,

        "CAN ID": can_id,

        "DLC": dlc,

        "Data Length": data_length,

        "CAN Data": can_data,

        "Anomaly Type": anomaly_type,

        "Expected Value": expected_value,

        "Actual Value": actual_value,

        "Description": description,

        "Packet Counter": packet_counter,

        "Event Time (ms)": event_time,

        "ADC Value": adc_value,

        "Alert Status": "ACTIVE"
    }

    alerts.append(alert)


# ============================================================
# PROCESS EVERY CAN FRAME
# ============================================================

for index, row in enumerate(rows, start=1):

    frame_number = index

    # --------------------------------------------------------
    # BASIC DATA
    # --------------------------------------------------------

    can_id = str(row["CAN ID"]).strip().upper()

    try:
        dlc = int(row["DLC"])
    except:
        dlc = -1

    can_data = str(row["CAN Data"]).strip()

    # Split CAN bytes
    data_bytes = can_data.split()

    data_length = len(data_bytes)

    # --------------------------------------------------------
    # DECODE V3 PAYLOAD
    #
    # Byte 0     = Button State
    # Bytes 1-2  = ADS1115 ADC Value
    # Bytes 3-4  = Packet Counter
    # Bytes 5-7  = Event Time
    # --------------------------------------------------------

    button_state = None
    adc_value = None
    packet_counter = None
    event_time = None

    try:

        if data_length >= 1:
            button_state = int(
                data_bytes[0],
                16
            )

        if data_length >= 3:
            adc_value = (
                (int(data_bytes[1], 16) << 8)
                |
                int(data_bytes[2], 16)
            )

        if data_length >= 5:
            packet_counter = (
                (int(data_bytes[3], 16) << 8)
                |
                int(data_bytes[4], 16)
            )

        if data_length >= 8:
            event_time = (
                (int(data_bytes[5], 16) << 16)
                |
                (int(data_bytes[6], 16) << 8)
                |
                int(data_bytes[7], 16)
            )

    except ValueError:

        add_alert(
            frame_number,
            current_session,
            "MEDIUM",
            can_id,
            dlc,
            data_length,
            can_data,
            "INVALID PAYLOAD",
            "Valid hexadecimal CAN payload",
            can_data,
            "CAN payload contains invalid hexadecimal data",
            packet_counter,
            event_time,
            adc_value
        )

        payload_anomalies += 1

        continue


    # ========================================================
    # SESSION DETECTION
    # ========================================================

    if (
        previous_event_time is not None
        and event_time is not None
        and event_time < previous_event_time
    ):

        current_session += 1
        sessions += 1

        # Reset sequence checking for new session
        previous_packet_counter = None


    # ========================================================
    # 1. CAN ID CHECK
    # ========================================================

    if can_id not in allowed_can_ids:

        can_id_anomalies += 1

        add_alert(
            frame_number,
            current_session,
            "HIGH",
            can_id,
            dlc,
            data_length,
            can_data,
            "UNEXPECTED CAN ID",
            ", ".join(sorted(allowed_can_ids)),
            can_id,
            "CAN ID is not present in the normal CAN baseline",
            packet_counter,
            event_time,
            adc_value
        )


    # ========================================================
    # 2. DLC CHECK
    # ========================================================

    if dlc not in allowed_dlc:

        dlc_anomalies += 1

        add_alert(
            frame_number,
            current_session,
            "MEDIUM",
            can_id,
            dlc,
            data_length,
            can_data,
            "UNEXPECTED DLC",
            ", ".join(
                str(value)
                for value in sorted(allowed_dlc)
            ),
            dlc,
            "CAN DLC does not match the normal baseline",
            packet_counter,
            event_time,
            adc_value
        )


    # ========================================================
    # 3. DATA LENGTH CHECK
    # ========================================================

    if data_length not in allowed_data_lengths:

        data_length_anomalies += 1

        add_alert(
            frame_number,
            current_session,
            "MEDIUM",
            can_id,
            dlc,
            data_length,
            can_data,
            "UNEXPECTED DATA LENGTH",
            ", ".join(
                str(value)
                for value in sorted(allowed_data_lengths)
            ),
            data_length,
            "Number of CAN payload bytes does not match baseline",
            packet_counter,
            event_time,
            adc_value
        )


    # ========================================================
    # 4. BUTTON PAYLOAD CHECK
    # ========================================================

    if (
        button_state is not None
        and button_state not in allowed_button_states
    ):

        payload_anomalies += 1

        add_alert(
            frame_number,
            current_session,
            "MEDIUM",
            can_id,
            dlc,
            data_length,
            can_data,
            "INVALID BUTTON STATE",
            "0 or 1",
            button_state,
            "Button payload contains an invalid state",
            packet_counter,
            event_time,
            adc_value
        )


    # ========================================================
    # 5. PACKET SEQUENCE CHECK
    # ========================================================

    if (
        previous_packet_counter is not None
        and packet_counter is not None
    ):

        expected_counter = (
            previous_packet_counter
            + expected_packet_increment
        )

        if packet_counter != expected_counter:

            sequence_anomalies += 1

            add_alert(
                frame_number,
                current_session,
                "HIGH",
                can_id,
                dlc,
                data_length,
                can_data,
                "PACKET SEQUENCE ERROR",
                expected_counter,
                packet_counter,
                "Packet counter does not follow the expected sequence",
                packet_counter,
                event_time,
                adc_value
            )


    # ========================================================
    # 6. TRAFFIC RATE CHECK
    # ========================================================

    if (
        previous_event_time is not None
        and event_time is not None
        and event_time >= previous_event_time
    ):

        interval = event_time - previous_event_time

        # Ignore zero/negative intervals
        if interval > 0:

            # Current project baseline expects roughly
            # one frame per ~1 second.
            #
            # This check is deliberately conservative so that
            # normal sensor variation does not trigger alerts.

            if interval < 100:

                rate_anomalies += 1

                add_alert(
                    frame_number,
                    current_session,
                    "HIGH",
                    can_id,
                    dlc,
                    data_length,
                    can_data,
                    "HIGH TRAFFIC RATE",
                    ">= 100 ms interval",
                    interval,
                    "CAN frames are arriving at an unusually high rate",
                    packet_counter,
                    event_time,
                    adc_value
                )


    # ========================================================
    # 7. ADS1115 SENSOR CHECK
    # ========================================================

    if adc_value is not None:

        if (
            adc_value < normal_adc_min
            or
            adc_value > normal_adc_max
        ):

            sensor_anomalies += 1

            add_alert(
                frame_number,
                current_session,
                "MEDIUM",
                can_id,
                dlc,
                data_length,
                can_data,
                "ABNORMAL ADS1115 VALUE",
                f"{normal_adc_min:.0f}-{normal_adc_max:.0f}",
                adc_value,
                (
                    "ADS1115 ADC value is outside the "
                    "established normal sensor range"
                ),
                packet_counter,
                event_time,
                adc_value
            )


    # ========================================================
    # UPDATE PREVIOUS VALUES
    # ========================================================

    if packet_counter is not None:
        previous_packet_counter = packet_counter

    if event_time is not None:
        previous_event_time = event_time


# ============================================================
# SAVE ALERT CSV
# ============================================================

os.makedirs(
    os.path.dirname(ALERT_OUTPUT_FILE),
    exist_ok=True
)

fieldnames = [
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


with open(
    ALERT_OUTPUT_FILE,
    "w",
    newline=""
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for alert in alerts:
        writer.writerow(alert)


# ============================================================
# ALERT COUNTS
# ============================================================

high_alerts = sum(
    1
    for alert in alerts
    if alert["Severity"] == "HIGH"
)

medium_alerts = sum(
    1
    for alert in alerts
    if alert["Severity"] == "MEDIUM"
)

low_alerts = sum(
    1
    for alert in alerts
    if alert["Severity"] == "LOW"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print()
print("==============================================")
print("          DETAILED ALERT LOG SUMMARY")
print("==============================================")

print(
    f"Total frames analyzed : {total_frames}"
)

print(
    f"Total alerts generated: {len(alerts)}"
)

print(
    f"CAN sessions detected : {sessions}"
)

print("----------------------------------------------")

print(
    f"HIGH alerts           : {high_alerts}"
)

print(
    f"MEDIUM alerts         : {medium_alerts}"
)

print(
    f"LOW alerts            : {low_alerts}"
)

print("----------------------------------------------")

print(
    "Detailed alerts saved to:"
)

print(
    ALERT_OUTPUT_FILE
)

print("----------------------------------------------")


if len(alerts) == 0:

    print("RESULT: NO ANOMALIES DETECTED")

else:

    print("RESULT: DETAILED ALERTS GENERATED")


# ============================================================
# PRINT DETAILED ALERTS
# ============================================================

print()

for alert in alerts:

    print(
        f"[{alert['Severity']}] "
        f"Frame {alert['Frame Number']} → "
        f"{alert['Anomaly Type']}"
    )

    print(
        f"    Expected : "
        f"{alert['Expected Value']}"
    )

    print(
        f"    Actual   : "
        f"{alert['Actual Value']}"
    )

    print()