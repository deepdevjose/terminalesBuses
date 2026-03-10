# Guía de Conexión Cliente-Servidor en Red

## 🌐 Conectar desde Otra Máquina

### Paso 1: Obtener la IP del Servidor

En la máquina donde ejecutarás el servidor, corre:

```bash
python obtener_ip.py
```

Esto te mostrará algo como:
```
📍 IP Principal: 192.168.100.98
   → Usa esta IP para conectarte desde otras máquinas en la misma red
```

### Paso 2: Iniciar el Servidor

En la máquina servidor:

```bash
python servidor.py
```

El servidor escuchará en **todas las interfaces** (0.0.0.0), lo que significa que acepta conexiones desde:
- `localhost` (127.0.0.1) - misma máquina
- IP local (192.168.100.98) - otras máquinas en la red

### Paso 3: Conectar Clientes

Hay **3 formas** de conectar un cliente:

#### A) Por Línea de Comandos (Más Fácil) ✅

```bash
# Desde otra máquina en la red
python cliente.py 192.168.100.98

# Con puerto específico
python cliente.py 192.168.100.98 5000
```

#### B) Editando cliente.py

Abre `cliente.py` y cambia la línea 235:

```python
# ANTES (solo funciona localmente)
host = 'localhost'

# DESPUÉS (funciona desde cualquier máquina)
host = '192.168.100.98'  # ← Tu IP aquí
```

#### C) Variable de Entorno

```bash
# Linux/Mac
export SERVIDOR_IP=192.168.100.98
python cliente.py $SERVIDOR_IP

# Windows
set SERVIDOR_IP=192.168.100.98
python cliente.py %SERVIDOR_IP%
```

## 🔥 Configuración del Firewall

Si no puedes conectarte, es probable que el firewall esté bloqueando el puerto 5000.

### Linux (Fedora/CentOS/RHEL)

```bash
# Permitir puerto 5000
sudo firewall-cmd --zone=public --add-port=5000/tcp --permanent
sudo firewall-cmd --reload

# Verificar
sudo firewall-cmd --list-ports
```

### Linux (Ubuntu/Debian)

```bash
# Permitir puerto 5000
sudo ufw allow 5000/tcp

# Verificar
sudo ufw status
```

### Windows

```powershell
# PowerShell como Administrador
New-NetFirewallRule -DisplayName "Servidor Asientos" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

## 📋 Escenarios de Uso

### Escenario 1: Todo en la Misma Máquina (Desarrollo)

```bash
# Terminal 1
python servidor.py

# Terminal 2
python cliente.py
# (usa localhost por defecto)
```

### Escenario 2: Servidor y Cliente en Máquinas Diferentes

**Máquina A (Servidor):**
```bash
python obtener_ip.py  # Anota la IP: 192.168.100.98
python servidor.py
```

**Máquina B (Cliente):**
```bash
python cliente.py 192.168.100.98
```

**Máquina C (Cliente 2):**
```bash
python cliente.py 192.168.100.98
```

### Escenario 3: Servidor en la Nube o VPS

**En el servidor:**
```bash
# Obtener IP pública
curl ifconfig.me

# Iniciar servidor
python servidor.py
```

**En cualquier cliente:**
```bash
python cliente.py <IP_PUBLICA_SERVIDOR>
```

⚠️ **IMPORTANTE para servidores públicos:**
- Configura el firewall correctamente
- Considera usar autenticación
- No uses para producción sin seguridad adicional

## 🧪 Verificar Conectividad

Antes de ejecutar el cliente, verifica que puedes alcanzar el servidor:

### Método 1: ping

```bash
ping 192.168.100.98
```

### Método 2: telnet

```bash
telnet 192.168.100.98 5000
```

Si conecta, verás algo como `Connected to...`. Presiona Ctrl+] y escribe `quit`.

### Método 3: netcat

```bash
nc -zv 192.168.100.98 5000
```

Debe mostrar: `Connection to 192.168.100.98 5000 port [tcp/*] succeeded!`

### Método 4: Python (más confiable)

```bash
python -c "
import socket
try:
    s = socket.socket()
    s.settimeout(3)
    s.connect(('192.168.100.98', 5000))
    print('✓ Conexión exitosa')
    s.close()
except:
    print('✗ No se pudo conectar')
"
```

## 🔍 Solución de Problemas

### Error: "Connection refused"

**Causa:** El servidor no está ejecutándose o el puerto está bloqueado

**Solución:**
1. Verifica que el servidor esté corriendo: `ps aux | grep servidor.py`
2. Verifica que esté escuchando: `netstat -tuln | grep 5000`
3. Revisa el firewall (ver sección anterior)

### Error: "No route to host"

**Causa:** Problema de red o firewall bloqueando

**Solución:**
1. Verifica conectividad básica: `ping <IP_SERVIDOR>`
2. Verifica que ambas máquinas estén en la misma red
3. Revisa configuración del firewall

### Error: "Connection timeout"

**Causa:** Firewall bloqueando o IP incorrecta

**Solución:**
1. Verifica la IP con `python obtener_ip.py`
2. Intenta desde otra máquina en la red
3. Desactiva temporalmente el firewall para probar

## 📊 Tabla de Referencia Rápida

| Ubicación | Comando para Conectar |
|-----------|----------------------|
| Misma máquina | `python cliente.py` |
| Misma red | `python cliente.py <IP_LOCAL>` |
| Internet | `python cliente.py <IP_PUBLICA>` |

## 🎓 Ejemplo Completo

### Red Local con 3 Máquinas

```
┌─────────────────┐
│  Servidor       │  IP: 192.168.100.98
│  (Máquina 1)    │  Ejecuta: python servidor.py
└─────────────────┘
        ↑  ↑
        │  │
    ┌───┘  └───┐
    │          │
┌───┴────┐ ┌──┴─────┐
│Cliente 1│ │Cliente 2│
│(Máq. 2) │ │(Máq. 3) │
└─────────┘ └─────────┘
  python      python
  cliente.py  cliente.py
  192.168...  192.168...
```

**Resultado:** 3 máquinas compitiendo por los 40 asientos, con sistema de prioridades FIFO garantizado. 🎯
