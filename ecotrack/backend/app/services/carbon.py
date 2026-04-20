# Factores de emisión (kg CO2 por unidad)
# Fuente: IPCC / IDAE España
ELECTRICITY_FACTOR = 0.233   # kg CO2 por kWh (red eléctrica española)
GAS_FACTOR = 0.202            # kg CO2 por kWh de gas natural
WATER_FACTOR = 0.000298       # kg CO2 por litro
TRANSPORT_FACTOR = 0.171      # kg CO2 por km (coche medio gasolina)


def calculate_carbon_footprint(
    electricity_kwh: float,
    gas_kwh: float,
    water_liters: float,
    transport_km: float,
) -> float:
    """
    Calcula la huella de carbono total en kg de CO2.
    Devuelve el resultado redondeado a 2 decimales.
    """
    total = (
        electricity_kwh * ELECTRICITY_FACTOR
        + gas_kwh * GAS_FACTOR
        + water_liters * WATER_FACTOR
        + transport_km * TRANSPORT_FACTOR
    )
    return round(total, 2)


def get_carbon_breakdown(
    electricity_kwh: float,
    gas_kwh: float,
    water_liters: float,
    transport_km: float,
) -> dict:
    """Devuelve el desglose por categoría en kg CO2."""
    return {
        "electricity": round(electricity_kwh * ELECTRICITY_FACTOR, 2),
        "gas": round(gas_kwh * GAS_FACTOR, 2),
        "water": round(water_liters * WATER_FACTOR, 2),
        "transport": round(transport_km * TRANSPORT_FACTOR, 2),
    }
