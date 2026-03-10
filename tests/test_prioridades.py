#!/usr/bin/env python3
"""
Script de prueba para demostrar el sistema de prioridades FIFO.
Simula múltiples clientes intentando comprar al mismo tiempo.
"""

import socket
import threading
import time
import random


def cliente_competidor(id_simulacion, num_intentos=5, delay_inicial=0):
    """
    Simula un cliente que intenta comprar asientos.
    
    Args:
        id_simulacion: Identificador para mostrar en logs
        num_intentos: Número de compras a intentar
        delay_inicial: Retardo antes de comenzar (para sincronizar)
    """
    time.sleep(delay_inicial)
    
    try:
        # Conectar al servidor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 5000))
        archivo = sock.makefile('rw', encoding='utf-8', newline='\n')
        
        # Leer bienvenida y obtener ID del servidor
        bienvenida = archivo.readline().strip()
        id_servidor = None
        if ":ID=" in bienvenida:
            id_servidor = bienvenida.split("ID=")[1]
        
        print(f"[Simulación {id_simulacion}] Conectado como Cliente #{id_servidor}")
        
        # Realizar intentos de compra
        for i in range(num_intentos):
            # Todos los clientes intentan comprar "al mismo tiempo"
            time.sleep(0.001)  # Mínimo delay para crear competencia
            
            archivo.write("VENDER_RANDOM\n")
            archivo.flush()
            respuesta = archivo.readline().strip()
            
            if respuesta.startswith("OK:"):
                asiento = respuesta.split(':')[1]
                print(f"[Simulación {id_simulacion}] Cliente #{id_servidor} → Compró asiento {asiento}")
            else:
                print(f"[Simulación {id_simulacion}] Cliente #{id_servidor} → {respuesta}")
        
        # Despedirse
        archivo.write("SALIR\n")
        archivo.flush()
        archivo.close()
        sock.close()
        
        print(f"[Simulación {id_simulacion}] Cliente #{id_servidor} desconectado")
        
    except Exception as e:
        print(f"[Simulación {id_simulacion}] Error: {e}")


def prueba_competencia_simultanea():
    """
    Prueba con clientes que intentan comprar exactamente al mismo tiempo.
    Demuestra que el servidor procesa en orden FIFO.
    """
    print("=" * 70)
    print("PRUEBA DE PRIORIDADES: COMPETENCIA SIMULTÁNEA")
    print("=" * 70)
    print("\nEsta prueba simula 4 clientes intentando comprar al mismo tiempo.")
    print("El servidor debe procesarlos en orden de llegada (FIFO).\n")
    
    # Crear hilos que se inician casi simultáneamente
    hilos = []
    num_clientes = 4
    intentos_por_cliente = 3
    
    print(f"Iniciando {num_clientes} clientes con {intentos_por_cliente} intentos cada uno...\n")
    
    # Iniciar todos los clientes casi al mismo tiempo
    for i in range(num_clientes):
        hilo = threading.Thread(
            target=cliente_competidor,
            args=(i+1, intentos_por_cliente, 0.01 * i)  # Pequeño delay escalonado
        )
        hilos.append(hilo)
        hilo.start()
    
    # Esperar a que todos terminen
    for hilo in hilos:
        hilo.join()
    
    print("\n✓ Prueba completada")
    print("\nObserva los logs del servidor para ver:")
    print("  - Los IDs de cliente asignados en orden")
    print("  - Los mensajes [PRIORIDAD] cuando hay competencia")
    print("  - Qué cliente procesó cada petición")


