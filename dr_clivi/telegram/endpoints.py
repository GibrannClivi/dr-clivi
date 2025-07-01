"""
FastAPI Endpoints - Separados del handler para mejor organización
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict

from ..config import Config
from .handler_optimized import TelegramHandlerOptimized

app = FastAPI(title="Dr. Clivi Telegram Bot")
telegram_handler = None


def init_telegram_handler(config: Config):
    """Inicializa el handler de Telegram"""
    global telegram_handler
    telegram_handler = TelegramHandlerOptimized(config)


@app.post("/telegram-webhook")
async def receive_webhook(request: Request):
    """Recibe webhooks de Telegram"""
    if not telegram_handler:
        raise HTTPException(status_code=500, detail="Handler not initialized")
    
    try:
        update_data = await request.json()
        result = await telegram_handler.process_update(update_data)
        return JSONResponse(content={"status": "success", "result": result})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}")


@app.get("/telegram-bot-info")
async def get_bot_info():
    """Obtiene información del bot"""
    if not telegram_handler:
        raise HTTPException(status_code=500, detail="Handler not initialized")
    
    bot_info = await telegram_handler.get_bot_info()
    return JSONResponse(content=bot_info)


@app.post("/set-telegram-webhook")
async def set_webhook(webhook_data: Dict[str, str]):
    """Configura webhook de Telegram"""
    if not telegram_handler:
        raise HTTPException(status_code=500, detail="Handler not initialized")
    
    webhook_url = webhook_data.get("webhook_url")
    if not webhook_url:
        raise HTTPException(status_code=400, detail="webhook_url required")
    
    success = await telegram_handler.set_webhook(webhook_url)
    return JSONResponse(content={"success": success, "webhook_url": webhook_url})


@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "service": "dr-clivi-telegram-bot"}


if __name__ == "__main__":
    import uvicorn
    
    config = Config()
    init_telegram_handler(config)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
