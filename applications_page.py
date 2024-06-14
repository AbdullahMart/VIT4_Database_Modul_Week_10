import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTableWidget, QLabel, QTableWidgetItem, QComboBox
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
import sys
import os
import psycopg2
from collections import Counter, defaultdict

# Veritabanı bağlantı bilgileri
database_name = "CRM"
user = "postgres"
password = "Kirmizi"
host = "localhost"

# PostgreSQL bağlantısı
def connect_to_db():
    conn = psycopg2.connect(
        dbname=database_name,
        user=user,
        password=password,
        host=host
    )
    return conn

# Veritabanından verileri çeken fonksiyon
def fetch_data(query, params=None):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchall()
    headers = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return headers, data

class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Pencere başlığı ve boyutu
        self.setWindowTitle("Applications")
        self.setGeometry(100, 100, 1220, 735)

        # Merkezi widget ve ana layout
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.mainLayout = QVBoxLayout(self.centralWidget)

        # Arama çubuğu ve butonu yatay layout
        self.searchLayout = QHBoxLayout()

        # PNG için QLabel
        self.pngLabel = QLabel()
        self.pngLabel.setPixmap(QPixmap("images/werhere_image.png"))
        self.pngLabel.setFixedSize(250, 40)  # PNG boyutunu ayarlayın
        self.pngLabel.setScaledContents(True)

        # QLineEdit ve Search butonu
        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setMaximumWidth(540)  # Arama çubuğunun maksimum genişliğini ayarlayın
        self.searchLineEdit.setPlaceholderText("Name/Surname")  # Placeholder text
        self.searchLineEdit.returnPressed.connect(self.search_applications)  # Enter tuşuna basıldığında arama yap

        self.searchButton = QPushButton("Search")
        self.searchButton.setStyleSheet("""
        QPushButton {
            background-color: #696969; /* Koyu gri */
            border-radius: 10px;
            padding: 10px;
            color: white; /* Beyaz metin rengi */
        }
        QPushButton:hover {
            background-color: #40E0D0; /* Turkuaz */
        }
        """)
        self.searchButton.clicked.connect(self.search_applications)  # Butona tıklandığında arama yap

        # PNG ve arama elemanlarını layout'a ekle
        self.searchLayout.addWidget(self.pngLabel)
        self.searchLayout.addWidget(self.searchLineEdit)
        self.searchLayout.addWidget(self.searchButton)
        self.mainLayout.addLayout(self.searchLayout)

        # Diğer butonlar için layout
        self.buttonLayout = QHBoxLayout()

        self.leftButtonLayout = QVBoxLayout()
        self.middleButtonLayout = QVBoxLayout()
        self.rightButtonLayout = QVBoxLayout()

        # Buton stil sayfası (hover rengi turkuaz yapar, köşeleri yuvarlar)
        button_style = """
        QPushButton {
            background-color: #696969; /* Koyu gri */
            border-radius: 10px;
            padding: 10px;
            color: white; /* Beyaz metin rengi */
        }
        QPushButton:hover {
            background-color: #40E0D0; /* Turkuaz */
        }
        """

        # Buton isimleri ve sıralaması
        button_texts = [
            "All Applications", "Meetings with Assigned Mentor", "Filtered Applications",
            "Multiple Registrations", "Meetings with Unassigned Mentor", "Preferences",
            "Different Registrations", "Former VIT Check", "EXIT"
        ]

        # Butonları oluştur ve uygun layout'a ekle
        for i, text in enumerate(button_texts):
            button = QPushButton(text)
            button.setStyleSheet(button_style)
            button.setMinimumHeight(40)  # Minimum buton yüksekliği
            button.clicked.connect(self.handleButtonClick)  # Tıklama olayını bağla

            if i < 3:
                self.leftButtonLayout.addWidget(button)
            elif i < 6:
                self.middleButtonLayout.addWidget(button)
            else:
                self.rightButtonLayout.addWidget(button)

        self.buttonLayout.addLayout(self.leftButtonLayout)
        self.buttonLayout.addLayout(self.middleButtonLayout)
        self.buttonLayout.addLayout(self.rightButtonLayout)

        self.mainLayout.addLayout(self.buttonLayout)

        # ComboBox'u butonların altına ekle
        # self.comboBox = QComboBox()
        # self.comboBox.addItems([
        #     "Language level B1 and above [Ingilizce]",
        #     "Language level A2 and below [Ingilizce]",
        #     "Language level B1 and above [Nederlands]",
        #     "Language level A2 and below [Nederlands]",
        #     "At least one of English and Nederlands is at B1 level"
        # ])
        # self.comboBox.currentIndexChanged.connect(self.handleComboBoxChange)
        # self.mainLayout.addWidget(self.comboBox)

        # QTableWidget
        self.tableWidget = QTableWidget()
        self.tableWidget.setFont(QFont("Arial", 11))
        self.tableWidget.setSortingEnabled(True)  # Sıralama etkinleştirildi
        self.tableWidget.setSizeAdjustPolicy(QTableWidget.SizeAdjustPolicy.AdjustToContents)
        self.mainLayout.addWidget(self.tableWidget)

    def handleButtonClick(self):
        sender = self.sender()
        if sender.text() == "All Applications":
            self.load_all_applications()
        elif sender.text() == "Multiple Registrations":
            self.find_multiple_registrations()
        elif sender.text() == "Meetings with Assigned Mentor":
            self.find_assigned_mentor_meetings()
        elif sender.text() == "Meetings with Unassigned Mentor":
            self.find_unassigned_mentor_meetings()
        elif sender.text() == "Filtered Applications":
            self.find_filtered_applications()
        elif sender.text() == "Preferences":
            self.open_preferences()
        elif sender.text() == "Different Registrations":
            self.find_different_registrations()
        elif sender.text() == "Former VIT Check":
            self.former_vit_check()
        elif sender.text() == "EXIT":
            self.exit_application()

    # def handleComboBoxChange(self):
    #     index = self.comboBox.currentIndex()
    #     if index == 0:
    #         self.find_language_level("english_level", ["B1", "B2 ve üzeri", "C1", "C2"])
    #     elif index == 1:
    #         self.find_language_level("english_level", ["A0", "A1", "A2"])
    #     elif index == 2:
    #         self.find_language_level("dutch_level", ["B1", "B2 ve üzeri", "C1", "C2"])
    #     elif index == 3:
    #         self.find_language_level("dutch_level", ["A0", "A1", "A2"])
    #     elif index == 4:
    #         self.find_combined_language_level()

    # def find_language_level(self, column_name, levels):
    #     try:
    #         query = f"SELECT * FROM applications WHERE {Yabancı dil Seviyeniz [İngilizce]} = ANY(%s)"
    #         headers, data = fetch_data(query, (levels,))
    #         self.load_data(headers, data)
    #     except Exception as e:
    #         print(f"Error finding language level {column_name}: {e}")

    # def find_combined_language_level(self):
    #     try:
    #         query = """
    #             SELECT * FROM applications
    #             WHERE english_level = ANY(%s) OR dutch_level = ANY(%s)
    #         """
    #         levels = ["B1", "B2 ve üzeri", "C1", "C2"]
    #         headers, data = fetch_data(query, (levels, levels))
    #         self.load_data(headers, data)
    #     except Exception as e:
    #         print(f"Error finding combined language levels: {e}")

    def load_all_applications(self):
        try:
            query = "SELECT * FROM applications"
            headers, data = fetch_data(query)
            print("Data retrieved from PostgreSQL:", data)  # Hata ayıklama için veriyi yazdırın
            self.load_data(headers, data)
        except Exception as e:
            print(f"Error loading data: {e}")

    def find_multiple_registrations(self):
        try:
            query = """
                SELECT *, COUNT(*) as count
                FROM applications
                GROUP BY name, surname
                HAVING COUNT(*) > 1
            """
            headers, data = fetch_data(query)
            self.load_data(headers, data)
        except Exception as e:
            print(f"Error finding multiple registrations: {e}")

    def find_assigned_mentor_meetings(self):
        try:
            query = "SELECT * FROM applications WHERE mentor_meeting = 'OK'"
            headers, data = fetch_data(query)
            self.load_data(headers, data)
        except Exception as e:
            print(f"Error finding assigned mentor meetings: {e}")

    def find_unassigned_mentor_meetings(self):
        try:
            query = "SELECT * FROM applications WHERE mentor_meeting != 'OK'"
            headers, data = fetch_data(query)
            self.load_data(headers, data)
        except Exception as e:
            print(f"Error finding unassigned mentor meetings: {e}")

    def find_filtered_applications(self):
        try:
            query = """
                SELECT DISTINCT ON (name, surname) *
                FROM applications
            """
            headers, data = fetch_data(query)
            self.load_data(headers, data)
        except Exception as e:
            print(f"Error finding filtered applications: {e}")

    def load_data(self, headers, data):
        if not data:
            print("No data found.")
            return

        self.tableWidget.setRowCount(len(data))
        self.tableWidget.setColumnCount(len(headers))

        # Sütun başlıklarını ayarla
        self.tableWidget.setHorizontalHeaderLabels(headers)

        # Verileri tabloya ekle
        for row_idx, row_data in enumerate(data):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.tableWidget.setItem(row_idx, col_idx, item)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def search_applications(self):
        search_text = self.searchLineEdit.text().strip().lower()
        if not search_text:
            return
        
        try:
            query = """
                SELECT * FROM applications
                WHERE LOWER(Adiniz_soyadiniz) LIKE %s OR LOWER(Adiniz_Soyadiniz) LIKE %s
            """
            headers, data = fetch_data(query, ('%' + search_text + '%', '%' + search_text + '%'))
            self.load_data(headers, data)
        except Exception as e:
            print(f"Error searching data: {e}")

    def former_vit_check(self):
        try:
            query = """
                SELECT * FROM applications a
                WHERE EXISTS (
                    SELECT 1 FROM vit1 v1 WHERE v1.name = a.name AND v1.surname = a.surname
                ) OR EXISTS (
                    SELECT 1 FROM vit2 v2 WHERE v2.name = a.name AND v2.surname = a.surname
                )
            """
            headers, data = fetch_data(query)
            self.load_data(headers, data)
        except Exception as e:
            print(f"Error finding former VIT check: {e}")

    def find_different_registrations(self):
        try:
            query = """
                SELECT * FROM applications a
                WHERE NOT EXISTS (
                    SELECT 1 FROM vit1 v1 WHERE v1.name = a.name AND v1.surname = a.surname
                ) AND NOT EXISTS (
                    SELECT 1 FROM vit2 v2 WHERE v2.name = a.name AND v2.surname = a.surname
                )
            """
            headers, data = fetch_data(query)
            self.load_data(headers, data)
        except Exception as e:
            print(f"Error finding different registrations: {e}")

    def open_preferences(self):
        self.close()
        try:
            subprocess.Popen(["python", os.path.join(os.path.dirname(__file__), "preference_admin_menu.py")])
        except FileNotFoundError:
            subprocess.Popen(["python3", os.path.join(os.path.dirname(__file__), "preference_admin_menu.py")])

    def exit_application(self):
        self.close()
        try:
            subprocess.Popen(["python", os.path.join(os.path.dirname(__file__), "login_window.py")])
        except FileNotFoundError:
            subprocess.Popen(["python3", os.path.join(os.path.dirname(__file__), "login_window.py")])

if __name__ == "__main__":
    app = QApplication([])
    window = ApplicationWindow()
    window.show()
    app.exec()

