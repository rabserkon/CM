from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

material_supplier = Table(
    'material_supplier',
    Base.metadata,
    Column('material_id', Integer, ForeignKey('materials.id')),
    Column('supplier_id', Integer, ForeignKey('suppliers.id'))
)

# Таблица "Материалы"
class Material(Base):
    __tablename__ = 'materials'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    quantity_per_pack = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    stock_quantity = Column(Float, nullable=False)
    min_quantity = Column(Float, nullable=False)
    description = Column(String)
    cost = Column(Float, nullable=False)
    suppliers = relationship("Supplier", secondary=material_supplier, back_populates="materials")

# Таблица "Поставщики"
class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    inn = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)
    rate = Column(Integer, nullable=False)
    start_date=Column(DateTime, nullable=False, default=datetime.utcnow)
    materials = relationship("Material", secondary=material_supplier, back_populates="suppliers")

# Таблица "История изменений материалов"
class MaterialChange(Base):
    __tablename__ = 'material_changes'
    id = Column(Integer, primary_key=True)
    material_id = Column(Integer, ForeignKey('materials.id'))
    change_date = Column(String, nullable=False)  # Дату можно хранить в формате ISO
    old_value = Column(Float)
    new_value = Column(Float)
    comment = Column(String)
