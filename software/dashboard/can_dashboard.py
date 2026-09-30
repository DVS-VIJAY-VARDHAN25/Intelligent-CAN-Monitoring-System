import streamlit as st
import pandas as pd
import time
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Intelligent CAN Monitoring & IDS",
    page_icon="🔐",
    layout="wide"
)


# ============================================================
# FILE PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CAN_LOG_FILE = PROJECT_ROOT / "can_log.csv"

ALERT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "ids_alerts.csv"
)

SENSOR_BASELINE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "sensor_baseline.json"
)


# ============================================================
# TITLE
# ============================================================

st.title("Intelligent CAN Monitoring & IDS")

st.caption(
    "CAN-Based Distributed Monitoring and Intrusion Detection System"
)

st.divider()


# ============================================================
# LOAD CAN DATA
# ============================================================

if CAN_LOG_FILE.exists():

    df = pd.read_csv(CAN_LOG_FILE)

else:

    df = pd.DataFrame()


# ============================================================
# LOAD ALERT DATA
# ============================================================

if ALERT_FILE.exists():

    alerts_df = pd.read_csv(ALERT_FILE)

else:

    alerts_df = pd.DataFrame()


# ============================================================
# LOAD SENSOR BASELINE
# ============================================================

sensor_min = None
sensor_max = None
sensor_mean = None
sensor_median = None

if SENSOR_BASELINE_FILE.exists():

    try:

        sensor_baseline = pd.read_json(
            SENSOR_BASELINE_FILE
        )

        # JSON structure is nested, so use standard json
        import json

        with open(
            SENSOR_BASELINE_FILE,
            "r"
        ) as file:

            sensor_data = json.load(file)

        adc_baseline = sensor_data["adc_sensor"]

        sensor_min = adc_baseline["normal_min"]
        sensor_max = adc_baseline["normal_max"]
        sensor_mean = adc_baseline["mean"]
        sensor_median = adc_baseline["median"]

    except Exception:

        sensor_min = None
        sensor_max = None
        sensor_mean = None
        sensor_median = None


# ============================================================
# REPLAY SETTINGS
# ============================================================

st.sidebar.header("CAN Replay")

replay_speed = st.sidebar.number_input(
    "Frame interval (seconds)",
    min_value=0.1,
    max_value=10.0,
    value=1.0,
    step=0.1
)

start_replay = st.sidebar.button(
    "▶ Start Replay"
)

reset_replay = st.sidebar.button(
    "↻ Reset Replay"
)


# ============================================================
# SESSION STATE
# ============================================================

if "replay_running" not in st.session_state:

    st.session_state.replay_running = False


if "current_frame" not in st.session_state:

    st.session_state.current_frame = 0


# ============================================================
# START REPLAY
# ============================================================

if start_replay:

    st.session_state.replay_running = True
    st.session_state.current_frame = 0


# ============================================================
# RESET REPLAY
# ============================================================

if reset_replay:

    st.session_state.replay_running = False
    st.session_state.current_frame = 0

    st.rerun()


# ============================================================
# REPLAY
# ============================================================

if (
    st.session_state.replay_running
    and not df.empty
):

    st.session_state.current_frame += 1

    if (
        st.session_state.current_frame
        > len(df)
    ):

        st.session_state.replay_running = False

        st.session_state.current_frame = len(df)


# ============================================================
# CURRENT DATA
# ============================================================

current_frame = st.session_state.current_frame


if current_frame > 0:

    displayed_df = df.iloc[
        :current_frame
    ].copy()

else:

    displayed_df = df.iloc[:0].copy()


# ============================================================
# SYSTEM / IDS STATUS
# ============================================================

st.subheader("System & IDS Status")


# ------------------------------------------------------------
# ALERT COUNTS
# ------------------------------------------------------------

if not alerts_df.empty:

    total_alerts = len(alerts_df)

    high_alerts = (
        alerts_df["Severity"]
        .astype(str)
        .str.upper()
        .eq("HIGH")
        .sum()
    )

    medium_alerts = (
        alerts_df["Severity"]
        .astype(str)
        .str.upper()
        .eq("MEDIUM")
        .sum()
    )

    low_alerts = (
        alerts_df["Severity"]
        .astype(str)
        .str.upper()
        .eq("LOW")
        .sum()
    )

else:

    total_alerts = 0
    high_alerts = 0
    medium_alerts = 0
    low_alerts = 0


# ------------------------------------------------------------
# STATUS
# ------------------------------------------------------------

if st.session_state.replay_running:

    status = "REPLAYING"

elif (
    current_frame >= len(df)
    and len(df) > 0
):

    status = "COMPLETE"

else:

    status = "READY"


# ------------------------------------------------------------
# STATUS METRICS
# ------------------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "CAN STATUS",
        status
    )


