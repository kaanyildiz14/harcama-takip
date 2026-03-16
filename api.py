import requests

def doviz_kuru_getir():
    try:
        response = requests.get("https://api.exchangerate-api.com/v4/latest/TRY", timeout=5)
        data = response.json()
        return {
            "USD": round(1 / data["rates"]["USD"], 4),
            "EUR": round(1 / data["rates"]["EUR"], 4),
        }
    except Exception:
        return {"USD": None, "EUR": None}
