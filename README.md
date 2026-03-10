# Sistema de Venta de Asientos - Aplicación Distribuida

Aplicación distribuida cliente-servidor en Python para la gestión de venta de 40 asientos, diseñada como práctica escolar de programación concurrente y comunicación por sockets.

## 📋 Descripción

El sistema consta de dos componentes:

- **Servidor Central**: Mantiene el estado de los 40 asientos y procesa peticiones de múltiples clientes simultáneamente usando threading.
- **Cliente Terminal**: Interfaz de usuario por consola que permite comprar asientos y consultar el estado.

## 🏗️ Arquitectura

```
[Cliente 1] <---\
[Cliente 2] <----> [Servidor Central] (40 asientos)
[Cliente N] <---/
```

- Comunicación mediante **sockets TCP**
- Protocolo de texto simple (líneas terminadas en `\n`)
- **Exclusión mutua** garantizada con `threading.Lock`
- Un **hilo por cliente** en el servidor

## 🚀 Uso

### 1. Iniciar el Servidor

```bash
python servidor.py [puerto]
```

- Por defecto usa el puerto **5000**
- Ejemplo: `python servidor.py 5000`

El servidor quedará escuchando conexiones. Para detenerlo, presiona **Ctrl+C**.

### 2. Conectar Clientes

#### Desde la Misma Máquina (Local)

```bash
python cliente.py
```

#### Desde Otra Máquina (Red)

**Primero, obtén la IP del servidor:**
```bash
python obtener_ip.py
```

**Luego, en la máquina cliente:**
```bash
python cliente.py <IP_DEL_SERVIDOR>
```

**Ejemplo:**
```bash
python cliente.py 192.168.100.98
```

O especifica puerto:
```bash
python cliente.py 192.168.100.98 5000
```

📖 **Ver guía completa:** [GUIA_CONEXION.md](GUIA_CONEXION.md)

### 3. Usar el Cliente

El cliente presenta un menú interactivo:

```
==================================================
       SISTEMA DE VENTA DE ASIENTOS
==================================================
1. Vender asiento aleatorio
2. Vender asiento específico
3. Ver asientos vendidos
4. Salir
==================================================
```

#### Opciones:

1. **Vender asiento aleatorio**: El servidor asigna el primer asiento disponible
2. **Vender asiento específico**: Permite elegir un número de asiento (1-40)
3. **Ver asientos vendidos**: Muestra una lista y representación visual de los asientos vendidos
4. **Salir**: Cierra la conexión con el servidor

## 📡 Protocolo de Comunicación

| Comando Cliente | Respuesta Servidor | Significado |
|----------------|-------------------|-------------|
| `VENDER_RANDOM` | `OK:n` | Asiento n vendido exitosamente |
| | `NO_QUEDAN` | No hay asientos disponibles |
| `VENDER_ESPECIFICO:n` | `OK:n` | Asiento n vendido |
| | `OCUPADO` | El asiento ya estaba vendido |
| | `INVALIDO` | Número fuera de rango (1-40) |
| `RESUMEN` | `VENDIDOS:[lista]` | Lista de asientos vendidos |
| `SALIR` | `ADIOS` | Cierre de conexión |

## 🔧 Requisitos

- **Python 3.6+**
- Librerías estándar (no requiere instalación adicional):
  - `socket`
  - `threading`
  - `sys`
  - `signal`

## 🧪 Prueba Rápida

### Terminal 1 - Servidor:
```bash
python servidor.py
```

### Terminal 2 - Cliente 1:
```bash
python cliente.py
```

### Terminal 3 - Cliente 2:
```bash
python cliente.py
```

Puedes ejecutar múltiples clientes simultáneamente para probar la concurrencia.

## 🧪 Pruebas de Prioridades y Concurrencia

### Pruebas Básicas
```bash
python test_sistema.py
```
Ejecuta pruebas automatizadas básicas del protocolo y funcionalidad.

