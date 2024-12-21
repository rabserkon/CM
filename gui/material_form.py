from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox, QPushButton, QFileDialog, QLabel, \
    QMessageBox, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from service.material_service import MaterialService

class MaterialForm(QDialog):
    def __init__(self, material=None):
        super().__init__()
        self.material = material
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Добавление материала" if not self.material else "Редактирование материала")

        layout = QFormLayout()

        # Fields
        self.name_input = QLineEdit(self.material.name if self.material else "")
        self.type_input = QComboBox()
        self.type_input.addItem("Выберите тип")
        unique_types = MaterialService.get_unique_material_types()
        self.type_input.addItems(unique_types)
        self.type_input.setCurrentText(self.material.type if self.material else "")

        self.stock_quantity_input = QSpinBox()
        self.stock_quantity_input.setRange(0, 1000000)
        self.stock_quantity_input.setValue(self.material.stock_quantity if self.material else 0)

        self.unit_input = QLineEdit(self.material.unit if self.material else "")
        self.pack_quantity_input = QSpinBox()
        self.pack_quantity_input.setRange(1, 1000000)
        self.pack_quantity_input.setValue(self.material.pack_quantity if self.material else 1)

        self.min_quantity_input = QSpinBox()
        self.min_quantity_input.setRange(0, 1000000)
        self.min_quantity_input.setValue(self.material.min_quantity if self.material else 0)

        self.cost_input = QLineEdit(str(self.material.cost) if self.material else "")
        self.cost_input.setValidator(QDoubleValidator(0, 1000000, 2))

        self.image_input = QLineEdit(self.material.image if self.material else "")
        self.browse_image_button = QPushButton("Выбрать изображение")
        self.browse_image_button.clicked.connect(self.browse_image)

        self.description_input = QLineEdit(self.material.description if self.material else "")

        # List of suppliers
        self.suppliers_input = QComboBox()
        self.suppliers_input.addItem("Выберите поставщика")
        suppliers = MaterialService.get_suppliers()
        self.suppliers_input.addItems(suppliers)
        self.suppliers_input.setEditable(True)

        # Buttons
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_material)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)

        layout.addRow("Наименование:", self.name_input)
        layout.addRow("Тип материала:", self.type_input)
        layout.addRow("Количество на складе:", self.stock_quantity_input)
        layout.addRow("Единица измерения:", self.unit_input)
        layout.addRow("Количество в упаковке:", self.pack_quantity_input)
        layout.addRow("Минимальное количество:", self.min_quantity_input)
        layout.addRow("Стоимость за единицу:", self.cost_input)
        layout.addRow("Описание:", self.description_input)
        layout.addRow("Поставщики:", self.suppliers_input)
        layout.addRow(self.save_button, self.cancel_button)

        self.setLayout(layout)

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.image_input.setText(file_path)

    def save_material(self):
        name = self.name_input.text().strip()
        material_type = self.type_input.currentText().strip()
        stock_quantity = self.stock_quantity_input.value()
        unit = self.unit_input.text().strip()
        pack_quantity = self.pack_quantity_input.value()
        min_quantity = self.min_quantity_input.value()
        cost = float(self.cost_input.text().strip())
        image = self.image_input.text().strip()
        description = self.description_input.text().strip()
        suppliers = self.suppliers_input.currentText().strip()

        if not name or not material_type or not unit:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля.")
            return

        if cost < 0:
            QMessageBox.warning(self, "Ошибка", "Стоимость не может быть отрицательной.")
            return

        if min_quantity < 0:
            QMessageBox.warning(self, "Ошибка", "Минимальное количество не может быть отрицательным.")
            return

        if not MaterialService.check_material_used_in_production(self.material.id if self.material else None):
            QMessageBox.warning(self, "Ошибка", "Удаление материала запрещено, так как он используется в производстве.")
            return

        if self.material:
            MaterialService.update_material(
                self.material.id,
                name,
                material_type,
                stock_quantity,
                unit,
                pack_quantity,
                min_quantity,
                cost,
                image,
                description,
                suppliers
            )
        else:
            MaterialService.create_material(
                name,
                material_type,
                stock_quantity,
                unit,
                pack_quantity,
                min_quantity,
                cost,
                image,
                description,
                suppliers
            )

        self.accept()