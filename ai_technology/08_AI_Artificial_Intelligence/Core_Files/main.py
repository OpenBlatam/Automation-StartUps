"""
Backend API para SaaS de IA Marketing - Respuestas Inteligentes en Redes Sociales
FastAPI con arquitectura escalable y microservicios
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json
import os
from contextlib import asynccontextmanager

# Importar nuestros módulos
from ai_response_engine import AIResponseEngine, CommentAnalysis, GeneratedResponse
from template_system import AdvancedTemplateEngine, ResponseTemplate
from database import DatabaseManager
from auth import AuthManager
from social_media_integrations import SocialMediaManager
from analytics import AnalyticsEngine
from config import Settings

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
settings = Settings()

# Inicializar componentes
db_manager = DatabaseManager()
auth_manager = AuthManager()
social_manager = SocialMediaManager()
analytics_engine = AnalyticsEngine()
ai_engine = AIResponseEngine(
    openai_api_key=settings.OPENAI_API_KEY,
    redis_url=settings.REDIS_URL,
    db_url=settings.DATABASE_URL
)
template_engine = AdvancedTemplateEngine()

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    logger.info("Iniciando aplicación...")
    await db_manager.initialize()
    await social_manager.initialize()
    await analytics_engine.initialize()
    
    # Inicializar plantillas predefinidas
    from template_system import initialize_predefined_templates
    initialize_predefined_templates(template_engine)
    
    logger.info("Aplicación iniciada correctamente")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    await db_manager.close()
    await social_manager.close()
    await analytics_engine.close()
    logger.info("Aplicación cerrada")

# Crear aplicación FastAPI
app = FastAPI(
    title="AI Marketing SaaS API",
    description="API para automatización de respuestas en redes sociales con IA",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencias
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtener usuario actual autenticado"""
    try:
        user = await auth_manager.verify_token(credentials.credentials)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error de autenticación"
        )

async def get_user_analytics(user_id: str):
    """Obtener analytics del usuario"""
    return await analytics_engine.get_user_analytics(user_id)

