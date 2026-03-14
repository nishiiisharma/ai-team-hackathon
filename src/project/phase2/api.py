from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.project.config.settings import get_settings
from src.project.phase2.database import get_connection
from src.project.phase2.menu_parser import MenuParser
from src.project.phase2.predictor import PurchasePredictor

app = FastAPI(title="Kombee AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# In-memory store for session continuity across the pipeline
sessions: Dict[int, Dict[str, Any]] = {}

def get_session(user_id: int) -> Dict[str, Any]:
    if user_id not in sessions:
        sessions[user_id] = {}
    return sessions[user_id]

@app.post("/upload-menu")
async def upload_menu(file: UploadFile = File(...), user_id: int = Form(...)):
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    session = get_session(user_id)
    session["menu_path"] = str(file_path)
    return {"message": "Menu uploaded successfully", "file_name": file.filename}

@app.post("/analyze")
async def analyze_menu(user_id: int = Form(...)):
    session = get_session(user_id)
    menu_path = session.get("menu_path")
    if not menu_path:
        raise HTTPException(status_code=400, detail="No menu uploaded for this user.")

    settings = get_settings()
    parser = MenuParser(gemini_api_key=settings.gemini_api_key, llm_model=settings.default_llm_model)
    
    try:
        menu_text = parser.load_menu_text(menu_path)
        dishes = parser.extract_dishes(menu_text)
        ingredients = sorted({ingredient for dish in dishes for ingredient in dish.ingredients})
        
        # Save to session
        session["dishes"] = [{"name": d.name, "ingredients": d.ingredients} for d in dishes]
        session["ingredients"] = ingredients
        
        return {
            "dishes": session["dishes"],
            "ingredients": ingredients
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ingredients-stock")
async def get_ingredients_stock(user_id: int):
    session = get_session(user_id)
    ingredients = session.get("ingredients")
    if not ingredients:
        raise HTTPException(status_code=400, detail="Menu not analyzed yet.")

    settings = get_settings()
    db_url = os.getenv("PHASE2_DATABASE_URL", "postgresql://admin:admin123@localhost:5433/kombee_phase2")
    conn = get_connection(db_url)
    
    try:
        predictor = PurchasePredictor(conn=conn)
        predictions = predictor.predict_for_user(user_id=user_id, ingredients=ingredients, horizon_days=7)
        
        stock_data = [{"ingredient": p.ingredient, "available_stock": p.available_stock} for p in predictions]
        session["predictions"] = predictions  # cache full predictions object for later
        
        return {"stock": stock_data}
    finally:
        conn.close()

@app.post("/predict")
async def predict_quantity(user_id: int = Form(...)):
    session = get_session(user_id)
    predictions = session.get("predictions")
    
    if not predictions:
        # If not cached, they skipped the step, so calculate it
        ingredients = session.get("ingredients")
        if not ingredients:
             raise HTTPException(status_code=400, detail="Analyze menu first.")
        
        db_url = os.getenv("PHASE2_DATABASE_URL", "postgresql://admin:admin123@localhost:5433/kombee_phase2")
        conn = get_connection(db_url)
        try:
            predictor = PurchasePredictor(conn=conn)
            predictions = predictor.predict_for_user(user_id=user_id, ingredients=ingredients, horizon_days=7)
            session["predictions"] = predictions
        finally:
            conn.close()

    predict_data = [{"ingredient": p.ingredient, "predicted_quantity": p.predicted_required_quantity} for p in predictions]
    return {"predictions": predict_data}

@app.get("/cart")
async def get_cart(user_id: int):
    session = get_session(user_id)
    predictions = session.get("predictions")
    if not predictions:
        raise HTTPException(status_code=400, detail="Prediction not run yet.")
        
    cart_items = []
    for p in predictions:
        recommended = round(max(p.predicted_required_quantity - p.available_stock, 0.0), 2)
        if recommended > 0:
            cart_items.append({
                "ingredient": p.ingredient,
                "available_stock": p.available_stock,
                "predicted_required_quantity": p.predicted_required_quantity,
                "recommended_order_quantity": recommended
            })
            
    return {"cart": cart_items}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
