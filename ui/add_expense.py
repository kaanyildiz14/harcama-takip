from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QDialogButtonBox, QMessageBox
)
from PyQt5.QtCore import QDate
import database
from amounts import tutar_dogrula

KATEGORILER = ["Yemek", "Ulasim", "Alisveris", "Fatura", "Eglence", "Diger"]

class HarcamaEkleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Harcama Ekle")
        self.setMinimumWidth(300)
        self._arayuz_olustur()

    def _arayuz_olustur(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.baslik_input = QLineEdit()
        self.miktar_input = QLineEdit()
        self.kategori_input = QComboBox()
        self.kategori_input.addItems(KATEGORILER)
        self.tarih_input = QDateEdit(QDate.currentDate())
        self.tarih_input.setCalendarPopup(True)

        form.addRow("Başlık:", self.baslik_input)
        form.addRow("Miktar (TL):", self.miktar_input)
        form.addRow("Kategori:", self.kategori_input)
        form.addRow("Tarih:", self.tarih_input)
        layout.addLayout(form)

        butonlar = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        butonlar.accepted.connect(self.kaydet)
        butonlar.rejected.connect(self.reject)
        layout.addWidget(butonlar)

    def kaydet(self):
        baslik = self.baslik_input.text().strip()
        miktar_str = self.miktar_input.text().strip()

        if not baslik:
            QMessageBox.warning(self, "Hata", "Başlık boş olamaz.")
            return
        try:
            miktar = tutar_dogrula(miktar_str)
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir miktar girin.")
            return

        kategori = self.kategori_input.currentText()
        tarih = self.tarih_input.date().toString("yyyy-MM-dd")
        database.harcama_ekle(baslik, miktar, kategori, tarih)
        self.accept()
