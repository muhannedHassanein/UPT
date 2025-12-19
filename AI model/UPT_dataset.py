import random
import math
import csv
from datetime import datetime, timedelta

# ================== الإعدادات ==================

NUM_SAMPLES = 150000
FILE_NAME = "dive_site_dataset.csv"

BASE_LAT = 31.3100   # أبو قير
BASE_LON = 29.9000
MAX_OFFSET = 0.01

# ================== دوال مساعدة ==================

def random_coord(base, max_offset=MAX_OFFSET):
    return round(base + random.uniform(-max_offset, max_offset), 6)

def random_time_in_month(year, month):
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)

    delta = end_date - start_date
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start_date + timedelta(seconds=random_seconds)

def noise(value, amount):
    return value + random.uniform(-amount, amount)

def classify_site(temp, ph, oxy, turb, light, change_factor):
    danger = 0
    unstable = 0

    if temp < 18 or temp > 32:
        danger += 1
    if ph < 7.5 or ph > 8.6:
        danger += 1
    if oxy < 4:
        danger += 1
    if turb > 8:
        danger += 1
    if light < 80:
        unstable += 1
    if change_factor > 4:
        unstable += 1
    if oxy < 5:
        unstable += 1

    if danger >= 2:
        return "Dangerous"
    elif unstable >= 2:
        return "Unstable"
    else:
        return "Stable"

# ================== توليد البيانات ==================

previous_temp = 25
previous_ph = 8.1
previous_oxy = 6

data = []

samples_per_month = NUM_SAMPLES // 12
year = 2024

for month in range(1, 13):
    for _ in range(samples_per_month):

        timestamp = random_time_in_month(year, month)

        lat = random_coord(BASE_LAT)
        lon = random_coord(BASE_LON)

        depth = round(random.uniform(2, 40), 2)

        # القيم الأساسية حسب الموسم
        if month in [12, 1, 2]:          # شتاء
            base_temp = 19 - 0.05 * depth
            light_base = 800
            turbidity_base = depth / 4
        elif month in [3, 4, 5]:         # ربيع
            base_temp = 22 - 0.05 * depth
            light_base = 1000
            turbidity_base = depth / 5
        elif month in [6, 7, 8]:         # صيف
            base_temp = 28 - 0.05 * depth
            light_base = 1200
            turbidity_base = depth / 6
        else:                            # خريف
            base_temp = 23 - 0.05 * depth
            light_base = 900
            turbidity_base = depth / 5

        temp = round(noise(base_temp, random.uniform(0.5, 2)), 2)
        ph = round(noise(8.1 - 0.003 * depth, 0.2), 2)
        oxygen = round(noise(6.5 - 0.05 * depth, 0.8), 2)
        turbidity = round(abs(noise(turbidity_base, 1.5)), 2)
        light = round(
            max(50, light_base * math.exp(-0.15 * depth) + random.uniform(-100, 100)),
            1
        )
        co2 = round(random.uniform(400, 500), 1)
        salinity = round(random.uniform(36, 38), 2)

        change = abs(temp - previous_temp) + abs(ph - previous_ph) + abs(oxygen - previous_oxy)

        status = classify_site(temp, ph, oxygen, turbidity, light, change)

        data.append([
            timestamp,
            lat, lon, depth,
            temp, ph, salinity,
            oxygen, co2,
            light, turbidity,
            round(change, 2),
            status
        ])

        previous_temp = temp
        previous_ph = ph
        previous_oxy = oxygen

# ================== حفظ الملف ==================

with open(FILE_NAME, "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow([
        "timestamp",
        "latitude", "longitude", "depth_m",
        "temp_c", "pH", "salinity",
        "dissolved_oxygen", "co2_ppm",
        "light_intensity", "turbidity",
        "change_factor", "site_status"
    ])
    writer.writerows(data)

print("\n✅ Dataset generated successfully")
print(f"📁 File: {FILE_NAME}")
print(f"📊 Samples: {len(data)}")
