from data.database import init_db
from gui.material_page import MaterialWindow
from PyQt5.QtWidgets import QApplication
import sys

from service.supplier_service import SupplierService

def import_suppliers_and_materials(file_path):
    SupplierService.import_suppliers_and_materials(file_path)

if __name__ == "__main__":
    file_path = 'path_to_your_file.xlsx'  # Укажите путь к вашему xlsx-файлу с данными о поставщиках и материалах
    import_suppliers_and_materials(file_path)