"""
Standalone FastAPI Microservice for AI Features
Runs completely independent of the core backend and UI.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

from app.services.ai.pricing_ai import DynamicPricingEngine
from app.services.ai.recommendation_ai import RecommendationEngine
from app.services.ai.auto_booking_ai import AutoBookingAgent
from app.services.ai.chatbot_ai import ParkingChatbot
from app.services.ai.llm_chatbot import LLMChatbot, USE_LLM

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AI SERVICE - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ParkMyCar AI Microservice",
    description="Decoupled AI features (Pricing, Recommendations, Agent, Chatbot)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 1. Dynamic Pricing API ===
class PricingRequest(BaseModel):
    base_price: float

@app.post("/api/ai/pricing/calculate/{lot_id}")
async def calculate_dynamic_price(lot_id: int, req: PricingRequest):
    result = await DynamicPricingEngine.calculate_dynamic_price(lot_id, req.base_price)
    return {"status": "success", "data": result}

@app.get("/api/ai/pricing/history/{lot_id}")
async def get_price_history(lot_id: int, days: int = 7):
    result = await DynamicPricingEngine.get_price_history(lot_id, days)
    return {"status": "success", "data": result}

@app.get("/api/ai/pricing/trend/{lot_id}")
async def get_price_trend(lot_id: int):
    # Running synchronously as defined
    result = DynamicPricingEngine.get_price_trend(lot_id)
    return {"status": "success", "data": result}


# === 2. Recommendation System API ===
@app.get("/api/ai/recommendations/{user_id}")
async def get_recommendations(user_id: int, location: Optional[str] = None, limit: int = 5):
    recommendations = await RecommendationEngine.get_recommendations(user_id, location, limit)
    return {"status": "success", "data": recommendations}


# === 3. Auto-Booking Agent API ===
class AutoBookingSettingsReq(BaseModel):
    enabled: bool = True
    auto_confirm: bool = False
    max_price_threshold: Optional[float] = None

@app.post("/api/ai/auto-booking/settings/{user_id}")
async def update_auto_booking_settings(user_id: int, settings: AutoBookingSettingsReq):
    success = await AutoBookingAgent.save_auto_booking_settings(
        user_id, settings.enabled, settings.auto_confirm, settings.max_price_threshold
    )
    return {"status": "success" if success else "error"}

@app.get("/api/ai/auto-booking/suggestions/{user_id}")
async def get_auto_booking_suggestions(user_id: int):
    suggestions = await AutoBookingAgent.get_auto_booking_suggestions(user_id)
    return {"status": "success", "data": suggestions}

@app.post("/api/ai/auto-booking/trigger-job")
async def trigger_auto_booking_job():
    executed = await AutoBookingAgent.check_and_execute_auto_bookings()
    return {"status": "success", "executed_count": len(executed), "data": executed}


# === 4. Chatbot API ===
class ChatMessageReq(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = None

@app.post("/api/ai/chatbot/query/{user_id}")
async def chatbot_query(user_id: int, req: ChatMessageReq):
    if USE_LLM:
        result = await LLMChatbot.generate_response(req.message, user_id, req.conversation_history)
        return {"status": "success", "data": result}
    else:
        result = await ParkingChatbot.generate_response(req.message, user_id, "session-1")
        return {"status": "success", "data": result}


@app.get("/health")
async def ai_health():
    return {"status": "healthy", "service": "AI Microservice"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AI_API_PORT", 8001))
    uvicorn.run("app.ai.main:app", host="0.0.0.0", port=port, reload=True)
