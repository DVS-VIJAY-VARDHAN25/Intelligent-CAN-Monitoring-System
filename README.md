Absolutely. Here is the final, properly formatted, GitHub-ready README.md in one single block. Copy the entire block into Notepad and save it as README.md.

# Intelligent CAN-Based Monitoring and Intrusion Detection System

An embedded CAN-based monitoring and intrusion detection system designed to acquire sensor data, transmit it over a Controller Area Network (CAN), analyze the traffic, detect abnormal behavior, and visualize the system status through a real-time dashboard.

---

## Overview

The project combines embedded systems, CAN communication, sensor monitoring, data analysis, and intrusion detection into a single monitoring system.

An ADS1115 ADC is used for sensor data acquisition. The acquired data is processed by an Arduino Uno and transmitted through an MCP2515 CAN controller and TJA1050 CAN transceiver.

The CAN traffic is captured through the Arduino serial interface and processed using Python.

The software system performs:

- CAN traffic logging
- CAN frame analysis
- Normal traffic baseline generation
- Sensor baseline generation
- CAN anomaly detection
- Sensor anomaly detection
- Packet sequence monitoring
- CAN ID monitoring
- DLC and payload validation
- Traffic-rate monitoring
- IDS alert generation
- Real-time visualization through Streamlit

---

## System Architecture

