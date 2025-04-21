import requests
import os
from datetime import datetime, timedelta

API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LEAGUES = {
    'NBA': 'basketball_nba',
    'Euroleague': 'basketball_euroleague',
    'CBA': 'basketball_china'
}

def obtener_fecha_objetivo():
    hoy = datetime.utcnow().date()
    fechas = [(hoy + timedelta(days=i)).isoformat() for i in range(1, 3)]
    return fechas

def obtener_odds_por_liga(league_key, fechas):
    url = f"https://api.the-odds-api.com/v4/sports/{league_key}/odds"
    all_odds = []
    for date in fechas:
        params = {
            'apiKey': API_KEY,
            'regions': 'us',
            'markets': 'totals',
            'oddsFormat': 'decimal',
            'dateFormat': 'iso',
            'date': date
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            all_odds.extend(response.json())
    return all_odds

def mostrar_predicciones(odds, liga):
    mensajes = [f"🏀 *Pronósticos Over/Under - {liga}*"]
    for partido in odds:
        local = partido['home_team']
        visitante = partido['away_team']
        try:
            outcomes = partido['bookmakers'][0]['markets'][0]['outcomes']
            over = next(o for o in outcomes if o['name'] == 'Over')
            under = next(o for o in outcomes if o['name'] == 'Under')
            recomendado = 'Over' if over['price'] < under['price'] else 'Under'
            linea = over['point']
            mensaje = (
                f"{local} vs {visitante}\n"
                f"  Línea: {linea} | Over: {over['price']} | Under: {under['price']}\n"
                f"  👉 Recomendación: *{recomendado}*"
            )
            mensajes.append(mensaje)
        except (KeyError, IndexError, StopIteration):
            mensajes.append(f"{local} vs {visitante} — Datos insuficientes.")
    return "\n\n".join(mensajes)

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': mensaje,
        'parse_mode': 'Markdown'
    }
    requests.post(url, data=payload)

def main():
    fechas = obtener_fecha_objetivo()
    for liga, clave in LEAGUES.items():
        odds = obtener_odds_por_liga(clave, fechas)
        if odds:
            mensaje = mostrar_predicciones(odds, liga)
            enviar_telegram(mensaje)

if __name__ == "__main__":
    main()