"""Utility meter tracker with tiered billing and spike detection."""

import json
import math
from datetime import datetime

BASE_RATES = (3.5, 5.0, 7.5)
SPIKE_LIMIT = 500
TIER_1_UNITS = 100
TIER_2_UNITS = 200


def record_reading(meters, meter_id, units, history=None):
    """Add units to a meter, log the reading and return the history."""
    if units < 0:
        raise ValueError(f"negative reading rejected for {meter_id}")
    if history is None:
        history = []
    history.append((meter_id, units, str(datetime.now())))
    meters[meter_id] = meters.get(meter_id, 0) + units
    return history


def compute_bill(meters, meter_id, tier_rates):
    """Return the three-tier bill for a meter."""
    units = meters[meter_id]
    slab_1 = min(units, TIER_1_UNITS)
    slab_2 = min(max(units - TIER_1_UNITS, 0), TIER_2_UNITS)
    slab_3 = max(units - TIER_1_UNITS - TIER_2_UNITS, 0)
    slabs = (slab_1, slab_2, slab_3)
    return sum(u * r for u, r in zip(slabs, tier_rates))


def raise_rates(rates, percent):
    """Return a new list of rates increased by the given percentage."""
    return [rate * (1 + percent / 100) for rate in rates]


def flag_spikes(meters, limit=SPIKE_LIMIT):
    """Return the ids of meters whose total exceeds the limit."""
    return [meter for meter, total in meters.items() if total > limit]


def load_meter_data(file="meters.json"):
    """Load meter totals from disk, or return an empty dict."""
    try:
        with open(file, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError):
        return {}


def save_meter_data(meters, file="meters.json"):
    """Write meter totals to disk."""
    with open(file, "w", encoding="utf-8") as handle:
        json.dump(meters, handle)


def parse_units(text):
    """Convert user input to a finite number of units."""
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("units must be a finite number")
    return value


def main():
    """Run the demo."""
    meters = {}
    history = []
    record_reading(meters, "M-01", 120, history)
    record_reading(meters, "M-02", 640, history)
    try:
        record_reading(meters, "M-03", -50, history)
    except ValueError as err:
        print("Rejected:", err)
    print("Readings stored so far:", len(history))
    rates = raise_rates(BASE_RATES, 10)
    print(f"Bill M-01: {compute_bill(meters, 'M-01', rates):.2f}")
    print("Spikes:", flag_spikes(meters))
    adjustment = input("Extra units for M-01 (Enter for 0): ") or "0"
    try:
        record_reading(meters, "M-01", parse_units(adjustment), history)
    except ValueError as err:
        print("Invalid input:", err)
    save_meter_data(meters)
    meters = load_meter_data()
    print(f"Bill M-01 after reload: {compute_bill(meters, 'M-01', rates):.2f}")


if __name__ == "__main__":
    main()