with col2:

    st.metric(
        "FRAMES RECEIVED",
        current_frame
    )


with col3:

    st.metric(
        "TOTAL ALERTS",
        total_alerts
    )


with col4:

    st.metric(
        "HIGH ALERTS",
        high_alerts
    )


with col5:

    st.metric(
        "MEDIUM ALERTS",
        medium_alerts
    )


# ============================================================
# REPLAY PROGRESS
# ============================================================

st.subheader("CAN Replay")


if len(df) > 0:

    progress = current_frame / len(df)

    st.progress(
        progress
    )

    st.write(
        f"Frame {current_frame} / {len(df)}"
    )

else:

    st.warning(
        "CAN log file not found."
    )


# ============================================================
# CAN STATISTICS
# ============================================================

st.subheader("CAN Statistics")


if not displayed_df.empty:

    stat1, stat2, stat3, stat4 = st.columns(4)


    # --------------------------------------------------------
    # PRESSED COUNT
    # --------------------------------------------------------

    pressed_count = (
        displayed_df["Button State"]
        .astype(str)
        .str.upper()
        .eq("PRESSED")
        .sum()
    )


    # --------------------------------------------------------
    # RELEASED COUNT
    # --------------------------------------------------------

    released_count = (
        displayed_df["Button State"]
        .astype(str)
        .str.upper()
        .eq("RELEASED")
        .sum()
    )


    # --------------------------------------------------------
    # EVENT INTERVAL
    # --------------------------------------------------------

    if len(displayed_df) > 1:

        event_times = pd.to_numeric(
            displayed_df["Event Time (ms)"],
            errors="coerce"
        ).dropna()

        if len(event_times) > 1:

            intervals = (
                event_times.diff()
                .dropna()
            )

            avg_interval = intervals.mean()

        else:

            avg_interval = 0

    else:

        avg_interval = 0


    # --------------------------------------------------------
    # EVENT RATE
    # --------------------------------------------------------

    if avg_interval > 0:

        event_rate = (
            1000 / avg_interval
        )

    else:

        event_rate = 0


    with stat1:

        st.metric(
            "PRESSED",
            pressed_count
        )


    with stat2:

        st.metric(
            "RELEASED",
            released_count
        )


    with stat3:

        st.metric(
            "AVG INTERVAL",
            f"{avg_interval:.2f} ms"
        )


    with stat4:

        st.metric(
            "EVENT RATE",
            f"{event_rate:.3f} /sec"
        )


else:

    st.info(
        "CAN statistics will appear when replay starts."
    )


# ============================================================
# CAN TRAFFIC
# ============================================================

st.subheader("Live CAN Traffic")


if not displayed_df.empty:

    st.dataframe(
        displayed_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "Press 'Start Replay' to begin CAN traffic."
    )


st.divider()


# ============================================================
# SENSOR MONITORING
# ============================================================

st.subheader("ADS1115 Sensor Monitoring")


if (
    not displayed_df.empty
    and "ADC Value" in displayed_df.columns
):

    # --------------------------------------------------------
    # CONVERT ADC VALUES
    # --------------------------------------------------------

    sensor_df = displayed_df.copy()

    sensor_df["ADC Value"] = pd.to_numeric(
        sensor_df["ADC Value"],
        errors="coerce"
    )

    sensor_df = sensor_df.dropna(
        subset=["ADC Value"]
    )


    # --------------------------------------------------------
    # SENSOR METRICS
    # --------------------------------------------------------

    sensor_col1, sensor_col2, sensor_col3, sensor_col4 = (
        st.columns(4)
    )


    current_adc = sensor_df[
        "ADC Value"
    ].iloc[-1]


    average_adc = sensor_df[
        "ADC Value"
    ].mean()


    minimum_adc = sensor_df[
        "ADC Value"
    ].min()


    maximum_adc = sensor_df[
        "ADC Value"
    ].max()


    with sensor_col1:

        st.metric(
            "CURRENT ADC",
            f"{current_adc:.0f}"
        )


    with sensor_col2:

        st.metric(
            "AVERAGE ADC",
            f"{average_adc:.1f}"
        )


    with sensor_col3:

        st.metric(
            "MIN ADC",
            f"{minimum_adc:.0f}"
        )


    with sensor_col4:

        st.metric(
            "MAX ADC",
            f"{maximum_adc:.0f}"
        )


    # --------------------------------------------------------
    # NORMAL RANGE
    # --------------------------------------------------------

    if (
        sensor_min is not None
        and sensor_max is not None
    ):

        st.info(
            f"Normal ADS1115 range: "
            f"{sensor_min:.0f} – {sensor_max:.0f}"
        )


    # --------------------------------------------------------
    # SENSOR GRAPH
    # --------------------------------------------------------

    st.write(
        "### ADS1115 ADC Value"
    )


    sensor_chart = sensor_df[
        ["ADC Value"]
    ].copy()


    st.line_chart(
        sensor_chart,
        use_container_width=True
    )


    # --------------------------------------------------------
    # SENSOR ANOMALIES IN REPLAY
    # --------------------------------------------------------

    if not alerts_df.empty:

        sensor_alerts = alerts_df[
            alerts_df["Anomaly Type"]
            .astype(str)
            .str.upper()
            .eq("ABNORMAL ADS1115 VALUE")
        ].copy()


        if not sensor_alerts.empty:

            sensor_alerts["Frame Number"] = (
                pd.to_numeric(
                    sensor_alerts["Frame Number"],
                    errors="coerce"
                )
            )


            visible_sensor_alerts = (
                sensor_alerts[
                    sensor_alerts["Frame Number"]
                    <= current_frame
                ]
            )


            if not visible_sensor_alerts.empty:

                st.warning(
                    f"⚠ "
                    f"{len(visible_sensor_alerts)} "
                    f"sensor anomaly/anomalies detected"
                )


                sensor_display_columns = [
                    "Frame Number",
                    "Severity",
                    "Anomaly Type",
                    "Expected Value",
                    "Actual Value",
                    "Description"
                ]


                available_sensor_columns = [
                    col
                    for col in sensor_display_columns
                    if col in visible_sensor_alerts.columns
                ]


                st.dataframe(
                    visible_sensor_alerts[
                        available_sensor_columns
                    ],
                    use_container_width=True,
                    hide_index=True
                )


            else:

                st.success(
                    "✓ No sensor anomalies detected "
                    "in the replayed frames"
                )

