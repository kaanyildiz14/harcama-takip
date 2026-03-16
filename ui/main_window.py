import csv
import math
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem,
    QLabel, QMessageBox, QHeaderView, QComboBox,
    QTabWidget, QFileDialog
)
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QPen
import database
from api import doviz_kuru_getir
from ui.add_expense import HarcamaEkleDialog

KATEGORI_RENK = {
    "Yemek":    "#FF6B6B",
    "Ulasim":   "#4ECDC4",
    "Alisveris":"#45B7D1",
    "Fatura":   "#FFA07A",
    "Eglence":  "#98D8C8",
    "Diger":    "#C3A6FF",
}

STIL = """
QMainWindow { background-color: #1e1e2e; }
QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: Segoe UI; font-size: 13px; }
QTabWidget::pane { border: 1px solid #313244; border-radius: 8px; }
QTabBar::tab { background: #313244; color: #cdd6f4; padding: 8px 20px; border-radius: 6px; margin-right: 4px; }
QTabBar::tab:selected { background: #89b4fa; color: #1e1e2e; font-weight: bold; }
QPushButton { background-color: #89b4fa; color: #1e1e2e; border: none; border-radius: 8px; padding: 8px 18px; font-weight: bold; }
QPushButton:hover { background-color: #b4befe; }
QPushButton#silBtn { background-color: #f38ba8; }
QPushButton#silBtn:hover { background-color: #eba0ac; }
QPushButton#csvBtn { background-color: #a6e3a1; color: #1e1e2e; }
QPushButton#csvBtn:hover { background-color: #94e2d5; }
QTableWidget { background-color: #181825; border: 1px solid #313244; border-radius: 8px; gridline-color: #313244; }
QTableWidget::item { padding: 6px; }
QTableWidget::item:selected { background-color: #313244; color: #cdd6f4; }
QTableWidget::item:alternate { background-color: #1e1e2e; }
QHeaderView::section { background-color: #313244; color: #89b4fa; padding: 8px; border: none; font-weight: bold; }
QComboBox { background-color: #313244; border: 1px solid #45475a; border-radius: 6px; padding: 6px 12px; color: #cdd6f4; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #313244; color: #cdd6f4; selection-background-color: #45475a; }
"""