```text
                 ┌─────────────────┐
                 │     ADS1115     │
                 │   ADC / Sensor  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Arduino Uno   │
                 │ Sensor + CAN    │
                 │ Data Processing │
                 └────────┬────────┘
                          │ SPI
                          ▼
                 ┌─────────────────┐
                 │    MCP2515      │
                 │ CAN Controller  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     TJA1050     │
                 │ CAN Transceiver │
                 └────────┬────────┘
                          │
                       CAN Bus
                          │
                          ▼
                 ┌─────────────────┐
                 │   USB Serial    │
                 │    Interface    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     Python      │
                 │ Data Processing │
                 │      + IDS      │
                 └────────┬────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
      ┌─────────────────┐     ┌─────────────────┐
      │   IDS Alerts    │     │   Streamlit     │
      │   & Analysis    │     │   Dashboard     │
      └─────────────────┘     └─────────────────┘
Hardware Used
Arduino Uno
ADS1115 16-bit ADC
MCP2515 CAN Controller
TJA1050 CAN Transceiver
Push Button
CAN-compatible wiring
USB connection for serial communication
Software Used
Arduino IDE
Python
Pandas
NumPy
Matplotlib
Streamlit
JSON
CSV
Git
GitHub
CAN Data Protocol

The system uses an 8-byte CAN payload.

Byte(s)	Parameter	Description
Byte 0	Button State	00 = Released, 01 = Pressed
Bytes 1–2	ADC Value	16-bit ADS1115 ADC value
Bytes 3–4	Packet Counter	16-bit sequential frame counter
Bytes 5–7	Event Time	24-bit event time in milliseconds
CAN Configuration
CAN ID : 0x101
DLC    : 8
Example CAN Payload
00 0B 5A 00 29 00 A1 90

Decoded:

Button State : Released
ADC Value    : 2906
Packet Count : 41
Event Time   : 41360 ms
CAN Logging

The Arduino CAN data is captured through the serial interface and stored in a CSV dataset.

The logged dataset contains:

PC Timestamp
Event Time (ms)
CAN ID
DLC
CAN Data
Button State
ADC Value
Packet Counter

The final dataset contains:

Total Frames : 51
CAN ID       : 0x101
DLC          : 8
Packet Count : 1–51
Normal CAN Baseline

A normal CAN traffic baseline was generated from the recorded CAN dataset.

The baseline contains expected characteristics such as:

Allowed CAN IDs
Expected DLC
Expected data length
Valid button states
Packet counter behavior
Expected timing behavior

This baseline is used by the IDS to identify abnormal CAN traffic.

ADS1115 Sensor Baseline

A sensor baseline was generated using the recorded ADS1115 values.

Normal Sensor Range
Minimum : 2875
Maximum : 2920
Mean    : 2897.59
Median  : 2896

The baseline also includes statistical information such as:

Q1  : 2887.5
Q3  : 2908
IQR : 20.5

The sensor baseline is used by the IDS to detect abnormal sensor readings.

Intrusion Detection System

The unified CAN IDS analyzes every received frame and checks multiple characteristics.

CAN ID Validation

The IDS verifies whether the received CAN ID belongs to the expected set of CAN IDs.

DLC Validation

The system checks whether the CAN frame contains the expected number of data bytes.

Data Length Validation

The actual payload length is checked against the expected CAN data length.

Payload Validation

The payload structure is checked against the defined CAN protocol.

Packet Sequence Monitoring

The packet counter is monitored to identify:

Missing packets
Unexpected counter jumps
Duplicate or incorrect sequence values
Traffic Rate Monitoring

The system monitors frame timing and traffic rate to identify abnormal bursts of CAN traffic.

Sensor Anomaly Detection

The ADS1115 value is compared against the established normal sensor range.

Controlled Anomaly Tests

Several controlled abnormal CAN datasets were generated to test the IDS.

Abnormal CAN ID

An unexpected CAN identifier was introduced:

0x555

This was used to test detection of unexpected CAN identifiers.

Abnormal DLC

A frame with an incorrect data length was generated to test DLC validation.

Abnormal Traffic Rate

A high-rate CAN traffic dataset was generated to test traffic-rate monitoring.

Abnormal Packet Sequence

A missing packet counter was introduced:

1, 2, 3, 5, 6, 7, 8

This was used to test packet sequence anomaly detection.

Abnormal Payload

An invalid payload value was introduced to test payload validation.

IDS Alert Logger

The alert logger processes the CAN dataset and generates a structured alert file.

The generated alert dataset contains:

Alert Timestamp
Session
Severity
Frame Number
CAN ID
DLC
Data Length
CAN Data
Anomaly Type
Expected Value
Actual Value
Description
Packet Counter
Event Time (ms)
ADC Value
Alert Status
Dataset Results

The final 51-frame dataset was analyzed by the unified IDS.

Total Frames Analyzed : 51
Total Anomalous Frames: 2

CAN ID Anomalies      : 0
DLC Anomalies         : 0
Data Length Anomalies : 0
Payload Anomalies     : 0
Sequence Anomalies    : 0
Rate Anomalies        : 0
Sensor Anomalies      : 2

The two detected sensor anomalies were:

Frame 40 → ADC = 2843
Frame 41 → ADC = 8126

Expected normal sensor range:

2875 – 2920

The IDS classified both events as sensor anomalies.

Streamlit Dashboard

A Streamlit dashboard was developed to visualize the CAN monitoring and IDS results.

The dashboard provides:

CAN system status
Frame reception progress
Total IDS alerts
Alert severity
Button state statistics
CAN ID information
DLC information
Packet counter monitoring
ADS1115 sensor monitoring
Sensor normal range
Minimum and maximum ADC values
Sensor anomaly visualization
CAN traffic visualization
Event interval analysis
CAN ID distribution

The final dashboard processes the recorded 51-frame dataset and displays the detected sensor anomalies.

Key Features
Embedded CAN communication
ADS1115 sensor acquisition
MCP2515 CAN controller
TJA1050 CAN transceiver
CAN frame logging
Structured CAN data protocol
Normal traffic baseline
Sensor baseline generation
CAN anomaly detection
Sensor anomaly detection
Packet sequence monitoring
CAN ID validation
DLC validation
Payload validation
Traffic-rate monitoring
IDS alert generation
CSV-based datasets
JSON-based baselines
Python-based analysis
Streamlit monitoring dashboard
Project Outcome

The project demonstrates an end-to-end embedded CAN monitoring and intrusion detection workflow.

Sensor data is acquired at the embedded node, transmitted using CAN, captured through a serial interface, processed using Python, analyzed against established baselines, and presented through a monitoring dashboard.

The system successfully demonstrated detection of abnormal sensor behavior within the recorded CAN dataset while also providing controlled test cases for CAN communication anomalies.

Technologies
Embedded Systems
CAN Bus
Arduino
ADS1115
MCP2515
TJA1050
Python
Pandas
NumPy
Matplotlib
Streamlit
Data Analysis
Intrusion Detection
Sensor Monitoring
Git
GitHub
Author

D.V. Sai Vijay Vardhan

B.Tech – Electronics & Communication Engineering
Mahindra University, Hyderabad


### After saving it

Make sure the file is exactly:

```text
README.md