### Pruebas de Prioridades FIFO
```bash
python test_prioridades.py
```
Suite completa de pruebas que demuestra:
- **Competencia simultánea**: 4 clientes intentando comprar al mismo tiempo
- **Ráfagas competitivas**: 5 clientes con múltiples peticiones rápidas
- **Orden estricto**: Verificación de que FIFO se respeta

**Qué observar en los logs del servidor:**
```
[SERVIDOR] Cliente #1 conectado desde ('127.0.0.1', 54321)
[SERVIDOR] Cliente #2 conectado desde ('127.0.0.1', 54322)
[SERVIDOR] Cliente #1 solicita: VENDER_RANDOM
[PRIORIDAD] Cliente #1 procesando (otros 1 esperando)
[SERVIDOR] Cliente #2 solicita: VENDER_RANDOM
[PRIORIDAD] Cliente #2 procesando (otros 0 esperando)
```

El mensaje `[PRIORIDAD]` indica que hubo competencia y muestra qué cliente tuvo prioridad.

## ✨ Características

### Servidor
- ✅ Gestión de 40 asientos con estado compartido
- ✅ Soporte para múltiples clientes simultáneos
- ✅ Sincronización thread-safe con `threading.Lock`
- ✅ Manejo robusto de errores y desconexiones
- ✅ Resumen final al detener el servidor
- ✅ Logs de actividad en consola

### Cliente
- ✅ Interfaz de menú intuitiva
- ✅ Representación visual de asientos
- ✅ Validación de entrada de usuario
- ✅ Manejo de desconexiones inesperadas
- ✅ Mensajes claros con emojis

## 🔒 Concurrencia y Sincronización

El servidor utiliza:
- **threading.Thread**: Un hilo por cada cliente conectado
- **threading.Lock**: Para proteger las operaciones sobre el estado compartido
- **Bloques `with self.lock`**: Garantizan exclusión mutua en operaciones críticas:
  - Venta de asientos
  - Consulta de asientos vendidos
  - Contador de clientes

Esto previene condiciones de carrera y garantiza que dos clientes no puedan comprar el mismo asiento.

### 🎯 Sistema de Prioridades FIFO

El servidor implementa un **sistema de prioridades First-In-First-Out (FIFO)** que garantiza:

1. **Orden de Procesamiento**: Cuando múltiples terminales intentan comprar simultáneamente, se procesan en el orden exacto en que llegaron las peticiones
2. **Identificación de Clientes**: Cada cliente recibe un ID único (1, 2, 3...) al conectarse
3. **Detección de Concurrencia**: El servidor registra cuando hay competencia entre clientes
4. **Estadísticas**: Al finalizar, muestra cuántas situaciones de concurrencia se detectaron

#### ¿Qué pasa si dos terminales intentan vender al mismo tiempo?

