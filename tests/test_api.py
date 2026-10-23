from unittest.mock import MagicMock, patch

import api


def test_doviz_kuru_tl_karsiligini_hesaplar():
    yanit = MagicMock()
    yanit.json.return_value = {"rates": {"USD": 0.025, "EUR": 0.02}}
    with patch("api.requests.get", return_value=yanit):
        assert api.doviz_kuru_getir() == {"USD": 40.0, "EUR": 50.0}


def test_baglanti_hatasinda_none_doner():
    with patch("api.requests.get", side_effect=Exception("ag yok")):
        assert api.doviz_kuru_getir() == {"USD": None, "EUR": None}
