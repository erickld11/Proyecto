ELECTRICITY_FACTOR = 0.233
GAS_FACTOR = 0.202
WATER_FACTOR = 0.000298
TRANSPORT_FACTOR = 0.171


def calculate_carbon_footprint(electricity_kwh, gas_kwh, water_liters, transport_km):
    total = (
        electricity_kwh * ELECTRICITY_FACTOR
        + gas_kwh * GAS_FACTOR
        + water_liters * WATER_FACTOR
        + transport_km * TRANSPORT_FACTOR
    )
    return round(total, 2)


def get_carbon_breakdown(electricity_kwh, gas_kwh, water_liters, transport_km):
    return {
        "electricity": round(electricity_kwh * ELECTRICITY_FACTOR, 2),
        "gas": round(gas_kwh * GAS_FACTOR, 2),
        "water": round(water_liters * WATER_FACTOR, 2),
        "transport": round(transport_km * TRANSPORT_FACTOR, 2),
    }
