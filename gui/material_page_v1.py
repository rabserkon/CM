import sys

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QTableWidget, \
    QTableWidgetItem, QComboBox, QLineEdit, QHBoxLayout, QSpinBox, QTableWidgetItem, QLabel, QFrame, QScrollArea
from PyQt5.QtCore import Qt
from service.material_service import MaterialService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление материалами")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout()
        self.cards_container.setLayout(self.cards_layout)
        self.scroll_area.setWidget(self.cards_container)

        # Кнопка импорта CSV
        self.import_button = QPushButton("Импорт материалов из CSV")
        self.import_button.clicked.connect(self.import_csv)
        self.layout.addWidget(self.import_button)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(10)
        h_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(h_layout)

        box_layout = QHBoxLayout()
        box_layout.setSpacing(10)
        box_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(box_layout)

        # Поиск
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по наименованию...")
        self.search_box.setStyleSheet("""
                   QLineEdit {
                       border: 1px solid black;
                       padding: 8px;
                       font-size: 14px;
                   }
               """)
        self.search_box.textChanged.connect(self.load_materials)
        h_layout.addWidget(self.search_box)
        h_layout.setStretchFactor(self.search_box, 2)

        # Сортировка
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("Без сортировки")
        self.sort_combo.addItem("Сортировка по наименованию (по возрастанию)")
        self.sort_combo.addItem("Сортировка по наименованию (по убыванию)")
        self.sort_combo.addItem("Сортировка по количеству (по возрастанию)")
        self.sort_combo.addItem("Сортировка по количеству (по убыванию)")
        self.sort_combo.addItem("Сортировка по стоимости (по возрастанию)")
        self.sort_combo.addItem("Сортировка по стоимости (по убыванию)")
        self.sort_combo.setStyleSheet("""
                QComboBox {
                    border: 1px solid black;
                    padding: 8px;
                    font-size: 14px;
                }
            """)
        self.sort_combo.currentIndexChanged.connect(self.load_materials)
        h_layout.addWidget(self.sort_combo)
        h_layout.setStretchFactor(self.sort_combo, 1)

        # Фильтрация
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все типы")
        self.filter_combo.setStyleSheet("""
                  QComboBox {
                      border: 1px solid black;
                      padding: 8px;
                      font-size: 14px;
                  }
              """)
        self.filter_combo.currentIndexChanged.connect(self.load_materials)
        h_layout.addWidget(self.filter_combo)
        h_layout.setStretchFactor(self.filter_combo, 1)



        self.pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("Предыдущая страница")
        self.prev_button.clicked.connect(self.prev_page)
        self.pagination_layout.addWidget(self.prev_button)

        self.page_label = QLabel("Страница 1")
        self.pagination_layout.addWidget(self.page_label)

        self.count_label = QLabel("Количество элементов")
        self.pagination_layout.addWidget(self.count_label)

        self.next_button = QPushButton("Следующая страница")
        self.next_button.clicked.connect(self.next_page)
        self.pagination_layout.addWidget(self.next_button)

        self.layout.addLayout(self.pagination_layout)

        # Кнопка обновления данных
        self.refresh_button = QPushButton("Обновить список материалов")
        self.refresh_button.clicked.connect(self.load_materials)
        self.layout.addWidget(self.refresh_button)

        # Основной виджет
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.current_page = 1
        self.items_per_page = 15
        self.total_items = 0

        self.load_materials()


    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите CSV файл", "", "CSV Files (*.csv)")
        if file_path:
            MaterialService.import_from_csv(file_path)
            self.load_materials()

    def load_materials(self):
        search_text = self.search_box.text()
        sort_combo_index = self.sort_combo.currentIndex()

        if sort_combo_index == 0:
            sort_name = "none"
            sort_quantity = "none"
            sort_cost = "none"
        elif sort_combo_index == 1:
            sort_name = "name_asc"
            sort_quantity = "none"
            sort_cost = "none"
        elif sort_combo_index == 2:
            sort_name = "name_desc"
            sort_quantity = "none"
            sort_cost = "none"
        elif sort_combo_index == 3:
            sort_name = "none"
            sort_quantity = "stock_asc"
            sort_cost = "none"
        elif sort_combo_index == 4:
            sort_name = "none"
            sort_quantity = "stock_desc"
            sort_cost = "none"
        elif sort_combo_index == 5:
            sort_name = "none"
            sort_quantity = "none"
            sort_cost = "cost_asc"
        elif sort_combo_index == 6:
            sort_name = "none"
            sort_quantity = "none"
            sort_cost = "cost_desc"

        filter_type = self.filter_combo.currentIndex()

        materials, self.total_items = MaterialService.get_materials(
            page=self.current_page,
            items_per_page=self.items_per_page,
            search_text=search_text,
            sort_name=sort_name,
            sort_quantity=sort_quantity,
            sort_cost=sort_cost,
            filter_type=filter_type
        )

        # Clear the previous cards
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for material in materials:
            card_frame = self.create_card(material)
            self.cards_layout.addWidget(card_frame)

        self.page_label.setText(f"Страница {self.current_page} из {self.total_items // self.items_per_page + 1}")
        self.count_label.setText(f"Всего найдено: {self.total_items}")

    def create_card(self, material):
        card_frame = QFrame()
        card_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        card_frame.setStyleSheet("""
               QFrame {
                   border: 1px solid black;
                   margin-bottom: 10px;
                   padding: 10px;
               }
           """)

        card_layout = QVBoxLayout()

        name_label = QLabel(f"Название: {material.name}")
        card_layout.addWidget(name_label)


        name_label = QLabel(f"Поставщики: пока нет")
        card_layout.addWidget(name_label)

        min_quantity_label = QLabel(f"Минимальное количество: {material.min_quantity}")
        card_layout.addWidget(min_quantity_label)

        stock_quantity_label = QLabel(f"Остаток: {material.stock_quantity}")
        card_layout.addWidget(stock_quantity_label)

        card_frame.setLayout(card_layout)
        return card_frame


    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_materials()

    def next_page(self):
        if self.current_page * self.items_per_page < self.total_items:
            self.current_page += 1
            self.load_materials()