def prueba_rafaga_competitiva():
    """
    Prueba con ráfagas de peticiones competitivas.
    """
    print("\n" + "=" * 70)
    print("PRUEBA DE PRIORIDADES: RÁFAGAS COMPETITIVAS")
    print("=" * 70)
    print("\nSimula 5 clientes enviando ráfagas de peticiones simultáneas.")
    print("Demuestra que el lock garantiza orden FIFO incluso bajo presión.\n")
    
    hilos = []
    num_clientes = 5
    intentos_por_cliente = 4
    
    print(f"Iniciando {num_clientes} clientes con {intentos_por_cliente} intentos cada uno...\n")
    
    for i in range(num_clientes):
        hilo = threading.Thread(
            target=cliente_competidor,
            args=(i+1, intentos_por_cliente, 0.005 * i)
        )
        hilos.append(hilo)
        hilo.start()
    
    for hilo in hilos:
        hilo.join()
    
    print("\n✓ Prueba completada")


def prueba_orden_estricto():
    """
    Prueba que verifica el orden estricto de procesamiento.
    """
    print("\n" + "=" * 70)
    print("PRUEBA DE PRIORIDADES: VERIFICACIÓN DE ORDEN ESTRICTO")
    print("=" * 70)
    print("\n3 clientes conectan en orden estricto (1, 2, 3).")
    print("Cada uno hace 2 compras. Verifica el orden en los logs del servidor.\n")
    
    resultados = []
    lock_resultados = threading.Lock()
    
    def cliente_con_orden(id_sim, orden_esperado):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 5000))
            archivo = sock.makefile('rw', encoding='utf-8', newline='\n')
            
            bienvenida = archivo.readline().strip()
            id_servidor = bienvenida.split("ID=")[1] if ":ID=" in bienvenida else "?"
            
            print(f"[Cliente {id_sim}] Conectado como #{id_servidor} (esperado orden {orden_esperado})")
            
            # Hacer compras
            for i in range(2):
                archivo.write("VENDER_RANDOM\n")
                archivo.flush()
                respuesta = archivo.readline().strip()
                
                if respuesta.startswith("OK:"):
                    asiento = respuesta.split(':')[1]
                    with lock_resultados:
                        resultados.append({
                            'cliente': id_servidor,
                            'orden': orden_esperado,
                            'asiento': asiento
                        })
                    print(f"[Cliente {id_sim}] #{id_servidor} compró asiento {asiento}")
                
                time.sleep(0.01)
            
            archivo.write("SALIR\n")
            archivo.flush()
            archivo.close()
            sock.close()
            
        except Exception as e:
            print(f"[Cliente {id_sim}] Error: {e}")
    
    # Conectar clientes en orden estricto
    hilos = []
    for i in range(3):
        hilo = threading.Thread(target=cliente_con_orden, args=(i+1, i+1))
        hilos.append(hilo)
        hilo.start()
        time.sleep(0.1)  # Delay para garantizar orden de conexión
    
    for hilo in hilos:
        hilo.join()
    
    print("\n--- Resumen de Orden de Compras ---")
    for idx, r in enumerate(resultados, 1):
        print(f"  Operación #{idx}: Cliente #{r['cliente']} → Asiento {r['asiento']}")
    
    print("\n✓ Prueba completada")


def main():
    print("=" * 70)
    print("SUITE DE PRUEBAS DE SISTEMA DE PRIORIDADES FIFO")
    print("=" * 70)
    print("\n⚠ IMPORTANTE: Asegúrate de tener el servidor ejecutándose:")
    print("  python servidor.py\n")
    
    input("Presiona Enter para comenzar las pruebas...")
    
    # Ejecutar pruebas
    prueba_competencia_simultanea()
    time.sleep(2)
    
    prueba_rafaga_competitiva()
    time.sleep(2)
    
    prueba_orden_estricto()
    
    print("\n" + "=" * 70)
    print("TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 70)
    print("\nRevisa los logs del servidor para ver:")
    print("  ✓ Asignación de IDs de cliente")
    print("  ✓ Mensajes [PRIORIDAD] indicando competencia")
    print("  ✓ Orden de procesamiento de peticiones")
    print("  ✓ Estadísticas de concurrencia en el resumen final")


if __name__ == "__main__":
    main()
