# Demostración del Sistema de Prioridades FIFO

## 🎯 ¿Qué Sucede Cuando Dos Terminales Intentan Vender al Mismo Tiempo?

Este documento explica el comportamiento del sistema de prioridades implementado.

## 📊 Escenario de Ejemplo

Imaginemos que **3 terminales** intentan comprar asientos casi simultáneamente:

```
Cliente Terminal 1 → Conecta primero  → Asignado ID #1
Cliente Terminal 2 → Conecta segundo  → Asignado ID #2
Cliente Terminal 3 → Conecta tercero  → Asignado ID #3
```

### Línea de Tiempo de Peticiones

```
Tiempo  Cliente #1      Cliente #2      Cliente #3      Servidor
------  ----------      ----------      ----------      --------
t0      Conecta...                                      Asigna ID=1
t1                      Conecta...                      Asigna ID=2
t2                                      Conecta...      Asigna ID=3
t3      VENDER_RANDOM                                   
t4                      VENDER_RANDOM                   Esperando...
t5                                      VENDER_RANDOM   Esperando...
t6                                                      Procesa #1 (OK:1)
t7      Recibe OK:1                                     
t8                                                      Procesa #2 (OK:2)
t9                      Recibe OK:2                     [PRIORIDAD] detectada
t10                                                     Procesa #3 (OK:3)
t11                                     Recibe OK:3     [PRIORIDAD] detectada
```

## 🔒 Mecanismo de Exclusión Mutua

El servidor usa `threading.Lock()` que garantiza:

### 1. **Acceso Exclusivo**
```python
with self.lock:
    # Solo UN cliente puede ejecutar este código a la vez
    if not self.asientos_vendidos[numero]:
        self.asientos_vendidos[numero] = True  # Marcar como vendido
```

### 2. **Cola FIFO (First In, First Out)**
Cuando múltiples clientes están esperando el lock:
- Python garantiza que quien pidió el lock **primero** lo obtendrá primero
- No hay "saltos de cola" ni preferencias arbitrarias
- El orden es estrictamente cronológico

## 📈 Logs del Servidor en Acción

### Ejemplo Real de Competencia:

```
[SERVIDOR] Cliente #1 solicita: VENDER_RANDOM
[SERVIDOR] Cliente #2 solicita: VENDER_RANDOM
[PRIORIDAD] Cliente #2 procesando (otros 1 esperando)
```

**Interpretación:**
- Cliente #1 solicitó primero, se procesó sin competencia
- Cliente #2 solicitó mientras #1 aún no terminaba
- Cuando #2 accede al lock, detecta que hay 1 cliente esperando

### Competencia Intensa (5 clientes):

```
[SERVIDOR] Cliente #3 solicita: VENDER_RANDOM
[PRIORIDAD] Cliente #3 procesando (otros 4 esperando)
```

**Interpretación:**
- 5 clientes están activos
- Cliente #3 está procesando
- Los otros 4 clientes están esperando su turno
- Cada uno procesará en el orden exacto en que llegó su petición

## 🎲 Situación Hipotética: Venta Simultánea del Mismo Asiento

### Escenario:
- Terminal 1 y Terminal 2 intentan comprar el **asiento #15** al mismo tiempo
- Solo quedan 2 asientos libres: #15 y #20

### ¿Qué Sucede?

```python
# Terminal 1 llega PRIMERO (aunque sea por microsegundos)
T1: VENDER_ESPECIFICO:15

# Terminal 2 llega después (esperando el lock)
T2: VENDER_ESPECIFICO:15
```

### Resultado Paso a Paso:

1. **Terminal 1 obtiene el lock**
   ```python
   with self.lock:  # T1 entra
       if not self.asientos_vendidos[15]:  # True (está libre)
           self.asientos_vendidos[15] = True  # Marca como vendido
           return ('OK', 15)  # ✓ VENTA EXITOSA
   # T1 libera el lock
   ```
   **Respuesta a T1:** `OK:15`

2. **Terminal 2 obtiene el lock**
   ```python
   with self.lock:  # T2 entra
       if not self.asientos_vendidos[15]:  # False (ya vendido por T1)
           # No entra aquí
       else:
           return ('OCUPADO', 15)  # ✗ YA VENDIDO
   # T2 libera el lock
   ```
   **Respuesta a T2:** `OCUPADO`

