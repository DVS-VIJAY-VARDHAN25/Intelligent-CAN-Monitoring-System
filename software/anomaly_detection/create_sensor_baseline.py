import pandas as pd
import json
import os

# ==============================
# FILE PATHS
# ==============================

INPUT_FILE = "can_log.csv"
OUTPUT_FILE = "data/processed/sensor_baseline.json"


# ==============================
# LOAD DATA
# ==============================

print("==============================================")
print("        SENSOR BASELINE GENERATOR")
print("==============================================")

print("\nLoading CAN dataset...")

df = pd.read_csv(INPUT_FILE)

print("Dataset loaded successfully.")
print(f"Total frames: {len(df)}")


# ==============================
# CHECK ADC COLUMN
# ==============================

if "ADC Value" not in df.columns:
    print("\nERROR: ADC Value column not found!")
    exit()

adc = df["ADC Value"].astype(float)


# ==============================
# ROBUST SENSOR STATISTICS
# ==============================

median = adc.median()

q1 = adc.quantile(0.25)
q3 = adc.quantile(0.75)

iqr = q3 - q1

# IQR-based limits
lower_limit = q1 - (1.5 * iqr)
upper_limit = q3 + (1.5 * iqr)


# ==============================
# IDENTIFY POSSIBLE OUTLIERS
# ==============================

outliers = df[
    (df["ADC Value"] < lower_limit) |
    (df["ADC Value"] > upper_limit)
]

# Values considered normal for baseline calculation
normal_adc = df[
    (df["ADC Value"] >= lower_limit) &
    (df["ADC Value"] <= upper_limit)
]["ADC Value"]


# ==============================
# FINAL NORMAL RANGE
# ==============================

normal_min = float(normal_adc.min())
normal_max = float(normal_adc.max())

normal_mean = float(normal_adc.mean())
normal_median = float(normal_adc.median())


# ==============================
# CREATE BASELINE
# ==============================

baseline = {
    "baseline_name": "ADS1115 Sensor Normal Baseline",
    "version": "1.0",

    "source_dataset": INPUT_FILE,

    "total_frames": int(len(df)),

    "adc_sensor": {
        "sensor": "ADS1115",
        "channel": "A0",

        "normal_min": normal_min,
        "normal_max": normal_max,

        "mean": normal_mean,
        "median": normal_median,

        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),

        "iqr_lower_limit": float(lower_limit),
        "iqr_upper_limit": float(upper_limit),

        "outliers_detected_during_baseline": int(len(outliers))
    }
}


# ==============================
# CREATE OUTPUT DIRECTORY
# ==============================

os.makedirs("data/processed", exist_ok=True)


# ==============================
# SAVE JSON
# ==============================

with open(OUTPUT_FILE, "w") as file:
    json.dump(baseline, file, indent=4)


# ==============================
# DISPLAY RESULTS
# ==============================

print("\n==============================================")
print("          SENSOR BASELINE RESULTS")
print("==============================================")

print(f"ADC minimum in dataset : {adc.min():.2f}")
print(f"ADC maximum in dataset : {adc.max():.2f}")
print(f"ADC median             : {median:.2f}")

print("\nIQR analysis:")
print(f"Q1                     : {q1:.2f}")
print(f"Q3                     : {q3:.2f}")
print(f"IQR                    : {iqr:.2f}")

print("\nDetected possible outliers:")
print(f"Count                  : {len(outliers)}")

if len(outliers) > 0:
    print("\nOutlier frames:")
    for _, row in outliers.iterrows():
        print(
            f"Frame {int(row['Packet Counter'])}"
            f" → ADC = {row['ADC Value']}"
        )

print("\nNormal sensor range used for baseline:")
print(f"Minimum                : {normal_min:.2f}")
print(f"Maximum                : {normal_max:.2f}")
print(f"Mean                   : {normal_mean:.2f}")
print(f"Median                 : {normal_median:.2f}")

print("\nBaseline saved to:")
print(OUTPUT_FILE)

print("\nRESULT: SENSOR BASELINE CREATED")
print("==============================================")