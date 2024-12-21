CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,
    quantity_per_pack VARCHAR NOT NULL,
    unit VARCHAR NOT NULL,
    stock_quantity FLOAT NOT NULL,
    min_quantity FLOAT NOT NULL,
    description VARCHAR,
    cost FLOAT NOT NULL
);

CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    inn VARCHAR NOT NULL UNIQUE,
    type VARCHAR NOT NULL,
    rate INTEGER NOT NULL,
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE material_supplier (
    material_id INTEGER REFERENCES materials(id),
    supplier_id INTEGER REFERENCES suppliers(id),
    PRIMARY KEY (material_id, supplier_id)
);

CREATE TABLE material_changes (
    id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES materials(id),
    change_date TIMESTAMP NOT NULL,
    old_value FLOAT,
    new_value FLOAT,
    comment VARCHAR
);