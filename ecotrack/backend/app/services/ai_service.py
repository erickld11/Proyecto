from app.config import settings


def generate_action_plan(month, electricity_kwh, gas_kwh, water_liters, transport_km, carbon_kg, previous_carbon_kg=None):
    if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
        return _generate_fallback_plan(month, electricity_kwh, gas_kwh, water_liters, transport_km, carbon_kg, previous_carbon_kg)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        change_text = ""
        if previous_carbon_kg and previous_carbon_kg > 0:
            change = ((carbon_kg - previous_carbon_kg) / previous_carbon_kg) * 100
            direction = "aumentó" if change > 0 else "disminuyó"
            change_text = f"Respecto al mes anterior, tu huella {direction} un {abs(change):.1f}%."

        prompt = f"""Eres un experto en sostenibilidad empresarial. Analiza los datos de consumo del mes {month}:
- Electricidad: {electricity_kwh} kWh
- Gas: {gas_kwh} kWh
- Agua: {water_liters} litros
- Transporte: {transport_km} km
- Huella total: {carbon_kg} kg CO2
{change_text}
Proporciona: 1) Análisis breve 2) 3 acciones prioritarias 3) Objetivo para el próximo mes. Usa emojis."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception:
        return _generate_fallback_plan(month, electricity_kwh, gas_kwh, water_liters, transport_km, carbon_kg, previous_carbon_kg)


def _generate_fallback_plan(month, electricity_kwh, gas_kwh, water_liters, transport_km, carbon_kg, previous_carbon_kg=None):
    tips = []
    if electricity_kwh > 500:
        tips.append("⚡ Tu consumo eléctrico es elevado. Instala sensores de presencia y revisa climatización fuera del horario laboral.")
    else:
        tips.append("⚡ Buen control eléctrico. Sigue apagando equipos al finalizar la jornada.")

    if gas_kwh > 300:
        tips.append("🔥 Gas significativo. Revisa el aislamiento y ajusta el termostato a 21°C. Cada grado menos ahorra un 7%.")
    else:
        tips.append("🔥 Uso de gas razonable. Mantén el mantenimiento regular de la calefacción.")

    if water_liters > 5000:
        tips.append("💧 Agua alta. Instala grifos de bajo consumo y revisa posibles fugas.")
    else:
        tips.append("💧 Buen control del agua. Considera sistemas de reutilización.")

    if transport_km > 1000:
        tips.append("🚗 Alta movilidad. Fomenta teletrabajo 2 días/semana y carpooling entre empleados.")
    else:
        tips.append("🚗 Buen uso del transporte. Continúa fomentando reuniones virtuales.")

    change_info = ""
    if previous_carbon_kg and previous_carbon_kg > 0:
        change = ((carbon_kg - previous_carbon_kg) / previous_carbon_kg) * 100
        if change > 0:
            change_info = f"\n📈 Tu huella aumentó un {change:.1f}% respecto al mes anterior. ¡Es momento de actuar!"
        else:
            change_info = f"\n📉 ¡Enhorabuena! Tu huella bajó un {abs(change):.1f}% respecto al mes anterior."

    objective = max(0, carbon_kg * 0.9)
    return f"""🌱 PLAN DE ACCIÓN PERSONALIZADO — {month}
{'=' * 50}

📊 RESUMEN DEL MES
Tu huella de carbono este mes fue de {carbon_kg:.1f} kg CO2.{change_info}

🎯 ACCIONES RECOMENDADAS

{chr(10).join(f'{i+1}. {tip}' for i, tip in enumerate(tips))}

🏆 OBJETIVO PARA EL PRÓXIMO MES
Reducir la huella a {objective:.1f} kg CO2 (reducción del 10%).

💡 CONSEJO EXTRA
Comunica estos resultados a tu equipo. La sostenibilidad es un esfuerzo colectivo.
"""
