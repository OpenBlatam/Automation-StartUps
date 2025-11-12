#!/bin/bash
# Stop Script - Detiene todos los servicios del sistema

echo "🛑 Deteniendo servicios TikTok Auto Edit..."
echo ""

services=("tiktok_api" "tiktok_webhook" "tiktok_dashboard" "tiktok_queue")

for service in "${services[@]}"; do
    pid_file="/tmp/${service}.pid"
    
    if [ -f "$pid_file" ]; then
        pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            echo "🛑 Deteniendo $service (PID: $pid)..."
            kill $pid 2>/dev/null || true
            sleep 1
            
            # Force kill si aún está corriendo
            if ps -p $pid > /dev/null 2>&1; then
                kill -9 $pid 2>/dev/null || true
            fi
            
            rm -f "$pid_file"
            echo "✅ $service detenido"
        else
            echo "ℹ️  $service no estaba corriendo"
            rm -f "$pid_file"
        fi
    else
        echo "ℹ️  PID file no encontrado para $service"
    fi
done

echo ""
echo "✅ Todos los servicios detenidos"