and located at:

C:\Users\SAI VIJAY VARDHAN\OneDrive\Desktop\Intelligent_CAN_Monitoring_System

Then run:

dir README.md

If it appears correctly, run:

git add README.md
git status

At that point, we'll verify the complete staged project one last time and make your first commit.

# Intelligent CAN-Based Monitoring and Intrusion Detection System

An embedded CAN-based monitoring and intrusion detection system designed to acquire sensor data, transmit it over a Controller Area Network (CAN), analyze the traffic, detect abnormal behavior, and visualize the system status through a real-time dashboard.

---

## Overview

The project combines embedded systems, CAN communication, sensor monitoring, data analysis, and intrusion detection into a single monitoring system.

An ADS1115 ADC is used for sensor data acquisition. The acquired data is processed by an Arduino Uno and transmitted through an MCP2515 CAN controller and TJA1050 CAN transceiver.

The CAN traffic is captured through the Arduino serial interface and processed using Python.

The software system performs:

- CAN traffic logging
- CAN frame analysis
- Normal traffic baseline generation
- Sensor baseline generation
- CAN anomaly detection
- Sensor anomaly detection
- Packet sequence monitoring
- CAN ID monitoring
- DLC and payload validation
- Traffic-rate monitoring
- IDS alert generation
- Real-time visualization through Streamlit

---

## System Architecture


text
                 ┌─────────────────┐
                 │     ADS1115     │
                 │   ADC / Sensor  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Arduino Uno   │
                 │ Sensor + CAN    │
                 │ Data Processing │
                 └────────┬────────┘
                          │ SPI
                          ▼
                 ┌─────────────────┐
                 │    MCP2515      │
                 │ CAN Controller  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     TJA1050     │
                 │ CAN Transceiver │
                 └────────┬────────┘
                          │
                       CAN Bus
                          │
                          ▼
                 ┌─────────────────┐
                 │   USB Serial    │
                 │    Interface    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     Python      │
                 │ Data Processing │
                 │      + IDS      │
                 └────────┬────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
      ┌─────────────────┐     ┌─────────────────┐
      │   IDS Alerts    │     │   Streamlit     │
      │   & Analysis    │     │   Dashboard     │
      └─────────────────┘     └─────────────────┘



you are just giveing this part not all so give me all in a single block

Yes — you're right. The previous response was getting cut off because the code block was being rendered separately. Here is the ENTIRE README from beginning to end in ONE single code block.

Copy everything inside this block into Notepad and save it as README.md.

# Intelligent CAN-Based Monitoring and Intrusion Detection System

An embedded CAN-based monitoring and intrusion detection system designed to acquire sensor data, transmit it over a Controller Area Network (CAN), analyze the traffic, detect abnormal behavior, and visualize the system status through a real-time dashboard.

---

## Overview

The project combines embedded systems, CAN communication, sensor monitoring, data analysis, and intrusion detection into a single monitoring system.

An ADS1115 ADC is used for sensor data acquisition. The acquired data is processed by an Arduino Uno and transmitted through an MCP2515 CAN controller and TJA1050 CAN transceiver.

The CAN traffic is captured through the Arduino serial interface and processed using Python.

The software system performs:

- CAN traffic logging
- CAN frame analysis
- Normal traffic baseline generation
- Sensor baseline generation
- CAN anomaly detection
- Sensor anomaly detection
- Packet sequence monitoring
- CAN ID monitoring
- DLC and payload validation
- Traffic-rate monitoring
- IDS alert generation
- Real-time visualization through Streamlit

---

## System Architecture

