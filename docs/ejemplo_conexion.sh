#!/bin/bash
# Script de ejemplo para conectar cliente al servidor

echo "=================================================="
echo "   EJEMPLO DE CONEXIÓN CLIENTE-SERVIDOR"
echo "=================================================="
echo ""
echo "📍 PASO 1: Obtener IP del servidor"
echo "   En la máquina del servidor, ejecuta:"
echo "   $ python obtener_ip.py"
echo ""
echo "📍 PASO 2: Iniciar el servidor"
echo "   $ python servidor.py"
echo ""
echo "📍 PASO 3: Conectar cliente (desde cualquier máquina)"
echo "   $ python cliente.py <IP_DEL_SERVIDOR>"
echo ""
echo "Ejemplo con tu IP actual:"
IP=$(python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2>/dev/null)
if [ ! -z "$IP" ]; then
    echo "   $ python cliente.py $IP"
fi
echo ""
echo "=================================================="

chmod +x ejemplo_conexion.sh
