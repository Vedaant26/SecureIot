"""
SecureIoT Privacy Module
Pseudonymisation, aggregation, noise addition (differential privacy).
"""

import hashlib
import random
import statistics


# ════════════════════════════════════════════
#  1. Pseudonymisation
# ════════════════════════════════════════════

def pseudonymise(records):
    """
    Replace identifying fields with pseudonyms.
    Input: list of dicts with 'device_id', 'location', 'value' keys.
    Returns: original and pseudonymised side by side.
    """
    results = []
    for record in records:
        pseudo_id = "DEV-" + hashlib.sha256(record["device_id"].encode()).hexdigest()[:8].upper()
        pseudo_loc = "LOC-" + hashlib.sha256(record["location"].encode()).hexdigest()[:6].upper()
        results.append({
            "original": record,
            "pseudonymised": {
                "device_id": pseudo_id,
                "location": pseudo_loc,
                "value": record["value"],
            },
        })
    return {
        "technique": "Pseudonymisation",
        "description": "Device IDs and locations are replaced with consistent hash-based pseudonyms. The original identity cannot be recovered without the mapping table.",
        "records": results,
    }


# ════════════════════════════════════════════
#  2. Data Aggregation
# ════════════════════════════════════════════

def aggregate_data(records):
    """
    Aggregate individual readings into summary statistics.
    Input: list of dicts with 'device_id' and 'value' (numeric) keys.
    Returns: aggregated statistics instead of individual data.
    """
    values = [r["value"] for r in records]

    aggregated = {
        "count": len(values),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "std_dev": round(statistics.stdev(values), 2) if len(values) > 1 else 0,
    }

    return {
        "technique": "Data Aggregation",
        "description": "Individual device readings are combined into summary statistics. No single device's data can be identified from the aggregated result.",
        "individual_records": records,
        "aggregated_result": aggregated,
    }


# ════════════════════════════════════════════
#  3. Noise Addition (Differential Privacy)
# ════════════════════════════════════════════

def add_noise(records, epsilon=1.0):
    """
    Add Laplacian noise to numeric values for differential privacy.
    Lower epsilon = more privacy (more noise).
    """
    sensitivity = 1.0
    scale = sensitivity / epsilon
    noisy_records = []

    for record in records:
        original_value = record["value"]
        # Add Laplace noise
        noise = random.uniform(-1, 1) * scale
        # Simple approximation of Laplace using uniform
        noise = (random.expovariate(1/scale) - random.expovariate(1/scale))
        noisy_value = round(original_value + noise, 2)
        noisy_records.append({
            "device_id": record["device_id"],
            "original_value": original_value,
            "noise_added": round(noise, 4),
            "noisy_value": noisy_value,
        })

    return {
        "technique": "Noise Addition (Differential Privacy)",
        "description": f"Random Laplacian noise (ε={epsilon}) is added to each reading. This protects individual data points while preserving overall statistical patterns.",
        "epsilon": epsilon,
        "scale": round(scale, 4),
        "records": noisy_records,
    }


# ════════════════════════════════════════════
#  Demonstrate All Privacy Techniques
# ════════════════════════════════════════════

def get_sample_data():
    """Generate sample IoT data for privacy demonstrations."""
    return [
        {"device_id": "TEMP-001", "location": "Floor 1 - Lobby", "value": 23.5},
        {"device_id": "TEMP-002", "location": "Floor 2 - Office", "value": 24.1},
        {"device_id": "ENERGY-001", "location": "Floor 1", "value": 2.4},
        {"device_id": "ENERGY-002", "location": "Floor 2", "value": 3.1},
        {"device_id": "MOTION-001", "location": "Corridor A", "value": 1.0},
        {"device_id": "MOTION-002", "location": "Parking Lot", "value": 0.0},
    ]


def demonstrate_all(sample_data=None):
    """Run all three privacy techniques on sample data."""
    if sample_data is None:
        sample_data = get_sample_data()

    return {
        "pseudonymisation": pseudonymise(sample_data),
        "aggregation": aggregate_data(sample_data),
        "noise_addition": add_noise(sample_data, epsilon=1.0),
    }
