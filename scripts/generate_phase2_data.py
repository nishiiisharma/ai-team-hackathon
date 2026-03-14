from __future__ import annotations

import argparse
import json
import os
import time

from src.project.phase2.database import SeedConfig, create_schema, get_connection, seed_data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Phase 2 dummy dataset (users/products/orders/order_details)"
    )
    parser.add_argument(
        "--db-url",
        default=os.getenv("PHASE2_DATABASE_URL", ""),
        help="PostgreSQL connection URL",
    )
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--products", type=int, default=50000)
    parser.add_argument("--orders-per-user", type=int, default=2000)
    args = parser.parse_args()
    if not args.db_url:
        raise ValueError(
            "Phase 2 requires PostgreSQL. Set PHASE2_DATABASE_URL or pass --db-url."
        )

    start = time.perf_counter()
    conn = get_connection(args.db_url)
    try:
        create_schema(conn)
        summary = seed_data(
            conn,
            SeedConfig(
                users_count=args.users,
                products_count=args.products,
                orders_per_user=args.orders_per_user,
            ),
        )
    finally:
        conn.close()
    elapsed = round(time.perf_counter() - start, 2)
    print(json.dumps({"summary": summary, "elapsed_seconds": elapsed}, indent=2))


if __name__ == "__main__":
    main()

