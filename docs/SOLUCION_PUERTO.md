# Solución de Problemas: "Address already in use"

## 🔴 Problema

Cuando detienes el servidor con Ctrl+C y lo intentas reiniciar inmediatamente, obtienes:

```
OSError: [Errno 98] Address already in use
```

## ❓ ¿Por Qué Sucede?

Cuando un servidor TCP se cierra, el puerto entra en estado **TIME_WAIT** durante 30-120 segundos. Esto es parte del protocolo TCP para asegurar que todos los paquetes en tránsito se procesen correctamente antes de reutilizar el puerto.

## ✅ Soluciones Implementadas

### 1. SO_REUSEADDR (Automático)

El servidor ahora incluye:

```python
servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
```

Esto permite reutilizar el puerto inmediatamente en la mayoría de casos.

### 2. Cierre Limpio (Automático)

El servidor ahora cierra correctamente el socket:

```python
try:
    servidor_socket.shutdown(socket.SHUT_RDWR)
except:
    pass
servidor_socket.close()
```

### 3. Mensaje de Error Mejorado

Si el puerto sigue ocupado, el servidor muestra instrucciones claras:

```
[ERROR] El puerto 5000 ya está en uso.
Soluciones:
  1. Espera 30-60 segundos y vuelve a intentar
  2. Usa otro puerto: python servidor.py 5001
  3. Mata el proceso que usa el puerto:
     sudo lsof -ti:5000 | xargs kill -9
```

## 🛠️ Herramientas Incluidas

### A) Script de Limpieza Rápida

```bash
# Limpiar puerto automáticamente
python limpiar_puerto.py -r

# O con interfaz interactiva
python limpiar_puerto.py
```

### B) Script de Inicio Inteligente

```bash
# Verifica y limpia el puerto antes de iniciar
./iniciar_servidor.sh
```

### C) Comandos Manuales

Ver qué proceso usa el puerto:
```bash
sudo lsof -i :5000
```

Matar el proceso:
```bash
sudo lsof -ti:5000 | xargs kill -9
```

O en una línea:
```bash
sudo fuser -k 5000/tcp
```

## 📋 Flujo de Trabajo Recomendado

### Opción 1: Usar Script de Inicio (Recomendado)

```bash
./iniciar_servidor.sh
```

Esto:
1. ✅ Verifica si el puerto está libre
2. ✅ Pregunta si quieres matar procesos existentes
3. ✅ Limpia el puerto automáticamente
4. ✅ Inicia el servidor

### Opción 2: Inicio Manual con Limpieza

```bash
# 1. Limpiar puerto
python limpiar_puerto.py -r

# 2. Iniciar servidor
python servidor.py
```

### Opción 3: Esperar

```bash
# Simplemente espera 60 segundos y el puerto se liberará
sleep 60 && python servidor.py
```

### Opción 4: Usar Puerto Diferente

```bash
# Usar puerto 5001 en lugar de 5000
python servidor.py 5001

# Los clientes deben conectarse así:
python cliente.py localhost 5001
```

## 🔍 Diagnóstico

### Ver todos los puertos en uso:

```bash
sudo netstat -tulpn
# o
sudo ss -tulpn
```

### Verificar puerto específico:

```bash
# Con lsof
sudo lsof -i :5000

# Con netstat
sudo netstat -tulpn | grep 5000

# Con ss
sudo ss -tulpn | grep 5000
```

### Ejemplo de salida cuando el puerto está ocupado:

```
COMMAND    PID  USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
python   12345  user    3u  IPv4  123456      0t0  TCP *:5000 (LISTEN)
```

El PID es 12345, puedes matarlo con:
```bash
kill -9 12345
```

## 🎯 Prevención

### 1. Cierra el Servidor Correctamente

Siempre usa **Ctrl+C** en lugar de:
- ❌ `kill -9` (forzado)
- ❌ Cerrar la terminal directamente
- ❌ `killall python` sin discriminar

### 2. Usa el Script de Limpieza

Antes de iniciar el servidor:
```bash
python limpiar_puerto.py -r && python servidor.py
```

### 3. En Desarrollo, Usa Puertos Dinámicos

```bash
# Prueba con diferentes puertos si 5000 está ocupado
for port in 5000 5001 5002 5003; do
    python servidor.py $port && break
done
```

## 🐛 Debugging Avanzado

### Ver estado detallado del puerto:

```bash
watch -n 1 'sudo lsof -i :5000'
```

Esto actualiza cada segundo, útil para ver cuándo se libera el puerto.

### Ver sockets en TIME_WAIT:

```bash
ss -tan | grep TIME-WAIT
```

### Forzar liberación inmediata (último recurso):

```bash
# Linux
sudo sysctl -w net.ipv4.tcp_tw_reuse=1

# Pero mejor usa SO_REUSEADDR que ya está implementado
```

## 📊 Comparación de Soluciones

| Solución | Velocidad | Seguridad | Dificultad |
|----------|-----------|-----------|------------|
| SO_REUSEADDR | ⚡ Inmediata | ✅ Segura | ✅ Fácil (ya implementado) |
| Script limpieza | ⚡ Inmediata | ✅ Segura | ✅ Fácil |
| Esperar 60s | 🐌 Lenta | ✅ Segura | ✅ Muy fácil |
| Otro puerto | ⚡ Inmediata | ✅ Segura | ⚠️ Requiere reconfigurar clientes |
| kill -9 manual | ⚡ Inmediata | ⚠️ Puede perder datos | ⚠️ Requiere permisos |

## ✨ Resumen

**Forma más simple y rápida:**

```bash
python limpiar_puerto.py -r && python servidor.py
```

**O usa el script automático:**

```bash
./iniciar_servidor.sh
```

¡Listo! El servidor ahora maneja mejor el cierre y liberación del puerto. 🎯
