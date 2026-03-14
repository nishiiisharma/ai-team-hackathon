from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import psycopg


@dataclass(frozen=True)
class SeedConfig:
    users_count: int = 10
    products_count: int = 50_000
    orders_per_user: int = 2_000
    min_items_per_order: int = 5
    max_items_per_order: int = 15


INGREDIENT_POOL = [
    "tomato", "onion", "potato", "rice", "flour", "salt", "oil", "sugar", "milk",
    "butter", "paneer", "chicken", "garlic", "ginger", "chili", "coriander", "cumin",
    "turmeric", "peas", "beans", "carrot", "capsicum", "spinach", "lemon", "yogurt",
    "cheese", "cream", "lentil", "chickpea", "vinegar", "soy sauce", "mushroom",
    "corn", "egg", "basil", "oregano", "black pepper", "cabbage", "cauliflower",
    "broccoli", "mint", "coconut", "cashew", "almond", "noodles", "pasta", "bread",
]


def get_connection(database_url: str) -> Any:
    return psycopg.connect(database_url)


def create_schema(conn: Any) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                created_at TIMESTAMPTZ NOT NULL
            );

            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                unit TEXT NOT NULL,
                stock_quantity DOUBLE PRECISION NOT NULL,
                current_price DOUBLE PRECISION NOT NULL,
                season_tag TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                order_ts TIMESTAMPTZ NOT NULL,
                total_amount DOUBLE PRECISION NOT NULL
            );

            CREATE TABLE IF NOT EXISTS order_details (
                id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id),
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity DOUBLE PRECISION NOT NULL,
                unit_price DOUBLE PRECISION NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
            CREATE INDEX IF NOT EXISTS idx_orders_order_ts ON orders(order_ts);
            CREATE INDEX IF NOT EXISTS idx_order_details_order_id ON order_details(order_id);
            CREATE INDEX IF NOT EXISTS idx_order_details_product_id ON order_details(product_id);
            """
        )
    conn.commit()


def seed_data(conn: Any, config: SeedConfig) -> dict[str, int]:
    random.seed(42)
    now = datetime.utcnow()

    users = [
        (index, f"User {index}", f"user{index}@demo.local", now)
        for index in range(1, config.users_count + 1)
    ]
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO users(id, name, email, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                email = EXCLUDED.email,
                created_at = EXCLUDED.created_at
            """,
            users,
        )

    products: list[tuple[int, str, str, str, float, float, str]] = []
    for index in range(1, config.products_count + 1):
        name = INGREDIENT_POOL[index - 1] if index <= len(INGREDIENT_POOL) else f"ingredient_{index}"
        products.append(
            (
                index,
                name,
                "ingredient",
                "kg",
                round(random.uniform(10, 300), 2),
                round(random.uniform(20, 600), 2),
                random.choice(["all", "summer", "winter", "monsoon"]),
            )
        )

    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO products(id, name, category, unit, stock_quantity, current_price, season_tag)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET name = EXCLUDED.name,
                category = EXCLUDED.category,
                unit = EXCLUDED.unit,
                stock_quantity = EXCLUDED.stock_quantity,
                current_price = EXCLUDED.current_price,
                season_tag = EXCLUDED.season_tag
            """,
            products,
        )
    conn.commit()

    order_rows: list[tuple[int, int, datetime, float]] = []
    order_detail_rows: list[tuple[int, int, int, float, float]] = []
    order_id = 1
    order_detail_id = 1

    popular_product_ids = list(range(1, min(config.products_count, 300) + 1))
    for user_id in range(1, config.users_count + 1):
        for _ in range(config.orders_per_user):
            order_ts = now - timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )
            item_count = random.randint(config.min_items_per_order, config.max_items_per_order)
            selected = random.sample(popular_product_ids, k=item_count)
            total = 0.0

            for product_id in selected:
                qty = round(random.uniform(0.3, 8.0), 2)
                price = products[product_id - 1][5]
                total += qty * price
                order_detail_rows.append((order_detail_id, order_id, product_id, qty, price))
                order_detail_id += 1

            order_rows.append((order_id, user_id, order_ts, round(total, 2)))
            order_id += 1

        if len(order_rows) >= 2000:
            _flush_orders(conn, order_rows, order_detail_rows)
            order_rows.clear()
            order_detail_rows.clear()

    if order_rows:
        _flush_orders(conn, order_rows, order_detail_rows)

    return {
        "users": config.users_count,
        "products": config.products_count,
        "orders": config.users_count * config.orders_per_user,
    }


def _flush_orders(
    conn: Any,
    order_rows: list[tuple[int, int, datetime, float]],
    order_detail_rows: list[tuple[int, int, int, float, float]],
) -> None:
    with conn.cursor() as cursor:
        cursor.executemany(
            """
            INSERT INTO orders(id, user_id, order_ts, total_amount)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET user_id = EXCLUDED.user_id,
                order_ts = EXCLUDED.order_ts,
                total_amount = EXCLUDED.total_amount
            """,
            order_rows,
        )
        cursor.executemany(
            """
            INSERT INTO order_details(id, order_id, product_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET order_id = EXCLUDED.order_id,
                product_id = EXCLUDED.product_id,
                quantity = EXCLUDED.quantity,
                unit_price = EXCLUDED.unit_price
            """,
            order_detail_rows,
        )
    conn.commit()

