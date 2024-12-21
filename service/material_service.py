from data.models import Material, Supplier
from data.database import SessionLocal
import pandas as pd
import logging
import re


def parse_numeric(value):
    match = re.search(r'[\d,]+(?:\.\d+)?', str(value))
    if match:
        return float(
            match.group(0).replace(',', '.'))
    return None


class MaterialService:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()])


    @staticmethod
    def add_material(name, type, quantity_per_pack, unit, stock_quantity, min_quantity, description, cost):
        session = SessionLocal()
        material = Material(
            name=name, type=type, quantity_per_pack=quantity_per_pack,
            unit=unit, stock_quantity=stock_quantity, min_quantity=min_quantity,
            description=description, cost=cost
        )
        session.add(material)
        session.commit()
        session.close()
        return material

    # @staticmethod
    # def get_materials():
    #     session = SessionLocal()
    #     materials = session.query(Material).all()
    #     session.close()
    #     return materials


    @staticmethod
    def get_materials(page, items_per_page, search_text, sort_name, sort_quantity, sort_cost, filter_type):
        session = SessionLocal()
        query = session.query(Material)

        if filter_type and filter_type != "Все типы":
            query = query.filter(Material.type == filter_type)

        if search_text:
            query = query.filter(
                Material.name.ilike(f"%{search_text}%") | Material.description.ilike(f"%{search_text}%"))

        # Применение сортировки по наименованию
        if sort_name != "none":
            if sort_name == "name_asc":
                query = query.order_by(Material.name.asc())
            elif sort_name == "name_desc":
                query = query.order_by(Material.name.desc())

        # Применение сортировки по количеству
        if sort_quantity != "none":
            if sort_quantity == "stock_asc":
                query = query.order_by(Material.stock_quantity.asc())
            elif sort_quantity == "stock_desc":
                query = query.order_by(Material.stock_quantity.desc())

        # Применение сортировки по стоимости
        if sort_cost != "none":
            if sort_cost == "cost_asc":
                query = query.order_by(Material.cost.asc())
            elif sort_cost == "cost_desc":
                query = query.order_by(Material.cost.desc())

        offset = (page - 1) * items_per_page
        materials = query.offset(offset).limit(items_per_page).all()


        count_query = session.query(Material)
        if filter_type and filter_type != "Все типы":
            count_query = count_query.filter(Material.type == filter_type)
        if search_text:
            count_query = count_query.filter(
                Material.name.ilike(f"%{search_text}%") | Material.description.ilike(f"%{search_text}%"))
        total_items = count_query.count()
        session.close()
        return materials, total_items

    @staticmethod
    def get_unique_material_types():
        session = SessionLocal()
        unique_types = session.query(Material.type).distinct().all()
        session.close()
        return [t[0] for t in unique_types]


    @staticmethod
    def import_from_csv(file_path):
        try:
            session = SessionLocal()
            materials_df = pd.read_csv(file_path)

            materials_df = pd.read_csv(file_path, encoding='utf-8',sep=';')  # Попробуйте 'cp1251', если нужно
            materials_df.columns = materials_df.columns.str.strip()
            print("Найденные столбцы:", materials_df.columns)

            # Проверка наличия всех нужных столбцов
            required_columns = [
                'Наименование материала', 'Тип материала', 'Изображение',
                'Единица измерения', 'Количество на складе', 'Минимальное количество',
                'Цена'
            ]

            missing_columns = [col for col in required_columns if col not in materials_df.columns]

            if missing_columns:
                raise ValueError(f"Отсутствуют следующие столбцы в CSV файле: {', '.join(missing_columns)}")

            for _, row in materials_df.iterrows():
                try:
                    stock_quantity = parse_numeric(row['Количество на складе'])
                    min_quantity = parse_numeric(row['Минимальное количество'])
                    cost = parse_numeric(row['Цена'])

                    material = Material(
                        name=row['Наименование материала'],
                        type=row['Тип материала'],
                        quantity_per_pack=row['Изображение'],
                        unit=row['Единица измерения'],
                        stock_quantity=stock_quantity,
                        min_quantity=min_quantity,
                        cost=cost
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
    def get_material_by_id(material_id):

        pass

    @staticmethod
    def create_material(name, material_type, stock_quantity, unit, pack_quantity, min_quantity, cost, image, description, suppliers):
        session = SessionLocal()

        if MaterialService.check_material_used_in_production(name):
            logging.error(f"Material with name {name} is used in production, cannot be created.")
            session.close()
            return None

        new_material = Material(
            name=name,
            type=material_type,
            stock_quantity=stock_quantity,
            unit=unit,
            quantity_per_pack=pack_quantity,
            min_quantity=min_quantity,
            cost=cost,
            image=image,
            description=description
        )

        session.add(new_material)
        session.commit()

        for supplier_name in suppliers:
            supplier = session.query(Supplier).filter(Supplier.name.ilike(f"%{supplier_name}%")).first()
            if not supplier:
                supplier = Supplier(name=supplier_name)
                session.add(supplier)
            new_material.suppliers.append(supplier)

        session.commit()
        session.close()
        return new_material

    @staticmethod
    def update_material(material_id, name, material_type, stock_quantity, unit, pack_quantity, min_quantity, cost, image, description, suppliers):
        session = SessionLocal()
        material = session.query(Material).filter(Material.id == material_id).first()

        if not material:
            logging.error(f"Material with id {material_id} not found.")
            session.close()
            return None

        if MaterialService.check_material_used_in_production(material_id):
            logging.error(f"Material with id {material_id} is used in production, cannot be updated.")
            session.close()
            return None

        material.name = name
        material.type = material_type
        material.stock_quantity = stock_quantity
        material.unit = unit
        material.quantity_per_pack = pack_quantity
        material.min_quantity = min_quantity
        material.cost = cost
        material.image = image
        material.description = description

        # Обновление поставщиков
        existing_suppliers = {supplier.name: supplier for supplier in material.suppliers}
        new_suppliers = set(suppliers)

        # Удаление отсутствующих поставщиков
        for supplier_name in list(existing_suppliers.keys()):
            if supplier_name not in new_suppliers:
                session.delete(existing_suppliers[supplier_name])
                material.suppliers = [s for s in material.suppliers if s.name != supplier_name]

        # Добавление новых поставщиков
        for supplier_name in new_suppliers:
            if supplier_name not in existing_suppliers:
                supplier = session.query(Supplier).filter(Supplier.name.ilike(f"%{supplier_name}%")).first()
                if not supplier:
                    supplier = Supplier(name=supplier_name)
                    session.add(supplier)
                material.suppliers.append(supplier)

        session.commit()
        session.close()
        return material

    @staticmethod
    def check_material_used_in_production(material_id):

        pass

    @staticmethod
    def get_suppliers():

        return []