```text
                 ┌─────────────────┐
                 │     ADS1115     │
                 │   ADC / Sensor  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Arduino Uno   │
                 │ Sensor + CAN    │
                 │ Data Processing │
                 └────────┬────────┘
                          │ SPI
                          ▼
                 ┌─────────────────┐
                 │    MCP2515      │
                 │ CAN Controller  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     TJA1050     │
                 │ CAN Transceiver │
                 └────────┬────────┘
                          │
                       CAN Bus
                          │
                          ▼
                 ┌─────────────────┐
                 │   USB Serial    │
                 │    Interface    │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     Python      │
                 │ Data Processing │
                 │      + IDS      │
                 └────────┬────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
      ┌─────────────────┐     ┌─────────────────┐
      │   IDS Alerts    │     │   Streamlit     │
      │   & Analysis    │     │   Dashboard     │
      └─────────────────┘     └─────────────────┘
Hardware Used
Arduino Uno
ADS1115 16-bit ADC
MCP2515 CAN Controller
TJA1050 CAN Transceiver
Push Button
CAN-compatible wiring
USB connection for serial communication
Software Used
Arduino IDE
Python
Pandas
NumPy
Matplotlib
Streamlit
JSON
CSV
Git
GitHub
CAN Data Protocol

The system uses an 8-byte CAN payload.

Byte(s)	Parameter	Description
Byte 0	Button State	00 = Released, 01 = Pressed
Bytes 1–2	ADC Value	16-bit ADS1115 ADC value
Bytes 3–4	Packet Counter	16-bit sequential frame counter
Bytes 5–7	Event Time	24-bit event time in milliseconds
CAN Configuration
CAN ID : 0x101
DLC    : 8
Example CAN Payload
00 0B 5A 00 29 00 A1 90

Decoded:

Button State : Released
ADC Value    : 2906
Packet Count : 41
Event Time   : 41360 ms
CAN Logging

The Arduino CAN data is captured through the serial interface and stored in a CSV dataset.

The logged dataset contains:

PC Timestamp
Event Time (ms)
CAN ID
DLC
CAN Data
Button State
ADC Value
Packet Counter

The final dataset contains:

Total Frames : 51
CAN ID       : 0x101
DLC          : 8
Packet Count : 1–51
Normal CAN Baseline

A normal CAN traffic baseline was generated from the recorded CAN dataset.

The baseline contains expected characteristics such as:

Allowed CAN IDs
Expected DLC
Expected data length
Valid button states
Packet counter behavior
Expected timing behavior

This baseline is used by the IDS to identify abnormal CAN traffic.

ADS1115 Sensor Baseline

A sensor baseline was generated using the recorded ADS1115 values.

Normal Sensor Range
Minimum : 2875
Maximum : 2920
Mean    : 2897.59
Median  : 2896

The baseline also includes statistical information such as:

Q1  : 2887.5
Q3  : 2908
IQR : 20.5

The sensor baseline is used by the IDS to detect abnormal sensor readings.

Intrusion Detection System

The unified CAN IDS analyzes every received frame and checks multiple characteristics.

CAN ID Validation

The IDS verifies whether the received CAN ID belongs to the expected set of CAN IDs.

DLC Validation

The system checks whether the CAN frame contains the expected number of data bytes.

Data Length Validation

The actual payload length is checked against the expected CAN data length.

Payload Validation

The payload structure is checked against the defined CAN protocol.

Packet Sequence Monitoring

The packet counter is monitored to identify:

Missing packets
Unexpected counter jumps
Duplicate or incorrect sequence values
Traffic Rate Monitoring

The system monitors frame timing and traffic rate to identify abnormal bursts of CAN traffic.

Sensor Anomaly Detection

The ADS1115 value is compared against the established normal sensor range.

Controlled Anomaly Tests

Several controlled abnormal CAN datasets were generated to test the IDS.

Abnormal CAN ID

An unexpected CAN identifier was introduced:

0x555

This was used to test detection of unexpected CAN identifiers.

Abnormal DLC

A frame with an incorrect data length was generated to test DLC validation.

Abnormal Traffic Rate

A high-rate CAN traffic dataset was generated to test traffic-rate monitoring.

Abnormal Packet Sequence

A missing packet counter was introduced:

1, 2, 3, 5, 6, 7, 8

This was used to test packet sequence anomaly detection.

Abnormal Payload

An invalid payload value was introduced to test payload validation.

IDS Alert Logger

The alert logger processes the CAN dataset and generates a structured alert file.

The generated alert dataset contains:

Alert Timestamp
Session
Severity
Frame Number
CAN ID
DLC
Data Length
CAN Data
Anomaly Type
Expected Value
Actual Value
Description
Packet Counter
Event Time (ms)
ADC Value
Alert Status
Dataset Results

The final 51-frame dataset was analyzed by the unified IDS.

Total Frames Analyzed : 51
Total Anomalous Frames: 2

CAN ID Anomalies      : 0
DLC Anomalies         : 0
Data Length Anomalies : 0
Payload Anomalies     : 0
Sequence Anomalies    : 0
Rate Anomalies        : 0
Sensor Anomalies      : 2

The two detected sensor anomalies were:

Frame 40 → ADC = 2843
Frame 41 → ADC = 8126

Expected normal sensor range:

2875 – 2920

The IDS classified both events as sensor anomalies.

Streamlit Dashboard

A Streamlit dashboard was developed to visualize the CAN monitoring and IDS results.

The dashboard provides:

CAN system status
Frame reception progress
Total IDS alerts
Alert severity
Button state statistics
CAN ID information
DLC information
Packet counter monitoring
ADS1115 sensor monitoring
Sensor normal range
Minimum and maximum ADC values
Sensor anomaly visualization
CAN traffic visualization
Event interval analysis
CAN ID distribution

The final dashboard processes the recorded 51-frame dataset and displays the detected sensor anomalies.

Key Features
Embedded CAN communication
ADS1115 sensor acquisition
MCP2515 CAN controller
TJA1050 CAN transceiver
CAN frame logging
Structured CAN data protocol
Normal traffic baseline
Sensor baseline generation
CAN anomaly detection
Sensor anomaly detection
Packet sequence monitoring
CAN ID validation
DLC validation
Payload validation
Traffic-rate monitoring
IDS alert generation
CSV-based datasets
JSON-based baselines
Python-based analysis
Streamlit monitoring dashboard
Project Outcome

The project demonstrates an end-to-end embedded CAN monitoring and intrusion detection workflow.

Sensor data is acquired at the embedded node, transmitted using CAN, captured through a serial interface, processed using Python, analyzed against established baselines, and presented through a monitoring dashboard.

The system successfully demonstrated detection of abnormal sensor behavior within the recorded CAN dataset while also providing controlled test cases for CAN communication anomalies.

Technologies
Embedded Systems
CAN Bus
Arduino
ADS1115
MCP2515
TJA1050
Python
Pandas
NumPy
Matplotlib
Streamlit
Data Analysis
Intrusion Detection
Sensor Monitoring
Git
GitHub
Author

D.V. Sai Vijay Vardhan

B.Tech – Electronics & Communication Engineering
Mahindra University, Hyderabad


### Now save it

In Notepad:

**File → Save As**

Filename:

```text
README.md

