from data.models import Supplier, material_supplier, Material
from data.database import SessionLocal
import pandas as pd
import logging

class SupplierService:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()])

    @staticmethod
    def import_from_csv(file_path):
        try:
            session = SessionLocal()
            supplier_df = pd.read_csv(file_path)

            supplier_df = pd.read_csv(file_path, encoding='utf-8', sep=';')  # Попробуйте 'cp1251', если нужно
            supplier_df.columns = supplier_df.columns.str.strip()
            print("Найденные столбцы:", supplier_df.columns)


            required_columns = [
                'Наименование поставщика', 'Тип поставщика', 'ИНН', 'Рейтинг качества', 'Дата начала работы с поставщиком'
            ]

            missing_columns = [col for col in required_columns if col not in supplier_df.columns]

            if missing_columns:
                raise ValueError(f"Отсутствуют следующие столбцы в CSV файле: {', '.join(missing_columns)}")

            for _, row in supplier_df.iterrows():
                try:

                    material = Supplier(
                        name=row['Наименование поставщика'],
                        type=row['Тип поставщика'],
                        inn=row['ИНН'],
                        rate=['Рейтинг качества'],



                    )
                    session.add(material)
                except KeyError as e:
                    logging.error(f"Ошибка при обработке строки: отсутствует столбец '{e.args[0]}'")
                    continue

            session.commit()
            session.close()
        except Exception as e:
            logging.error(f"Произошла ошибка при импорте данных из CSV: {e}")

    @staticmethod
    def get_suppliers():
        session = SessionLocal()
        suppliers = session.query(Supplier).all()
        session.close()
        return suppliers