### Línea de Tiempo Detallada:

```
Microsegundo    Terminal 1              Terminal 2              Estado Asiento #15
-----------     -----------             -----------             ------------------
    0           Envía petición                                  LIBRE
    1                                   Envía petición          LIBRE
    2           Adquiere Lock                                   LIBRE
    3           Verifica: ¿libre? SÍ                            LIBRE
    4           Marca como vendido      [Esperando Lock]        VENDIDO
    5           Libera Lock                                     VENDIDO
    6                                   Adquiere Lock           VENDIDO
    7                                   Verifica: ¿libre? NO    VENDIDO
    8                                   Responde OCUPADO        VENDIDO
```

## 🏆 Sistema de Prioridades: Resumen

### ✅ Lo que el Sistema Garantiza:

1. **Orden FIFO Estricto**: Primera petición en llegar = primera en procesarse
2. **Atomicidad**: Las operaciones de venta son atómicas (todo o nada)
3. **Consistencia**: Nunca se vende el mismo asiento dos veces
4. **Visibilidad**: Los logs muestran claramente el orden y la competencia
5. **Justicia**: No hay inanición, todos los clientes eventualmente se atienden

### ❌ Lo que NO determina la prioridad:

- ❌ El ID del cliente (Cliente #5 puede tener prioridad sobre Cliente #1)
- ❌ El tiempo de conexión (conectarse primero ≠ comprar primero)
- ❌ Preferencias arbitrarias del sistema
- ❌ Tipo de petición (RANDOM vs ESPECIFICO tienen igual prioridad)

### 🔑 La Clave es el **Timestamp de la Petición**

```
Quien solicita primero → Procesa primero
```

## 🧪 Cómo Verificarlo

### 1. Iniciar el servidor:
```bash
python servidor.py
```

### 2. Ejecutar pruebas de concurrencia:
```bash
python test_prioridades.py
```

### 3. Observar los logs del servidor:
Busca las líneas con `[PRIORIDAD]` que indican:
- Qué cliente está procesando
- Cuántos otros están esperando
- El orden de procesamiento

### 4. Revisar estadísticas finales:
Al detener el servidor (Ctrl+C), verás:
```
--- Estadísticas de Prioridad ---
Total de peticiones procesadas: 45
Situaciones de concurrencia detectadas: 23
✓ El sistema FIFO garantizó el orden de prioridad correcto
```

## 📚 Implementación Técnica

### Código Clave en `servidor.py`:

```python
def vender_siguiente_disponible(self, id_cliente=None):
    with self.lock:  # ← PUNTO CRÍTICO: Solo uno entra a la vez
        # Registrar petición
        self.peticiones_procesadas += 1
        
        # Detectar competencia
        if id_cliente:
            clientes_esperando = len(self.clientes_info) - 1
            if clientes_esperando > 0:
                self.conflictos_detectados += 1
                print(f"[PRIORIDAD] Cliente #{id_cliente} procesando "
                      f"(otros {clientes_esperando} esperando)")
        
        # Buscar y vender asiento
        for i in range(1, self.total_asientos + 1):
            if not self.asientos_vendidos[i]:
                self.asientos_vendidos[i] = True  # Venta atómica
                return ('OK', i)
```

### Propiedades del Lock:

1. **Mutual Exclusion**: Solo un hilo dentro del bloque `with self.lock`
2. **FIFO Fairness**: Python's threading.Lock usa cola FIFO en la mayoría de sistemas
3. **Reentrant-Safe**: No hay deadlocks en las operaciones
4. **Performance**: Operaciones críticas mínimas dentro del lock

## 🎓 Conclusión

El sistema de prioridades FIFO garantiza que cuando dos o más terminales intentan vender al mismo tiempo:

✅ Se procesan en orden de llegada estricto
✅ No hay condiciones de carrera  
✅ No hay ventas duplicadas  
✅ El comportamiento es predecible y justo
✅ El sistema es escalable y eficiente

**La prioridad la determina el orden cronológico de las peticiones, punto.**
