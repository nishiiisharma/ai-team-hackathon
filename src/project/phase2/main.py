from __future__ import annotations

import argparse
import json
import os

from src.project.config.settings import get_settings
from src.project.phase2.database import SeedConfig, create_schema, get_connection, seed_data
from src.project.phase2.inventory_assistant import RestaurantInventoryAssistant


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 2: Restaurant Inventory Planning Assistant"
    )
    parser.add_argument(
        "--db-url",
        default=os.getenv("PHASE2_DATABASE_URL", ""),
        help="PostgreSQL connection URL",
    )
    parser.add_argument("--menu-path", required=True, help="Menu file path (pdf/txt)")
    parser.add_argument("--user-id", type=int, default=1)
    parser.add_argument(
        "--prepare-db",
        action="store_true",
        help="Create schema and seed required dummy data before running",
    )
    parser.add_argument("--users", type=int, default=10)
    parser.add_argument("--products", type=int, default=50000)
    parser.add_argument("--orders-per-user", type=int, default=2000)
    args = parser.parse_args()
    if not args.db_url:
        raise ValueError(
            "Phase 2 requires PostgreSQL. Set PHASE2_DATABASE_URL or pass --db-url."
        )

    conn = get_connection(args.db_url)
    try:
        if args.prepare_db:
            create_schema(conn)
            seed_data(
                conn,
                SeedConfig(
                    users_count=args.users,
                    products_count=args.products,
                    orders_per_user=args.orders_per_user,
                ),
            )

        settings = get_settings()
        assistant = RestaurantInventoryAssistant(settings=settings, conn=conn)
        result = assistant.run(menu_path=args.menu_path, user_id=args.user_id)
        print(json.dumps(result, ensure_ascii=True, indent=2))
    finally:
        conn.close()


if __name__ == "__main__":
    main()