Save as type:

All Files (*.*)

Encoding:

UTF-8

Location:

C:\Users\SAI VIJAY VARDHAN\OneDrive\Desktop\Intelligent_CAN_Monitoring_System

Then run:

dir README.md

If it shows the file, run:

git add README.md
git status

Then send me the git status output.

again you are giveing me the same now u generate a word file for readme instead a single block so that it will easy to put in notepad

Done. I created the complete README content as a Word file so you can open it easily and copy the entire content into Notepad.

Download the README Word file

Open it → Ctrl+A → Ctrl+C → paste into Notepad → save as:

README.md

Then save it inside:

C:\Users\SAI VIJAY VARDHAN\OneDrive\Desktop\Intelligent_CAN_Monitoring_System

After that, tell me “saved”, and we'll continue with Git. 

CAN_Project_README_Content.docx
Document

CAN_Project_README_Content
100%

# Intelligent CAN-Based Monitoring and Intrusion Detection System

An embedded CAN-based monitoring and intrusion detection system designed to acquire sensor data, transmit it over a Controller Area Network (CAN), analyze the traffic, detect abnormal behavior, and visualize the system status through a real-time dashboard.

---

## Overview

The project combines embedded systems, CAN communication, sensor monitoring, data analysis, and intrusion detection into a single monitoring system.

An ADS1115 ADC is used for sensor data acquisition. The acquired data is processed by an Arduino Uno and transmitted through an MCP2515 CAN controller and TJA1050 CAN transceiver.

The CAN traffic is captured through the Arduino serial interface and processed using Python.

The software system performs:

- CAN traffic logging

- CAN frame analysis

- Normal traffic baseline generation

- Sensor baseline generation

