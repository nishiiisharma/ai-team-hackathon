# Phase 2 Practical Demonstration

## Use case

Restaurant inventory planning assistant for Zepto-style quick commerce flow.

## Implemented flow

1. User uploads menu file (PDF/text).
2. AI extracts dish names and ingredients.
3. Dish-ingredient records are stored in vector DB (Chroma) for retrieval.
4. System checks ingredient availability from dummy DB.
5. Prediction logic estimates required quantity using:
   - order frequency
   - time-of-day behavior
   - weekday/date pattern
   - seasonality
   - user-specific behavior
6. Final response returns table:
   - Ingredient
   - Available Stock
   - Predicted Required Quantity
   - Recommended Order Quantity
7. Only ingredients requiring order are included.

## Database setup

Recommended and implemented DB: **PostgreSQL**

Tables:
- `users` (>=10)
- `products` (>=50,000)
- `orders` (>=2,000 per user; ~20,000 total with 10 users)
- `order_details` (5-15 product rows per order)

Generation tools:
- `scripts/generate_phase2_data.py`
- `src/project/phase2/database.py`

## Run commands

```bash
set PHASE2_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/kombee_phase2
python -m scripts.generate_phase2_data
python -m src.project.phase2.main --menu-path ./examples/sample_menu.txt --user-id 1
```

