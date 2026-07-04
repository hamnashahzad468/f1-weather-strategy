import fastf1
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pandas as pd
import numpy as np
import os

# Setup cache
os.makedirs('f1_cache', exist_ok=True)
fastf1.Cache.enable_cache('f1_cache')

# Load 2026 Canadian GP
session = fastf1.get_session(2026, 'Canada', 'R')
session.load()

# Get weather data
weather = session.weather_data.copy()
weather['Time_sec'] = weather['Time'].dt.total_seconds()

# Get top 5 drivers lap data
drivers = ['RUS', 'VER', 'ANT', 'LEC', 'HAM']
driver_colors = {
    'RUS': '#00D2BE',
    'VER': '#FF8700',
    'ANT': '#00D2BE',
    'LEC': '#DC0000',
    'HAM': '#00D2BE'
}
driver_colors = {
    'RUS': '#00D2BE',
    'VER': '#FF8700',
    'ANT': '#6CD3BF',
    'LEC': '#DC0000',
    'HAM': '#ffffff'
}

# Collect pit stop laps per driver
pit_laps = {}
for driver in drivers:
    try:
        laps = session.laps.pick_drivers(driver).copy()
        laps['LapTimeSec'] = laps['LapTime'].dt.total_seconds()
        pit_laps[driver] = laps
    except Exception as e:
        print(f"Skipped {driver}: {e}")

# Get total laps
total_laps = session.total_laps

# --- Plotting ---
fig = plt.figure(figsize=(14, 12))
fig.suptitle('Weather & Strategy Decision Tool — Canadian GP 2026',
             fontsize=14, fontweight='bold')

gs = gridspec.GridSpec(4, 1, height_ratios=[2, 1, 1, 1], hspace=0.4)

# --- Plot 1: Lap times per driver ---
ax1 = fig.add_subplot(gs[0])
for driver, laps in pit_laps.items():
    clean = laps[laps['LapTimeSec'] < laps['LapTimeSec'].median() * 1.15]
    ax1.plot(clean['LapNumber'], clean['LapTimeSec'],
             label=driver, color=driver_colors[driver],
             linewidth=1.5, alpha=0.85)

ax1.set_ylabel('Lap Time (seconds)', fontsize=10)
ax1.set_title('Driver Lap Times', fontsize=11)
ax1.legend(loc='upper right', fontsize=9)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(1, total_laps)

# --- Plot 2: Track temperature ---
ax2 = fig.add_subplot(gs[1])
# Convert weather time to lap number approximation
weather['LapApprox'] = (weather['Time_sec'] /
                         weather['Time_sec'].max() * total_laps)
ax2.plot(weather['LapApprox'], weather['TrackTemp'],
         color='#FF8700', linewidth=2, label='Track Temp (°C)')
ax2.fill_between(weather['LapApprox'], weather['TrackTemp'],
                 alpha=0.2, color='#FF8700')
ax2.set_ylabel('Track Temp (°C)', fontsize=10)
ax2.set_title('Track Temperature', fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.set_xlim(1, total_laps)

# --- Plot 3: Rainfall ---
ax3 = fig.add_subplot(gs[2])
ax3.fill_between(weather['LapApprox'], weather['Rainfall'].astype(int),
                 color='#0067FF', alpha=0.6, label='Rainfall')
ax3.plot(weather['LapApprox'], weather['Rainfall'].astype(int),
         color='#0067FF', linewidth=1.5)
ax3.set_ylabel('Rainfall', fontsize=10)
ax3.set_title('Rain Events', fontsize=11)
ax3.set_yticks([0, 1])
ax3.set_yticklabels(['Dry', 'Rain'])
ax3.grid(True, alpha=0.3)
ax3.set_xlim(1, total_laps)

# --- Plot 4: Wind speed ---
ax4 = fig.add_subplot(gs[3])
ax4.plot(weather['LapApprox'], weather['WindSpeed'],
         color='#AAAAAA', linewidth=2, label='Wind Speed (m/s)')
ax4.fill_between(weather['LapApprox'], weather['WindSpeed'],
                 alpha=0.2, color='#AAAAAA')
ax4.set_ylabel('Wind Speed (m/s)', fontsize=10)
ax4.set_xlabel('Lap Number', fontsize=10)
ax4.set_title('Wind Speed', fontsize=11)
ax4.grid(True, alpha=0.3)
ax4.set_xlim(1, total_laps)

plt.savefig('weather_strategy.png', dpi=150, bbox_inches='tight')
plt.show()

# Print weather summary
print(f"\nWeather Summary — Canadian GP 2026")
print(f"Avg Track Temperature: {weather['TrackTemp'].mean():.1f}°C")
print(f"Max Track Temperature: {weather['TrackTemp'].max():.1f}°C")
print(f"Avg Wind Speed: {weather['WindSpeed'].mean():.1f} m/s")
print(f"Rain detected: {'Yes' if weather['Rainfall'].any() else 'No'}")