- CAN anomaly detection

- Sensor anomaly detection

- Packet sequence monitoring

- CAN ID monitoring

- DLC and payload validation

- Traffic-rate monitoring

- IDS alert generation

- Real-time visualization through Streamlit

---

## System Architecture

```text

                 ┌─────────────────┐

                 │     ADS1115     │

                 │   ADC / Sensor  │

                 └────────┬────────┘

                          │

                          ▼

                 ┌─────────────────┐

                 │   Arduino Uno   │

                 │ Sensor + CAN    │

                 │ Data Processing │

                 └────────┬────────┘

                          │ SPI

                          ▼

                 ┌─────────────────┐

                 │    MCP2515      │

                 │ CAN Controller  │

                 └────────┬────────┘

                          │

                          ▼

                 ┌─────────────────┐

                 │     TJA1050     │

                 │ CAN Transceiver │

                 └────────┬────────┘

                          │

                       CAN Bus

                          │

                          ▼

                 ┌─────────────────┐

                 │   USB Serial    │

                 │    Interface    │

                 └────────┬────────┘

                          │

                          ▼

                 ┌─────────────────┐

                 │     Python      │

                 │ Data Processing │

                 │      + IDS      │

                 └────────┬────────┘

                          │

              ┌───────────┴───────────┐

              ▼                       ▼

      ┌─────────────────┐     ┌─────────────────┐

      │   IDS Alerts    │     │   Streamlit     │

      │   & Analysis    │     │   Dashboard     │

      └─────────────────┘     └─────────────────┘

```

---

## Hardware Used

- Arduino Uno

- ADS1115 16-bit ADC

- MCP2515 CAN Controller

- TJA1050 CAN Transceiver

- Push Button

- CAN-compatible wiring

- USB connection for serial communication

---

## Software Used

- Arduino IDE

- Python

- Pandas

- NumPy

- Matplotlib

- Streamlit

- JSON

- CSV

- Git

- GitHub

---

## CAN Data Protocol

The system uses an 8-byte CAN payload.

| Byte(s) | Parameter | Description |

|---------|-----------|-------------|

| Byte 0 | Button State | `00` = Released, `01` = Pressed |

| Bytes 1–2 | ADC Value | 16-bit ADS1115 ADC value |

| Bytes 3–4 | Packet Counter | 16-bit sequential frame counter |

| Bytes 5–7 | Event Time | 24-bit event time in milliseconds |

### CAN Configuration

```text

CAN ID : 0x101

DLC    : 8

```

### Example CAN Payload

```text

00 0B 5A 00 29 00 A1 90

```

Decoded:

```text

Button State : Released

ADC Value    : 2906

Packet Count : 41

Event Time   : 41360 ms

```

---

## CAN Logging

The Arduino CAN data is captured through the serial interface and stored in a CSV dataset.

The logged dataset contains:

- PC Timestamp

- Event Time (ms)

- CAN ID

- DLC

- CAN Data

- Button State

- ADC Value

- Packet Counter

The final dataset contains:

```text

Total Frames : 51

CAN ID       : 0x101

DLC          : 8

Packet Count : 1–51

```

---

## Normal CAN Baseline

A normal CAN traffic baseline was generated from the recorded CAN dataset.

The baseline contains expected characteristics such as:

- Allowed CAN IDs

- Expected DLC

- Expected data length

- Valid button states

- Packet counter behavior

- Expected timing behavior

This baseline is used by the IDS to identify abnormal CAN traffic.

---

## ADS1115 Sensor Baseline

A sensor baseline was generated using the recorded ADS1115 values.

### Normal Sensor Range

```text

Minimum : 2875

Maximum : 2920

Mean    : 2897.59

Median  : 2896

```

The baseline also includes statistical information such as:

```text

Q1  : 2887.5

Q3  : 2908

IQR : 20.5

```

The sensor baseline is used by the IDS to detect abnormal sensor readings.

---

## Intrusion Detection System

The unified CAN IDS analyzes every received frame and checks multiple characteristics.

### CAN ID Validation

The IDS verifies whether the received CAN ID belongs to the expected set of CAN IDs.

### DLC Validation

The system checks whether the CAN frame contains the expected number of data bytes.

### Data Length Validation

