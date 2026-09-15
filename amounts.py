import math


def tutar_dogrula(deger):
    """Pozitif, sonlu bir tutar döndür; virgüllü ondalıkları da kabul et."""
    if isinstance(deger, str):
        deger = deger.strip().replace(",", ".")
    try:
        miktar = float(deger)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Geçerli bir miktar girin.") from exc
    if not math.isfinite(miktar) or miktar <= 0:
        raise ValueError("Geçerli bir miktar girin.")
    return miktar