class PastaGrafik(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.veriler = []
        self.setMinimumHeight(350)

    def guncelle(self):
        self.veriler = database.kategori_toplamlari()
        self.update()

    def paintEvent(self, event):
        if not self.veriler:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        toplam = sum(v[1] for v in self.veriler)
        if toplam == 0:
            return

        cx = self.width() // 2 - 60
        cy = self.height() // 2
        r = min(cx, cy) - 30
        rect = QRectF(cx - r, cy - r, r * 2, r * 2)

        baslac = 0
        for kategori, miktar in self.veriler:
            oran = miktar / toplam
            aci = oran * 360 * 16
            renk = KATEGORI_RENK.get(kategori, "#cdd6f4")
            painter.setBrush(QBrush(QColor(renk)))
            painter.setPen(QPen(QColor("#1e1e2e"), 2))
            painter.drawPie(rect, int(baslac), int(aci))
            baslac += aci

        # Lejant
        lejant_x = cx + r + 30
        lejant_y = cy - (len(self.veriler) * 25) // 2
        for i, (kategori, miktar) in enumerate(self.veriler):
            renk = KATEGORI_RENK.get(kategori, "#cdd6f4")
            oran = (miktar / toplam) * 100
            painter.setBrush(QBrush(QColor(renk)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(lejant_x, lejant_y + i * 28, 14, 14, 3, 3)
            painter.setPen(QPen(QColor("#cdd6f4")))
            painter.drawText(lejant_x + 20, lejant_y + i * 28 + 12,
                             f"{kategori}  {miktar:.0f} TL ({oran:.1f}%)")

        painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Harcama Takip")
        self.setMinimumSize(800, 580)
        self.setStyleSheet(STIL)
        database.tablo_olustur()
        self._arayuz_olustur()
        self.harcamalari_yukle()
        self.doviz_guncelle()

    def _arayuz_olustur(self):
        merkez = QWidget()
        self.setCentralWidget(merkez)
        ana_layout = QVBoxLayout(merkez)
        ana_layout.setSpacing(12)
        ana_layout.setContentsMargins(20, 20, 20, 20)

        ust_layout = QHBoxLayout()
        baslik = QLabel("Harcama Takip")
        baslik.setFont(QFont("Segoe UI", 18, QFont.Bold))
        baslik.setStyleSheet("color: #89b4fa;")
        self.doviz_label = QLabel("Doviz yukleniyor...")
        self.doviz_label.setStyleSheet("color: #a6e3a1; font-size: 12px;")
        self.doviz_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        ust_layout.addWidget(baslik)
        ust_layout.addWidget(self.doviz_label)
        ana_layout.addLayout(ust_layout)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._liste_tab(), "  Harcamalar")
        self.tabs.addTab(self._grafik_tab(), "  Grafik")
        self.tabs.currentChanged.connect(self._tab_degisti)
        ana_layout.addWidget(self.tabs)

        self.toplam_label = QLabel("Toplam: 0.00 TL")
        self.toplam_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.toplam_label.setStyleSheet("color: #a6e3a1;")
        self.toplam_label.setAlignment(Qt.AlignRight)
        ana_layout.addWidget(self.toplam_label)

    def _liste_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        ust = QHBoxLayout()
        filtre_label = QLabel("Filtre:")
        self.filtre_combo = QComboBox()
        self.filtre_combo.addItems(["Tumu", "Yemek", "Ulasim", "Alisveris", "Fatura", "Eglence", "Diger"])
        self.filtre_combo.currentTextChanged.connect(self.harcamalari_yukle)

        ekle_btn = QPushButton("+ Ekle")
        sil_btn = QPushButton("Sil")
        sil_btn.setObjectName("silBtn")
        csv_btn = QPushButton("CSV Indir")
        csv_btn.setObjectName("csvBtn")

        ekle_btn.clicked.connect(self.harcama_ekle)
        sil_btn.clicked.connect(self.harcama_sil)
        csv_btn.clicked.connect(self.csv_export)

        ust.addWidget(filtre_label)
        ust.addWidget(self.filtre_combo)
        ust.addStretch()
        ust.addWidget(ekle_btn)
        ust.addWidget(sil_btn)
        ust.addWidget(csv_btn)
        layout.addLayout(ust)

        self.tablo = QTableWidget()
        self.tablo.setColumnCount(5)
        self.tablo.setHorizontalHeaderLabels(["ID", "Baslik", "Miktar (TL)", "Kategori", "Tarih"])
        self.tablo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tablo.setSelectionBehavior(QTableWidget.SelectRows)
        self.tablo.setAlternatingRowColors(True)
        self.tablo.verticalHeader().setVisible(False)
        layout.addWidget(self.tablo)
        return widget

    def _grafik_tab(self):
        self.grafik = PastaGrafik()
        return self.grafik

    def _tab_degisti(self, index):
        if index == 1:
            self.grafik.guncelle()

    def harcamalari_yukle(self):
        filtre = self.filtre_combo.currentText()
        harcamalar = database.harcamalari_getir(filtre)
        self.tablo.setRowCount(len(harcamalar))
        toplam = 0
        for i, h in enumerate(harcamalar):
            for j, deger in enumerate(h):
                item = QTableWidgetItem(str(deger))
                item.setTextAlignment(Qt.AlignCenter)
                if j == 3:
                    renk = KATEGORI_RENK.get(str(deger), "#cdd6f4")
                    item.setForeground(QColor(renk))
                self.tablo.setItem(i, j, item)
            toplam += h[2]
        self.toplam_label.setText(f"Toplam: {toplam:.2f} TL")

    def harcama_ekle(self):
        dialog = HarcamaEkleDialog(self)
        if dialog.exec_():
            self.harcamalari_yukle()

    def harcama_sil(self):
        secili = self.tablo.currentRow()
        if secili < 0:
            QMessageBox.warning(self, "Uyari", "Lutfen bir harcama secin.")
            return
        harcama_id = int(self.tablo.item(secili, 0).text())
        cevap = QMessageBox.question(self, "Sil", "Secili harcamayi silmek istiyor musunuz?")
        if cevap == QMessageBox.Yes:
            database.harcama_sil(harcama_id)
            self.harcamalari_yukle()

    def csv_export(self):
        dosya, _ = QFileDialog.getSaveFileName(self, "CSV Kaydet", "harcamalar.csv", "CSV (*.csv)")
        if dosya:
            harcamalar = database.harcamalari_getir()
            with open(dosya, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Baslik", "Miktar (TL)", "Kategori", "Tarih"])
                writer.writerows(harcamalar)
            QMessageBox.information(self, "Basarili", "CSV dosyasi kaydedildi.")

    def doviz_guncelle(self):
        kurlar = doviz_kuru_getir()
        if kurlar["USD"]:
            self.doviz_label.setText(f"1 USD = {kurlar['USD']} TL   |   1 EUR = {kurlar['EUR']} TL")
        else:
            self.doviz_label.setText("Doviz bilgisi alinamadi")
