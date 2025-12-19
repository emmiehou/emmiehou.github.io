#!/usr/bin/env python3
import argparse
import csv
import math
import sys
from typing import List, Tuple, Optional

import os

import matplotlib.pyplot as plt

# Use Tk only when we need to open a dialog (avoids GUI init in CLI-only usage)
def pick_file_with_dialog() -> Optional[str]:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select CSV file",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    root.update()
    root.destroy()
    return path or None

def seconds_to_hms(seconds: float) -> str:
    total = int(max(0, round(seconds)))
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def to_hms(value: str) -> str:
    s = (value or "").strip()
    if not s:
        return ""
    # If it's already time-like (has ':') assume it's hh:mm:ss
    if ":" in s:
        parts = s.split(":")
        try:
            parts = [int(float(p)) for p in parts]
            while len(parts) < 3:
                parts.insert(0, 0)  # pad to hh:mm:ss
            h, m, sec = parts[-3], parts[-2], parts[-1]
            # Normalize minutes/seconds if out of range
            total = max(0, h) * 3600 + max(0, m) * 60 + max(0, sec)
            return seconds_to_hms(total)
        except Exception:
            # Keep as-is if parsing fails
            return s
    # Otherwise attempt seconds -> hh:mm:ss
    try:
        return seconds_to_hms(float(s))
    except Exception:
        return s

def try_float(s: str) -> Optional[float]:
    try:
        return float(str(s).strip())
    except Exception:
        return None

def looks_like_header(row: List[str]) -> bool:
    # If both target numeric cols (2 and 4) are non-numeric, likely a header
    if len(row) < 4:
        return False
    return try_float(row[1]) is None and try_float(row[3]) is None

def process_csv(path: str) -> Tuple[List[str], List[float], List[float]]:
    """
    Returns: (labels_hms, day1_values, day2_values)
    - labels_hms: formatted "hh:mm:ss" strings from column 1
    - day1_values: floats from column 2
    - day2_values: floats from column 4
    Skips empty/invalid rows.
    """
    labels: List[str] = []
    day1: List[float] = []
    day2: List[float] = []

    with open(path, newline="") as f:
        reader = csv.reader(f)
        rows = [r for r in reader if r and any(c.strip() for c in r)]

    if not rows:
        raise ValueError("The CSV appears to be empty.")

    start = 1 if looks_like_header(rows[0]) else 0
    for r in rows[start:]:
        if len(r) < 4:
            continue
        t_raw = r[0]
        d1 = try_float(r[1])
        d2 = try_float(r[3])
        if t_raw is None or d1 is None or d2 is None:
            continue
        labels.append(to_hms(str(t_raw)))
        day1.append(d1)
        day2.append(d2)

    if not labels:
        raise ValueError("No valid data rows found. Ensure columns 2 and 4 contain numbers.")

    return labels, day1, day2

def annotate_max(ax, x_positions: List[int], y_values: List[float], color: str):
    if not y_values:
        return
    max_idx = max(range(len(y_values)), key=lambda i: y_values[i])
    max_val = y_values[max_idx]
    x = x_positions[max_idx]
    y = max_val
    ax.scatter([x], [y], color=color, s=40, zorder=3)
    # Slight vertical offset for the label
    ax.annotate(f"{max_val:g}", xy=(x, y), xytext=(0, 8),
                textcoords="offset points", ha="center", va="bottom",
                color=color, fontsize=9,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=0.5))

def plot_graph(labels: List[str], day1: List[float], day2: List[float], title: str):
    # Use categorical x-axis positions
    x = list(range(len(labels)))

    plt.figure(figsize=(10, 5))
    ax = plt.gca()

    # Plot lines
    ax.plot(x, day1, color="red", label="Day 1", linewidth=2)
    ax.plot(x, day2, color="blue", label="Day 2", linewidth=2)

    # Axis labels and title
    ax.set_xlabel("time elapsed (hh:mm:ss)")
    ax.set_ylabel("pellets eaten")
    if title:
        ax.set_title(title)

    # X ticks
    # If many points, thin the tick labels to keep it readable
    max_ticks = 20
    if len(labels) > max_ticks:
        step = math.ceil(len(labels) / max_ticks)
        tick_positions = list(range(0, len(labels), step))
        tick_labels = [labels[i] for i in tick_positions]
    else:
        tick_positions = x
        tick_labels = labels
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha="right")

    # Annotate maxima
    annotate_max(ax, x, day1, color="red")
    annotate_max(ax, x, day2, color="blue")

    ax.legend(loc="best")
    ax.grid(True, linestyle="--", alpha=0.3)

    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Plot pellets eaten for Day 1 (col 2) and Day 2 (col 4) vs time (col 1).")
    parser.add_argument("--file", "-f", type=str, help="Path to CSV file.")
    parser.add_argument("--title", "-t", type=str, help="Graph title.")
    args = parser.parse_args()

    csv_path = args.file
    if not csv_path:
        csv_path = pick_file_with_dialog()
        if not csv_path:
            print("No file selected. Provide --file path/to/file.csv", file=sys.stderr)
            sys.exit(1)

    title = args.title if args.title is not None else input("Enter graph title (or leave blank): ").strip()

    try:
        labels, d1, d2 = process_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV: {e}", file=sys.stderr)
        sys.exit(1)

    plot_graph(labels, d1, d2, title)

if __name__ == "__main__":
    main()