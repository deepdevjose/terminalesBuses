#!/bin/bash
# Script para iniciar el servidor con limpieza automática del puerto

PUERTO=${1:-5000}

echo "=================================================="
echo "  INICIANDO SERVIDOR DE VENTA DE ASIENTOS"
echo "=================================================="
echo ""

# Verificar si el puerto está en uso
echo "🔍 Verificando puerto $PUERTO..."
PROCESO=$(lsof -ti:$PUERTO 2>/dev/null)

if [ ! -z "$PROCESO" ]; then
    echo "⚠️  Puerto $PUERTO en uso por proceso(s): $PROCESO"
    echo ""
    read -p "¿Deseas matar el proceso y continuar? (s/n): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        echo "🔪 Matando proceso(s)..."
        kill -9 $PROCESO 2>/dev/null
        sleep 0.5
        echo "✓ Puerto liberado"
    else
        echo "❌ Operación cancelada"
        exit 1
    fi
else
    echo "✓ Puerto $PUERTO disponible"
fi

echo ""
echo "🚀 Iniciando servidor en puerto $PUERTO..."
echo ""

# Iniciar servidor
python servidor.py $PUERTO