else:

    st.info(
        "ADS1115 sensor data will appear "
        "when CAN replay starts."
    )


st.divider()


# ============================================================
# IDS ALERT SECTION
# ============================================================

st.subheader("IDS Alerts")


if not alerts_df.empty:

    # --------------------------------------------------------
    # ONLY SHOW ALERTS FOR REPLAYED FRAMES
    # --------------------------------------------------------

    if "Frame Number" in alerts_df.columns:

        alerts_df["Frame Number"] = pd.to_numeric(
            alerts_df["Frame Number"],
            errors="coerce"
        )

        visible_alerts = alerts_df[
            alerts_df["Frame Number"]
            <= current_frame
        ]

    else:

        visible_alerts = alerts_df


    # --------------------------------------------------------
    # DISPLAY ALERTS
    # --------------------------------------------------------

    if not visible_alerts.empty:

        st.warning(
            f"⚠ "
            f"{len(visible_alerts)} "
            f"IDS alert(s) detected"
        )


        display_columns = [
            "Frame Number",
            "Severity",
            "CAN ID",
            "Anomaly Type",
            "Expected Value",
            "Actual Value",
            "ADC Value",
            "Description"
        ]


        available_columns = [
            col
            for col in display_columns
            if col in visible_alerts.columns
        ]


        st.dataframe(
            visible_alerts[
                available_columns
            ],
            use_container_width=True,
            hide_index=True
        )


    else:

        st.success(
            "✓ No IDS alerts detected "
            "in the replayed frames"
        )


else:

    st.success(
        "✓ No IDS alerts detected"
    )


# ============================================================
# VISUALIZATION SECTION
# ============================================================

st.subheader(
    "CAN Traffic Visualization"
)


if not displayed_df.empty:

    graph_col1, graph_col2 = st.columns(2)


    # ========================================================
    # EVENT INTERVAL GRAPH
    # ========================================================

    with graph_col1:

        st.write(
            "### Event Interval"
        )


        graph_df = displayed_df.copy()


        graph_df["Event Time (ms)"] = pd.to_numeric(
            graph_df["Event Time (ms)"],
            errors="coerce"
        )


        graph_df["Interval (ms)"] = (
            graph_df["Event Time (ms)"]
            .diff()
        )


        interval_data = graph_df[
            [
                "Event Time (ms)",
                "Interval (ms)"
            ]
        ].dropna()


        if not interval_data.empty:

            st.line_chart(
                interval_data.set_index(
                    "Event Time (ms)"
                )
            )

        else:

            st.info(
                "Waiting for more frames..."
            )


    # ========================================================
    # CAN ID DISTRIBUTION
    # ========================================================

    with graph_col2:

        st.write(
            "### CAN ID Distribution"
        )


        can_id_counts = (
            displayed_df["CAN ID"]
            .astype(str)
            .value_counts()
        )


        st.bar_chart(
            can_id_counts
        )


else:

    st.info(
        "Graphs will appear when CAN replay starts."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Intelligent CAN Monitoring & Intrusion Detection System"
)


# ============================================================
# AUTOMATIC REFRESH
# ============================================================

if st.session_state.replay_running:

    time.sleep(
        replay_speed
    )

    st.rerun()