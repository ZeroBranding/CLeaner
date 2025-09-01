"""
REST API Server für GermanCodeZero-Cleaner
==========================================

FastAPI-basierte REST API für Frontend-Backend-Kommunikation.
"""

import os
import sys
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

# Import Backend-Module
from src.core.database import get_database, ScanRecord, UserSettings
from src.core.system_monitor import get_system_monitor
from src.ai.ai_manager import get_ai_manager
from cleaner_engine import AdvancedSystemScanner, AdvancedCleaner
from cleaner.hardware.cpu import get_cpu_monitor
from cleaner.hardware.gpu import GPUMonitor
from cleaner.hardware.ram import RAMMonitor
from cleaner.hardware.ssd import SSDMonitor

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# API MODELS
# ============================================================================

class ScanRequest(BaseModel):
    """Scan-Anfrage."""
    categories: List[str] = Field(default=["temp_files", "cache", "logs"])
    enable_ai: bool = Field(default=True)
    user_id: Optional[str] = Field(default="default")


class ScanResponse(BaseModel):
    """Scan-Antwort."""
    scan_id: int
    status: str
    total_files: int
    total_size: int
    categories: Dict[str, int]
    message: str


class CleanRequest(BaseModel):
    """Bereinigungs-Anfrage."""
    scan_id: int
    selected_items: List[str]
    create_backup: bool = Field(default=True)
    user_id: Optional[str] = Field(default="default")


class CleanResponse(BaseModel):
    """Bereinigungs-Antwort."""
    success: bool
    files_deleted: int
    bytes_freed: int
    backup_path: Optional[str]
    message: str


class SystemInfoResponse(BaseModel):
    """System-Informationen."""
    os: str
    cpu: Dict[str, Any]
    memory: Dict[str, Any]
    disk: List[Dict[str, Any]]
    gpu: Optional[Dict[str, Any]]
    network: List[Dict[str, Any]]


class AIRequest(BaseModel):
    """AI-Anfrage."""
    prompt: str
    context: Optional[str] = None
    max_tokens: int = Field(default=500)
    temperature: float = Field(default=0.7)


class AIResponse(BaseModel):
    """AI-Antwort."""
    response: str
    model_used: str
    tokens_used: int
    response_time_ms: float


class SettingsRequest(BaseModel):
    """Einstellungs-Anfrage."""
    user_id: str
    auto_scan_enabled: bool = True
    data_sharing_enabled: bool = False
    theme: str = "dark"
    language: str = "de"
    selected_categories: List[str] = Field(default=["temp_files", "cache", "logs"])


# ============================================================================
# API SERVER
# ============================================================================

