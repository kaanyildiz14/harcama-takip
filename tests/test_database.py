import pytest

import database


@pytest.fixture(autouse=True)
def gecici_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.tablo_olustur()


def test_harcama_ekle_ve_getir():
    database.harcama_ekle("Market", 150.5, "Alisveris", "2026-01-10")
    harcamalar = database.harcamalari_getir()
    assert len(harcamalar) == 1
    assert harcamalar[0][1:] == ("Market", 150.5, "Alisveris", "2026-01-10")


def test_tarihe_gore_yeniden_eskiye_siralar():
    database.harcama_ekle("Eski", 10, "Yemek", "2026-01-01")
    database.harcama_ekle("Yeni", 20, "Yemek", "2026-02-01")
    basliklar = [h[1] for h in database.harcamalari_getir()]
    assert basliklar == ["Yeni", "Eski"]


def test_kategori_filtresi():
    database.harcama_ekle("Otobus", 20, "Ulasim", "2026-01-01")
    database.harcama_ekle("Pizza", 250, "Yemek", "2026-01-02")
    assert [h[1] for h in database.harcamalari_getir("Yemek")] == ["Pizza"]
    assert len(database.harcamalari_getir("Tumu")) == 2


def test_kategori_toplamlari():
    database.harcama_ekle("Kahvalti", 100, "Yemek", "2026-01-01")
    database.harcama_ekle("Aksam", 300, "Yemek", "2026-01-02")
    database.harcama_ekle("Taksi", 80, "Ulasim", "2026-01-02")
    assert dict(database.kategori_toplamlari()) == {"Yemek": 400, "Ulasim": 80}


def test_harcama_sil():
    database.harcama_ekle("Silinecek", 5, "Diger", "2026-01-01")
    harcama_id = database.harcamalari_getir()[0][0]
    database.harcama_sil(harcama_id)
    assert database.harcamalari_getir() == []
