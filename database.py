import sqlite3
import os
from amounts import tutar_dogrula

DB_PATH = os.environ.get(
    "HARCAMA_DB", os.path.join(os.path.dirname(__file__), "harcamalar.db")
)

def baglanti():
    return sqlite3.connect(DB_PATH)

def tablo_olustur():
    with baglanti() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS harcamalar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                baslik TEXT NOT NULL,
                miktar REAL NOT NULL,
                kategori TEXT NOT NULL,
                tarih TEXT NOT NULL
            )
        """)

def harcama_ekle(baslik, miktar, kategori, tarih):
    miktar = tutar_dogrula(miktar)
    with baglanti() as conn:
        conn.execute(
            "INSERT INTO harcamalar (baslik, miktar, kategori, tarih) VALUES (?, ?, ?, ?)",
            (baslik, miktar, kategori, tarih)
        )

def harcamalari_getir(kategori_filtre=None):
    with baglanti() as conn:
        if kategori_filtre and kategori_filtre != "Tumu":
            return conn.execute(
                "SELECT * FROM harcamalar WHERE kategori=? ORDER BY tarih DESC",
                (kategori_filtre,)
            ).fetchall()
        return conn.execute("SELECT * FROM harcamalar ORDER BY tarih DESC").fetchall()

def kategori_toplamlari():
    with baglanti() as conn:
        return conn.execute(
            "SELECT kategori, SUM(miktar) FROM harcamalar GROUP BY kategori"
        ).fetchall()

def harcama_sil(harcama_id):
    with baglanti() as conn:
        conn.execute("DELETE FROM harcamalar WHERE id = ?", (harcama_id,))