# Rutas de autenticación
@app.post("/api/auth/register")
async def register(user_data: Dict[str, Any]):
    """Registrar nuevo usuario"""
    try:
        user = await auth_manager.register_user(user_data)
        return {"message": "Usuario registrado exitosamente", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def login(credentials: Dict[str, str]):
    """Iniciar sesión"""
    try:
        token = await auth_manager.authenticate_user(
            credentials["email"], 
            credentials["password"]
        )
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/api/auth/refresh")
async def refresh_token(current_user: Dict = Depends(get_current_user)):
    """Renovar token de acceso"""
    try:
        new_token = await auth_manager.refresh_token(current_user["id"])
        return {"access_token": new_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# Rutas de comentarios
@app.get("/api/comments")
async def get_comments(
    sentiment: Optional[str] = None,
    platform: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict = Depends(get_current_user)
):
    """Obtener comentarios con filtros"""
    try:
        filters = {
            "user_id": current_user["id"],
            "sentiment": sentiment,
            "platform": platform,
            "search": search,
            "limit": limit,
            "offset": offset
        }
        
        comments = await db_manager.get_comments(filters)
        total = await db_manager.count_comments(filters)
        
        return {
            "comments": comments,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error obteniendo comentarios: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/comments/{comment_id}")
async def get_comment(
    comment_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Obtener comentario específico"""
    try:
        comment = await db_manager.get_comment(comment_id, current_user["id"])
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario no encontrado")
        
        return comment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo comentario {comment_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/comments/{comment_id}/generate-response")
async def generate_response(
    comment_id: str,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Generar respuesta para comentario"""
    try:
        # Obtener comentario
        comment = await db_manager.get_comment(comment_id, current_user["id"])
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario no encontrado")
        
        # Análisis del comentario
        analysis = await ai_engine._analyze_comment(comment["content"], {
            "user_id": current_user["id"],
            "platform": comment["platform"],
            "timestamp": comment["created_at"]
        })
        
        # Seleccionar plantilla
        template, score = await template_engine.select_best_template(
            {
                "content": comment["content"],
                "sentiment": analysis.sentiment.value,
                "intent": analysis.intent.value,
                "confidence": analysis.sentiment_confidence,
                "author": comment["author_username"],
                "entities": analysis.entities,
                "keywords": analysis.keywords
            },
            {
                "platform": comment["platform"],
                "user_id": current_user["id"],
                "language": "es"
            }
        )
        
        # Generar respuesta
        response = await ai_engine._generate_response(
            analysis, template, {
                "platform": comment["platform"],
                "user_id": current_user["id"],
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Guardar respuesta generada
        await db_manager.save_generated_response(comment_id, response)
        
        # Actualizar analytics en background
        background_tasks.add_task(
            analytics_engine.track_response_generation,
            current_user["id"],
            comment_id,
            response.confidence_score
        )
        
        return {
            "response_id": response.response_id,
            "content": response.content,
            "confidence_score": response.confidence_score,
            "template_used": template.name,
            "template_score": score
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando respuesta para {comment_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/comments/{comment_id}/send-response")
async def send_response(
    comment_id: str,
    response_data: Dict[str, str],
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Enviar respuesta a comentario"""
    try:
        # Obtener comentario
        comment = await db_manager.get_comment(comment_id, current_user["id"])
        if not comment:
            raise HTTPException(status_code=404, detail="Comentario no encontrado")
        
        # Enviar respuesta a red social
        result = await social_manager.send_response(
            comment["platform"],
            comment["comment_id"],
            response_data["response"],
            current_user["id"]
        )
        
        # Marcar como enviado en base de datos
        await db_manager.mark_response_sent(comment_id, response_data["response"])
        
        # Actualizar analytics en background
        background_tasks.add_task(
            analytics_engine.track_response_sent,
            current_user["id"],
            comment_id,
            result.get("engagement_metrics", {})
        )
        
        return {
            "message": "Respuesta enviada exitosamente",
            "response_id": result.get("response_id"),
            "platform_response": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enviando respuesta para {comment_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Rutas de plantillas
@app.get("/api/templates")
async def get_templates(
    category: Optional[str] = None,
    language: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Obtener plantillas disponibles"""
    try:
        templates = []
        for template in template_engine.templates.values():
            if template.is_active:
                if category and template.category.value != category:
                    continue
                if language and template.language.value != language:
                    continue
                
                templates.append({
                    "template_id": template.template_id,
                    "name": template.name,
                    "category": template.category.value,
                    "language": template.language.value,
                    "content": template.content,
                    "variables": [var.__dict__ for var in template.variables],
                    "success_rate": template.success_rate,
                    "usage_count": template.usage_count
                })
        
        return {"templates": templates}
        
    except Exception as e:
        logger.error(f"Error obteniendo plantillas: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/templates")
async def create_template(
    template_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Crear nueva plantilla"""
    try:
        # Validar datos de plantilla
        required_fields = ["name", "category", "content"]
        for field in required_fields:
            if field not in template_data:
                raise HTTPException(status_code=400, detail=f"Campo requerido: {field}")
        
        # Crear plantilla
        template = template_engine.create_template(
            name=template_data["name"],
            category=template_data["category"],
            language=template_data.get("language", "es"),
            content=template_data["content"],
            variables=template_data.get("variables", []),
            sentiment_target=template_data.get("sentiment_target", "neutral"),
            intent_target=template_data.get("intent_target", "general"),
            urgency_level=template_data.get("urgency_level", "medium"),
            confidence_threshold=template_data.get("confidence_threshold", 0.5),
            tags=template_data.get("tags", []),
            brand_voice=template_data.get("brand_voice", {})
        )
        
        return {
            "message": "Plantilla creada exitosamente",
            "template_id": template.template_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando plantilla: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/templates/{template_id}/analytics")
async def get_template_analytics(
    template_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Obtener analytics de plantilla"""
    try:
        analytics = template_engine.get_template_analytics(template_id)
        return analytics
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error obteniendo analytics de plantilla {template_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Rutas de analytics
@app.get("/api/analytics/dashboard")
async def get_dashboard_analytics(
    period: str = "7d",
    current_user: Dict = Depends(get_current_user)
):
    """Obtener métricas del dashboard"""
    try:
        analytics = await analytics_engine.get_dashboard_metrics(
            current_user["id"], period
        )
        return analytics
        
    except Exception as e:
        logger.error(f"Error obteniendo analytics del dashboard: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.get("/api/analytics/performance")
async def get_performance_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Obtener analytics de rendimiento"""
    try:
        analytics = await analytics_engine.get_performance_metrics(
            current_user["id"], start_date, end_date
        )
        return analytics
        
    except Exception as e:
        logger.error(f"Error obteniendo analytics de rendimiento: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Rutas de integraciones sociales
@app.get("/api/social-accounts")
async def get_social_accounts(
    current_user: Dict = Depends(get_current_user)
):
    """Obtener cuentas sociales conectadas"""
    try:
        accounts = await db_manager.get_social_accounts(current_user["id"])
        return {"accounts": accounts}
        
    except Exception as e:
        logger.error(f"Error obteniendo cuentas sociales: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/social-accounts/connect")
async def connect_social_account(
    account_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Conectar cuenta social"""
    try:
        # Validar datos
        required_fields = ["platform", "access_token"]
        for field in required_fields:
            if field not in account_data:
                raise HTTPException(status_code=400, detail=f"Campo requerido: {field}")
        
        # Conectar cuenta
        result = await social_manager.connect_account(
            current_user["id"],
            account_data["platform"],
            account_data["access_token"],
            account_data.get("refresh_token")
        )
        
        return {
            "message": "Cuenta conectada exitosamente",
            "account_id": result["account_id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error conectando cuenta social: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.delete("/api/social-accounts/{account_id}")
async def disconnect_social_account(
    account_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Desconectar cuenta social"""
    try:
        await social_manager.disconnect_account(account_id, current_user["id"])
        return {"message": "Cuenta desconectada exitosamente"}
        
    except Exception as e:
        logger.error(f"Error desconectando cuenta social: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Rutas de configuración
@app.get("/api/settings")
async def get_settings(
    current_user: Dict = Depends(get_current_user)
):
    """Obtener configuración del usuario"""
    try:
        settings = await db_manager.get_user_settings(current_user["id"])
        return settings
        
    except Exception as e:
        logger.error(f"Error obteniendo configuración: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.put("/api/settings")
async def update_settings(
    settings_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Actualizar configuración del usuario"""
    try:
        await db_manager.update_user_settings(current_user["id"], settings_data)
        return {"message": "Configuración actualizada exitosamente"}
        
    except Exception as e:
        logger.error(f"Error actualizando configuración: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Webhooks para redes sociales
@app.post("/api/webhooks/facebook")
async def facebook_webhook(webhook_data: Dict[str, Any]):
    """Webhook de Facebook para nuevos comentarios"""
    try:
        # Procesar webhook de Facebook
        await social_manager.process_facebook_webhook(webhook_data)
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error procesando webhook de Facebook: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/webhooks/instagram")
async def instagram_webhook(webhook_data: Dict[str, Any]):
    """Webhook de Instagram para nuevos comentarios"""
    try:
        # Procesar webhook de Instagram
        await social_manager.process_instagram_webhook(webhook_data)
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error procesando webhook de Instagram: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@app.post("/api/webhooks/twitter")
async def twitter_webhook(webhook_data: Dict[str, Any]):
    """Webhook de Twitter para nuevas menciones"""
    try:
        # Procesar webhook de Twitter
        await social_manager.process_twitter_webhook(webhook_data)
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error procesando webhook de Twitter: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Manejo de errores globales
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
