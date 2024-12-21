import sys

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QTableWidget, \
    QTableWidgetItem, QComboBox, QLineEdit, QHBoxLayout, QSpinBox, QTableWidgetItem, QLabel, QDialog
from PyQt5.QtCore import Qt

from gui.material_form import MaterialForm
from service.material_service import MaterialService

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление материалами")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()

        # Поиск
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Поиск по наименованию и описанию...")
        self.search_box.textChanged.connect(self.load_materials)
        self.layout.addWidget(self.search_box)

        # Выпадающий список для сортировки
        self.sort_combo = QComboBox()

        # Сортировка по наименованию
        self.sort_name_combo = QComboBox()
        self.sort_name_combo.addItem("Без сортировки (наименование)")
        self.sort_name_combo.addItem("Сортировка по наименованию (по возрастанию)")
        self.sort_name_combo.addItem("Сортировка по наименованию (по убыванию)")
        self.sort_name_combo.currentIndexChanged.connect(self.load_materials)
        self.layout.addWidget(self.sort_name_combo)

        # Сортировка по количеству
        self.sort_quantity_combo = QComboBox()
        self.sort_quantity_combo.addItem("Без сортировки (количество)")
        self.sort_quantity_combo.addItem("Сортировка по количеству (по возрастанию)")
        self.sort_quantity_combo.addItem("Сортировка по количеству (по убыванию)")
        self.sort_quantity_combo.currentIndexChanged.connect(self.load_materials)
        self.layout.addWidget(self.sort_quantity_combo)

        # Сортировка по стоимости
        self.sort_cost_combo = QComboBox()
        self.sort_cost_combo.addItem("Без сортировки (стоимость)")
        self.sort_cost_combo.addItem("Сортировка по стоимости (по возрастанию)")
        self.sort_cost_combo.addItem("Сортировка по стоимости (по убыванию)")
        self.sort_cost_combo.currentIndexChanged.connect(self.load_materials)
        self.layout.addWidget(self.sort_cost_combo)

        unique_types = MaterialService.get_unique_material_types()

        # Выпадающий список для фильтрации
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все типы")
        for material_type in unique_types:
            self.filter_combo.addItem(material_type)
        self.filter_combo.currentIndexChanged.connect(self.load_materials)
        self.layout.addWidget(self.filter_combo)

        # Кнопка импорта CSV
        self.import_button = QPushButton("Импорт материалов из CSV")
        self.import_button.clicked.connect(self.import_csv)
        self.layout.addWidget(self.import_button)

        # Таблица для отображения материалов
        self.table = QTableWidget()
        self.layout.addWidget(self.table)

        # Панель навигации для страниц
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

        self.add_material_button = QPushButton("Добавить материал")
        self.add_material_button.clicked.connect(self.show_material_form)
        self.table.itemDoubleClicked.connect(self.show_material_form)
        self.layout.addWidget(self.add_material_button)

        # Основной виджет
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.current_page = 1
        self.items_per_page = 15
        self.total_items = 0

        self.load_materials()


    def show_material_form(self, item=None):
        if item:
            material_id = int(self.table.item(item.row(), 0).text())
            material = MaterialService.get_material_by_id(material_id)
            form = MaterialForm(material)
        else:
            form = MaterialForm()

        if form.exec_() == QDialog.Accepted:
            self.load_materials()

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите CSV файл", "", "CSV Files (*.csv)")
        if file_path:
            MaterialService.import_from_csv(file_path)
            self.load_materials()

    def load_materials(self):
        # Получаем материалы из сервиса
        search_text = self.search_box.text()

        # Получаем выбранное направление сортировки для каждой категории
        sort_name_index = self.sort_name_combo.currentIndex()
        sort_quantity_index = self.sort_quantity_combo.currentIndex()
        sort_cost_index = self.sort_cost_combo.currentIndex()

        # Преобразуем индексы сортировки в строки
        sort_name = "none" if sort_name_index == 0 else ("name_asc" if sort_name_index == 1 else "name_desc")
        sort_quantity = "none" if sort_quantity_index == 0 else (
            "stock_asc" if sort_quantity_index == 1 else "stock_desc")
        sort_cost = "none" if sort_cost_index == 0 else ("cost_asc" if sort_cost_index == 1 else "cost_desc")

        # Применяем фильтры и сортировки
        filter_type = self.filter_combo.currentText()


        materials, self.total_items = MaterialService.get_materials(
            page=self.current_page,
            items_per_page=self.items_per_page,
            search_text=search_text,
            sort_name=sort_name,
            sort_quantity=sort_quantity,
            sort_cost=sort_cost,
            filter_type=filter_type
        )

        self.table.setRowCount(len(materials))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Название", "Тип", "Количество", "Минимальное количество", "Стоимость"])

        for row_idx, material in enumerate(materials):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(material.id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(material.name))
            self.table.setItem(row_idx, 2, QTableWidgetItem(material.type))
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(material.stock_quantity)))
            self.table.setItem(row_idx, 4, QTableWidgetItem(str(material.min_quantity)))
            self.table.setItem(row_idx, 5, QTableWidgetItem(str(material.cost)))

            # Логика подсветки строк в зависимости от условий
            stock_quantity = material.stock_quantity
            min_quantity = material.min_quantity

            if stock_quantity < min_quantity:

                for col in range(6):
                    self.table.item(row_idx, col).setBackground(QColor('#f19292'))
            elif stock_quantity >= 3 * min_quantity:
                for col in range(6):
                    self.table.item(row_idx, col).setBackground(QColor('#ffba01'))
        self.table.setColumnHidden(0, True)



        # Обновление текста страницы
        self.page_label.setText(f"Страница {self.current_page} из {self.total_items // self.items_per_page + 1}")
        self.count_label.setText(f"Всего найдено: {self.total_items}")

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_materials()

    def next_page(self):
        if self.current_page * self.items_per_page < self.total_items:
            self.current_page += 1
            self.load_materials()