**Ejemplo:**
- Terminal 1 (Cliente #1) y Terminal 2 (Cliente #3) intentan comprar un asiento al mismo tiempo
- El `threading.Lock` garantiza que **solo uno accede al estado compartido**
- Si Cliente #1 llegó primero (aunque sea por microsegundos), su petición se procesa primero
- Cliente #3 espera hasta que Cliente #1 termine
- El servidor registra en logs: `[PRIORIDAD] Cliente #1 procesando (otros 1 esperando)`

**El orden de prioridad está determinado por:**
- Orden de llegada de la petición (FIFO estricto)
- No por el ID del cliente
- No por el tiempo de conexión

Puedes verificar esto ejecutando:
```bash
python test_prioridades.py
```

Este script simula múltiples clientes compitiendo simultáneamente y muestra claramente el orden de procesamiento en los logs del servidor.

## 📊 Ejemplo de Sesión

```
$ python cliente.py
==================================================
  CLIENTE - SISTEMA DE VENTA DE ASIENTOS
==================================================
✓ Conectado al servidor localhost:5000

==================================================
       SISTEMA DE VENTA DE ASIENTOS
==================================================
1. Vender asiento aleatorio
2. Vender asiento específico
3. Ver asientos vendidos
4. Salir
==================================================

Selecciona una opción (1-4): 1

--- Venta Aleatoria ---
✓ ¡Asiento 1 vendido exitosamente!

Selecciona una opción (1-4): 2

--- Venta Específica ---
Ingresa el número de asiento (1-40): 15
✓ ¡Asiento 15 vendido exitosamente!

Selecciona una opción (1-4): 3

--- Asientos Vendidos ---
Total vendidos: 2
Asientos: [1, 15]

Representación visual:
[X 1] [_ 2] [_ 3] [_ 4] [_ 5] [_ 6] [_ 7] [_ 8] [_ 9] [_10] 
[_11] [_12] [_13] [_14] [X15] [_16] [_17] [_18] [_19] [_20] 
[_21] [_22] [_23] [_24] [_25] [_26] [_27] [_28] [_29] [_30] 
[_31] [_32] [_33] [_34] [_35] [_36] [_37] [_38] [_39] [_40] 

[X] = Vendido  [_] = Disponible
```

## � Configuración de Firewall (Conexiones en Red)

Si estás conectando desde otra máquina y obtienes "Connection refused":

**Linux (Fedora/RHEL):**
```bash
sudo firewall-cmd --zone=public --add-port=5000/tcp --permanent
sudo firewall-cmd --reload
```

**Linux (Ubuntu/Debian):**
```bash
sudo ufw allow 5000/tcp
```

**Windows:**
```powershell
New-NetFirewallRule -DisplayName "Servidor Asientos" -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

Ver guía completa de solución de problemas en [GUIA_CONEXION.md](GUIA_CONEXION.md)

## �🛑 Detener el Servidor

Presiona **Ctrl+C** en la terminal del servidor. Se mostrará un resumen final:

```
[SERVIDOR] Deteniendo servidor...

============================================================
RESUMEN FINAL DEL SERVIDOR
============================================================
Total de asientos vendidos: 25/40
Asientos vendidos: [1, 2, 5, 7, 10, 12, 15, 18, ...]
============================================================
```

## 📝 Notas de Implementación

- Los asientos se numeran del **1 al 40** (no desde 0)
- El servidor usa `socket.settimeout(1.0)` para permitir interrupciones limpias
- Los hilos de clientes son `daemon=True` para que terminen automáticamente
- Se usa `socket.makefile()` para facilitar la lectura/escritura de texto
- El protocolo es **case-sensitive** (comandos en MAYÚSCULAS)

## 🐛 Solución de Problemas

### "No se pudo conectar al servidor"
- Verifica que el servidor esté ejecutándose
- Comprueba que el puerto no esté bloqueado por firewall
- Confirma que host y puerto sean correctos

### "Error de comunicación"
- El servidor puede haberse detenido
- Problemas de red
- El cliente intentará reconectar automáticamente

### Puerto en uso
- Cambia el puerto: `python servidor.py 5001`
- O detén el proceso que usa el puerto 5000

## 📚 Estructura del Código

```
terminales/
├── servidor.py                  # Servidor central con threading y prioridades FIFO
├── cliente.py                   # Cliente con interfaz de menú
├── obtener_ip.py                # Script para obtener IP del servidor
├── test_sistema.py              # Pruebas básicas automatizadas
├── test_prioridades.py          # Pruebas del sistema de prioridades
├── test_bloqueo.py              # Demostración de bloqueo de asientos
├── ejemplos.py                  # Ejemplos de uso programático
├── README.md                    # Documentación principal
├── GUIA_CONEXION.md             # Guía completa de conexión en red
└── DEMOSTRACION_PRIORIDADES.md  # Documentación detallada de prioridades
```

## 👨‍💻 Autor

Práctica escolar de programación distribuida y concurrente.

## 📄 Licencia

Código educativo de libre uso para fines académicos.
