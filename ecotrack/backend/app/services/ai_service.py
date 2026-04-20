from app.config import settings


def generate_action_plan(
    month: str,
    electricity_kwh: float,
    gas_kwh: float,
    water_liters: float,
    transport_km: float,
    carbon_kg: float,
    previous_carbon_kg: float = None,
) -> str:
    """
    Llama a la API de OpenAI para generar un plan de acción
    personalizado basado en los datos de consumo del usuario.
    Si no hay clave API configurada, devuelve un plan de ejemplo.
    """
    if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
        return _generate_fallback_plan(
            month, electricity_kwh, gas_kwh,
            water_liters, transport_km, carbon_kg, previous_carbon_kg,
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)

        change_text = ""
        if previous_carbon_kg and previous_carbon_kg > 0:
            change = ((carbon_kg - previous_carbon_kg) / previous_carbon_kg) * 100
            direction = "aumentó" if change > 0 else "disminuyó"
            change_text = f"Respecto al mes anterior, tu huella {direction} un {abs(change):.1f}%."

        prompt = f"""Eres un experto en sostenibilidad empresarial. Analiza los siguientes datos de consumo 
de una empresa para el mes {month} y genera un plan de acción personalizado en español.

DATOS DE CONSUMO:
- Electricidad: {electricity_kwh} kWh
- Gas natural: {gas_kwh} kWh  
- Agua: {water_liters} litros
- Transporte: {transport_km} km
- Huella de carbono total: {carbon_kg} kg CO2
{change_text}

Proporciona:
1. Un análisis breve de los datos (2-3 frases)
2. Las 3 acciones más importantes que debería tomar la empresa para reducir su huella
3. Un objetivo de reducción realista para el próximo mes

Sé específico, práctico y motivador. Formato con emojis para hacerlo visual."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception:
        return _generate_fallback_plan(
            month, electricity_kwh, gas_kwh,
            water_liters, transport_km, carbon_kg, previous_carbon_kg,
        )


def _generate_fallback_plan(
    month: str,
    electricity_kwh: float,
    gas_kwh: float,
    water_liters: float,
    transport_km: float,
    carbon_kg: float,
    previous_carbon_kg: float = None,
) -> str:
    """Plan de acción generado localmente sin necesidad de API."""
    tips = []

    if electricity_kwh > 500:
        tips.append("⚡ Tu consumo eléctrico es elevado. Considera instalar sensores de presencia en zonas comunes y revisar el uso de climatización fuera del horario laboral.")
    else:
        tips.append("⚡ Buen control del consumo eléctrico. Mantén el hábito de apagar equipos al finalizar la jornada.")

    if gas_kwh > 300:
        tips.append("🔥 El consumo de gas es significativo. Revisa el aislamiento del edificio y ajusta el termostato a 21°C en invierno. Cada grado menos supone un 7% de ahorro.")
    else:
        tips.append("🔥 El uso de gas está dentro de parámetros razonables. Mantén el mantenimiento regular de la calefacción.")

    if water_liters > 5000:
        tips.append("💧 El consumo de agua es alto. Instala grifos y cisternas de bajo consumo. Revisa posibles fugas en las instalaciones.")
    else:
        tips.append("💧 Buen control del agua. Considera instalar sistemas de recogida de agua de lluvia para riego.")

    if transport_km > 1000:
        tips.append("🚗 Alta movilidad en transporte. Fomenta el teletrabajo 2 días por semana y el uso del transporte público o bicicleta. Considera un plan de carpooling para empleados.")
    else:
        tips.append("🚗 Buen uso del transporte. Continúa fomentando reuniones virtuales para evitar desplazamientos innecesarios.")

    change_info = ""
    if previous_carbon_kg and previous_carbon_kg > 0:
        change = ((carbon_kg - previous_carbon_kg) / previous_carbon_kg) * 100
        if change > 0:
            change_info = f"\n📈 Tu huella aumentó un {change:.1f}% respecto al mes anterior. ¡Es momento de actuar!"
        else:
            change_info = f"\n📉 ¡Enhorabuena! Tu huella bajó un {abs(change):.1f}% respecto al mes anterior."

    objective = max(0, carbon_kg * 0.9)

    plan = f"""🌱 PLAN DE ACCIÓN PERSONALIZADO — {month}
{'=' * 50}

📊 RESUMEN DEL MES
Tu huella de carbono este mes fue de {carbon_kg:.1f} kg CO2.{change_info}

🎯 ACCIONES RECOMENDADAS

{chr(10).join(f'{i + 1}. {tip}' for i, tip in enumerate(tips))}

🏆 OBJETIVO PARA EL PRÓXIMO MES
Reducir la huella de carbono a {objective:.1f} kg CO2 
(una reducción del 10% es un objetivo realista y alcanzable).

💡 CONSEJO EXTRA
Comunica estos resultados a tu equipo. La sostenibilidad es un 
esfuerzo colectivo y la transparencia motiva la participación de todos.
"""
    return plan