The actual payload length is checked against the expected CAN data length.

### Payload Validation

The payload structure is checked against the defined CAN protocol.

### Packet Sequence Monitoring

The packet counter is monitored to identify:

- Missing packets

- Unexpected counter jumps

- Duplicate or incorrect sequence values

### Traffic Rate Monitoring

The system monitors frame timing and traffic rate to identify abnormal bursts of CAN traffic.

### Sensor Anomaly Detection

The ADS1115 value is compared against the established normal sensor range.

---

## Controlled Anomaly Tests

Several controlled abnormal CAN datasets were generated to test the IDS.

### Abnormal CAN ID

An unexpected CAN identifier was introduced:

```text

0x555

```

This was used to test detection of unexpected CAN identifiers.

### Abnormal DLC

A frame with an incorrect data length was generated to test DLC validation.

### Abnormal Traffic Rate

A high-rate CAN traffic dataset was generated to test traffic-rate monitoring.

### Abnormal Packet Sequence

A missing packet counter was introduced:

```text

1, 2, 3, 5, 6, 7, 8

```

This was used to test packet sequence anomaly detection.

### Abnormal Payload

An invalid payload value was introduced to test payload validation.

---

## IDS Alert Logger

The alert logger processes the CAN dataset and generates a structured alert file.

The generated alert dataset contains:

- Alert Timestamp

- Session

- Severity

- Frame Number

- CAN ID

- DLC

- Data Length

- CAN Data

- Anomaly Type

- Expected Value

- Actual Value

- Description

- Packet Counter

- Event Time (ms)

- ADC Value

- Alert Status

---

## Dataset Results

The final 51-frame dataset was analyzed by the unified IDS.

```text

Total Frames Analyzed : 51

Total Anomalous Frames: 2

CAN ID Anomalies      : 0

DLC Anomalies         : 0

Data Length Anomalies : 0

Payload Anomalies     : 0

Sequence Anomalies    : 0

Rate Anomalies        : 0

Sensor Anomalies      : 2

```

The two detected sensor anomalies were:

```text

Frame 40 → ADC = 2843

Frame 41 → ADC = 8126

```

Expected normal sensor range:

```text

2875 – 2920

```

The IDS classified both events as sensor anomalies.

---

## Streamlit Dashboard

A Streamlit dashboard was developed to visualize the CAN monitoring and IDS results.

The dashboard provides:

- CAN system status

- Frame reception progress

- Total IDS alerts

- Alert severity

- Button state statistics

- CAN ID information

- DLC information

- Packet counter monitoring

- ADS1115 sensor monitoring

- Sensor normal range

- Minimum and maximum ADC values

- Sensor anomaly visualization

- CAN traffic visualization

- Event interval analysis

- CAN ID distribution

The final dashboard processes the recorded 51-frame dataset and displays the detected sensor anomalies.

---

## Key Features

- Embedded CAN communication

- ADS1115 sensor acquisition

- MCP2515 CAN controller

- TJA1050 CAN transceiver

- CAN frame logging

- Structured CAN data protocol

- Normal traffic baseline

- Sensor baseline generation

- CAN anomaly detection

- Sensor anomaly detection

- Packet sequence monitoring

- CAN ID validation

- DLC validation

- Payload validation

- Traffic-rate monitoring

- IDS alert generation

- CSV-based datasets

- JSON-based baselines

- Python-based analysis

- Streamlit monitoring dashboard

---

## Project Outcome

The project demonstrates an end-to-end embedded CAN monitoring and intrusion detection workflow.

Sensor data is acquired at the embedded node, transmitted using CAN, captured through a serial interface, processed using Python, analyzed against established baselines, and presented through a monitoring dashboard.

The system successfully demonstrated detection of abnormal sensor behavior within the recorded CAN dataset while also providing controlled test cases for CAN communication anomalies.

---

## Technologies

```text

Embedded Systems

CAN Bus

Arduino

ADS1115

MCP2515

TJA1050

Python

Pandas

NumPy

Matplotlib

Streamlit

Data Analysis

Intrusion Detection

Sensor Monitoring

Git

GitHub

```

---

## Author

**D.V. Sai Vijay Vardhan**

B.Tech – Electronics & Communication Engineering

Mahindra University, Hyderabad