app = FastAPI(
    title="GermanCodeZero-Cleaner API",
    description="REST API für System-Optimierung und Bereinigung",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State
scanner = AdvancedSystemScanner()
cleaner = AdvancedCleaner()
active_scans = {}
active_websockets = []


# ============================================================================
# HEALTH & STATUS ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health Check Endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api/status")
async def get_status():
    """Gibt Server-Status zurück."""
    monitor = get_system_monitor()
    current_usage = monitor.get_current_usage()
    
    return {
        "server_status": "running",
        "active_scans": len(active_scans),
        "connected_clients": len(active_websockets),
        "cpu_usage": current_usage.cpu_percent if current_usage else 0,
        "memory_usage": current_usage.memory_percent if current_usage else 0,
        "uptime": (datetime.now() - app.state.start_time).total_seconds() if hasattr(app.state, 'start_time') else 0
    }


# ============================================================================
# SYSTEM INFORMATION ENDPOINTS
# ============================================================================

@app.get("/api/system/info", response_model=SystemInfoResponse)
async def get_system_info():
    """Gibt System-Informationen zurück."""
    monitor = get_system_monitor()
    cpu_monitor = get_cpu_monitor()
    gpu_monitor = GPUMonitor()
    ram_monitor = RAMMonitor()
    ssd_monitor = SSDMonitor()
    
    system_info = monitor.system_info
    
    return SystemInfoResponse(
        os=f"{system_info.os_name} {system_info.os_version}" if system_info else "Unknown",
        cpu={
            "model": system_info.cpu_model if system_info else "Unknown",
            "cores": system_info.cpu_cores if system_info else 0,
            "threads": system_info.cpu_threads if system_info else 0,
            "frequency": system_info.cpu_frequency if system_info else 0,
            "usage": cpu_monitor.get_current_usage().overall_percent if cpu_monitor.get_current_usage() else 0
        },
        memory={
            "total": system_info.memory_total if system_info else 0,
            "available": system_info.memory_available if system_info else 0,
            "usage": ram_monitor.get_current_usage().percent if ram_monitor.get_current_usage() else 0
        },
        disk=[
            {
                "device": disk.device,
                "total": disk.total,
                "free": disk.free,
                "percent": disk.percent
            }
            for disk in ssd_monitor.get_current_usage().values()
        ],
        gpu={
            "name": system_info.gpu_info[0]["name"] if system_info and system_info.gpu_info else None,
            "memory": system_info.gpu_info[0]["memory_total"] if system_info and system_info.gpu_info else None,
            "usage": gpu_monitor.get_current_usage().gpu_utilization if gpu_monitor.get_current_usage() else 0
        } if system_info and system_info.gpu_info else None,
        network=[
            {
                "interface": iface["name"],
                "is_up": iface["is_up"],
                "speed": iface["speed"]
            }
            for iface in (system_info.network_interfaces if system_info else [])
        ]
    )


@app.get("/api/system/usage")
async def get_system_usage():
    """Gibt aktuelle System-Auslastung zurück."""
    monitor = get_system_monitor()
    usage = monitor.get_current_usage()
    
    if not usage:
        return {"error": "No usage data available"}
    
    return {
        "timestamp": usage.timestamp.isoformat(),
        "cpu": {
            "overall": usage.cpu_percent,
            "per_core": usage.cpu_per_core
        },
        "memory": {
            "percent": usage.memory_percent,
            "used": usage.memory_used,
            "available": usage.memory_available
        },
        "disk_io": {
            "read": usage.disk_io_read,
            "write": usage.disk_io_write
        },
        "network": {
            "sent": usage.network_sent,
            "recv": usage.network_recv
        },
        "gpu": {
            "usage": usage.gpu_usage,
            "memory": usage.gpu_memory,
            "temperature": usage.gpu_temperature
        }
    }


@app.get("/api/system/processes")
async def get_top_processes(sort_by: str = "cpu", limit: int = 10):
    """Gibt Top-Prozesse zurück."""
    monitor = get_system_monitor()
    processes = monitor.get_top_processes(count=limit, sort_by=sort_by)
    
    return {
        "processes": [
            {
                "pid": p.pid,
                "name": p.name,
                "cpu_percent": p.cpu_percent,
                "memory_percent": p.memory_percent,
                "memory_rss": p.memory_rss,
                "num_threads": p.num_threads,
                "status": p.status
            }
            for p in processes
        ]
    }


# ============================================================================
# SCAN ENDPOINTS
# ============================================================================

@app.post("/api/scan/start", response_model=ScanResponse)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    """Startet einen System-Scan."""
    try:
        # Generiere Scan-ID
        scan_id = int(datetime.now().timestamp())
        
        # Starte Scan im Hintergrund
        background_tasks.add_task(
            run_scan_task,
            scan_id,
            request.categories,
            request.enable_ai,
            request.user_id
        )
        
        active_scans[scan_id] = {
            "status": "running",
            "progress": 0,
            "start_time": datetime.now()
        }
        
        return ScanResponse(
            scan_id=scan_id,
            status="started",
            total_files=0,
            total_size=0,
            categories={},
            message="Scan wurde gestartet"
        )
        
    except Exception as e:
        logger.error(f"Scan start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_scan_task(scan_id: int, categories: List[str], 
                        enable_ai: bool, user_id: str):
    """Führt Scan-Task aus."""
    try:
        # Progress Callback
        def progress_callback(status: str, progress: float):
            if scan_id in active_scans:
                active_scans[scan_id]["status"] = status
                active_scans[scan_id]["progress"] = progress
                
                # Sende Update über WebSocket
                asyncio.create_task(broadcast_scan_progress(scan_id, status, progress))
        
        # Führe Scan aus
        results = await scanner.perform_comprehensive_scan(
            categories=categories,
            progress_callback=progress_callback,
            enable_ai_analysis=enable_ai
        )
        
        # Speichere in Datenbank
        db = get_database()
        
        total_files = sum(cat.total_count for cat in results.values())
        total_size = sum(cat.total_size for cat in results.values())
        
        scan_record = ScanRecord(
            timestamp=datetime.now(),
            duration_seconds=(datetime.now() - active_scans[scan_id]["start_time"]).total_seconds(),
            total_files=total_files,
            total_size=total_size,
            categories={cat: len(items.items) for cat, items in results.items()},
            user_id=user_id
        )
        
        db_scan_id = db.save_scan_result(scan_record)
        
        # Update Status
        active_scans[scan_id]["status"] = "completed"
        active_scans[scan_id]["results"] = results
        active_scans[scan_id]["db_scan_id"] = db_scan_id
        
    except Exception as e:
        logger.error(f"Scan task failed: {e}")
        if scan_id in active_scans:
            active_scans[scan_id]["status"] = "failed"
            active_scans[scan_id]["error"] = str(e)


@app.get("/api/scan/status/{scan_id}")
async def get_scan_status(scan_id: int):
    """Gibt Scan-Status zurück."""
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan_info = active_scans[scan_id]
    
    return {
        "scan_id": scan_id,
        "status": scan_info["status"],
        "progress": scan_info.get("progress", 0),
        "error": scan_info.get("error")
    }


@app.get("/api/scan/results/{scan_id}")
async def get_scan_results(scan_id: int):
    """Gibt Scan-Ergebnisse zurück."""
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    scan_info = active_scans[scan_id]
    
    if scan_info["status"] != "completed":
        return {"status": scan_info["status"], "message": "Scan not completed yet"}
    
    results = scan_info.get("results", {})
    
    # Konvertiere zu JSON-kompatiblem Format
    formatted_results = {}
    for category_name, category in results.items():
        formatted_results[category_name] = {
            "name": category.name,
            "total_count": category.total_count,
            "total_size": category.total_size,
            "items": [
                {
                    "path": item.metadata.path,
                    "size": item.metadata.size,
                    "safety_score": item.safety_score,
                    "ai_explanation": item.ai_explanation
                }
                for item in category.items[:100]  # Limitiere auf 100 Items
            ]
        }
    
    return {
        "scan_id": scan_id,
        "results": formatted_results
    }


# ============================================================================
# CLEANING ENDPOINTS
# ============================================================================

@app.post("/api/clean/start", response_model=CleanResponse)
async def start_cleaning(request: CleanRequest, background_tasks: BackgroundTasks):
    """Startet Bereinigung."""
    try:
        if request.scan_id not in active_scans:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        scan_info = active_scans[request.scan_id]
        
        if scan_info["status"] != "completed":
            raise HTTPException(status_code=400, detail="Scan not completed")
        
        # Sammle ausgewählte Items
        results = scan_info.get("results", {})
        selected_items = []
        
        for category in results.values():
            for item in category.items:
                if item.metadata.path in request.selected_items:
                    item.user_selected = True
                    selected_items.append(item)
        
        if not selected_items:
            return CleanResponse(
                success=False,
                files_deleted=0,
                bytes_freed=0,
                backup_path=None,
                message="Keine Dateien ausgewählt"
            )
        
        # Führe Bereinigung aus
        cleaning_result = await cleaner.perform_cleaning(
            items=selected_items,
            create_backup=request.create_backup
        )
        
        # Speichere in Datenbank
        db = get_database()
        from src.core.database import CleaningHistory
        
        cleaning_history = CleaningHistory(
            scan_id=scan_info.get("db_scan_id"),
            files_deleted=[item.metadata.path for item in selected_items],
            total_size_freed=cleaning_result["bytes_freed"],
            backup_path=cleaning_result.get("backup_path"),
            success=cleaning_result["success"]
        )
        
        db.save_cleaning_history(cleaning_history)
        
        return CleanResponse(
            success=cleaning_result["success"],
            files_deleted=cleaning_result["files_deleted"],
            bytes_freed=cleaning_result["bytes_freed"],
            backup_path=cleaning_result.get("backup_path"),
            message="Bereinigung erfolgreich abgeschlossen"
        )
        
    except Exception as e:
        logger.error(f"Cleaning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# AI ENDPOINTS
# ============================================================================

@app.post("/api/ai/chat", response_model=AIResponse)
async def ai_chat(request: AIRequest):
    """AI Chat Endpoint."""
    try:
        ai_manager = get_ai_manager()
        
        response = await ai_manager.generate(
            prompt=request.prompt,
            context=request.context,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return AIResponse(
            response=response.response_text,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            response_time_ms=response.response_time_ms
        )
        
    except Exception as e:
        logger.error(f"AI chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ai/models")
async def get_ai_models():
    """Gibt verfügbare AI-Modelle zurück."""
    ai_manager = get_ai_manager()
    
    models = []
    for name, model in ai_manager.available_models.items():
        models.append({
            "name": name,
            "provider": model.provider.value,
            "size_gb": model.size_gb,
            "is_available": model.is_available,
            "is_loaded": model.is_loaded
        })
    
    return {"models": models}


# ============================================================================
# SETTINGS ENDPOINTS
# ============================================================================

@app.get("/api/settings/{user_id}")
async def get_settings(user_id: str):
    """Gibt Benutzer-Einstellungen zurück."""
    db = get_database()
    settings = db.get_user_settings(user_id)
    
    if not settings:
        # Return defaults
        return {
            "user_id": user_id,
            "auto_scan_enabled": True,
            "data_sharing_enabled": False,
            "theme": "dark",
            "language": "de",
            "selected_categories": ["temp_files", "cache", "logs"]
        }
    
    return {
        "user_id": settings.user_id,
        "auto_scan_enabled": settings.auto_scan_enabled,
        "data_sharing_enabled": settings.data_sharing_enabled,
        "theme": settings.theme,
        "language": settings.language,
        "selected_categories": settings.selected_categories
    }


@app.post("/api/settings/update")
async def update_settings(request: SettingsRequest):
    """Aktualisiert Benutzer-Einstellungen."""
    try:
        db = get_database()
        
        settings = UserSettings(
            user_id=request.user_id,
            auto_scan_enabled=request.auto_scan_enabled,
            data_sharing_enabled=request.data_sharing_enabled,
            theme=request.theme,
            language=request.language,
            selected_categories=request.selected_categories
        )
        
        db.save_user_settings(settings)
        
        return {"success": True, "message": "Einstellungen gespeichert"}
        
    except Exception as e:
        logger.error(f"Settings update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket für Echtzeit-Updates."""
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        # Starte System-Monitoring
        monitor = get_system_monitor()
        monitor.start_monitoring(interval=1.0)
        
        while True:
            # Sende System-Updates
            usage = monitor.get_current_usage()
            
            if usage:
                await websocket.send_json({
                    "type": "system_update",
                    "data": {
                        "cpu": usage.cpu_percent,
                        "memory": usage.memory_percent,
                        "disk_io": usage.disk_io_read + usage.disk_io_write,
                        "timestamp": usage.timestamp.isoformat()
                    }
                })
            
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        active_websockets.remove(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in active_websockets:
            active_websockets.remove(websocket)


async def broadcast_scan_progress(scan_id: int, status: str, progress: float):
    """Sendet Scan-Fortschritt an alle WebSocket-Clients."""
    message = {
        "type": "scan_progress",
        "data": {
            "scan_id": scan_id,
            "status": status,
            "progress": progress
        }
    }
    
    for websocket in active_websockets:
        try:
            await websocket.send_json(message)
        except:
            # Client disconnected
            if websocket in active_websockets:
                active_websockets.remove(websocket)


# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Server-Start-Event."""
    app.state.start_time = datetime.now()
    
    # Initialisiere System-Monitor
    monitor = get_system_monitor()
    monitor.start_monitoring()
    
    # Initialisiere AI Manager
    ai_manager = get_ai_manager()
    await ai_manager.load_model(AI_CONFIG["default_model"])
    
    logger.info("API Server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Server-Shutdown-Event."""
    # Stoppe System-Monitor
    monitor = get_system_monitor()
    monitor.stop_monitoring()
    
    # Cleanup
    ai_manager = get_ai_manager()
    ai_manager.cleanup()
    
    # Schließe Datenbank
    db = get_database()
    db.close()
    
    logger.info("API Server shutdown complete")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )