#!/usr/bin/env python3
"""
Script de prueba automatizada para el sistema de venta de asientos.
Simula operaciones de compra sin interacción del usuario.
"""

import socket
import time


def prueba_basica():
    """
    Realiza una serie de pruebas básicas del sistema.
    """
    print("=" * 60)
    print("PRUEBA AUTOMATIZADA DEL SISTEMA DE VENTA DE ASIENTOS")
    print("=" * 60)
    
    try:
        # Conectar al servidor
        print("\n[TEST 1] Conectando al servidor...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 5000))
        archivo = sock.makefile('rw', encoding='utf-8', newline='\n')
        
        # Leer bienvenida
        bienvenida = archivo.readline().strip()
        print(f"✓ Conectado. Mensaje: {bienvenida}")
        
        # Prueba 1: Vender asiento aleatorio
        print("\n[TEST 2] Vendiendo asiento aleatorio...")
        archivo.write("VENDER_RANDOM\n")
        archivo.flush()
        respuesta = archivo.readline().strip()
        print(f"✓ Respuesta: {respuesta}")
        
        # Prueba 2: Vender asiento específico
        print("\n[TEST 3] Vendiendo asiento específico (15)...")
        archivo.write("VENDER_ESPECIFICO:15\n")
        archivo.flush()
        respuesta = archivo.readline().strip()
        print(f"✓ Respuesta: {respuesta}")
        
        # Prueba 3: Intentar vender asiento ya vendido
        print("\n[TEST 4] Intentando vender asiento 15 nuevamente...")
        archivo.write("VENDER_ESPECIFICO:15\n")
        archivo.flush()
        respuesta = archivo.readline().strip()
        print(f"✓ Respuesta: {respuesta} (Debería ser OCUPADO)")
        
        # Prueba 4: Vender asiento inválido
        print("\n[TEST 5] Intentando vender asiento inválido (99)...")
        archivo.write("VENDER_ESPECIFICO:99\n")
        archivo.flush()
        respuesta = archivo.readline().strip()
        print(f"✓ Respuesta: {respuesta} (Debería ser INVALIDO)")
        
        # Prueba 5: Obtener resumen
        print("\n[TEST 6] Solicitando resumen de asientos vendidos...")
        archivo.write("RESUMEN\n")
        archivo.flush()
        respuesta = archivo.readline().strip()
        print(f"✓ Respuesta: {respuesta}")
        
        # Prueba 6: Comando desconocido
        print("\n[TEST 7] Enviando comando desconocido...")
        archivo.write("COMANDO_INVENTADO\n")
        archivo.flush()
        respuesta = archivo.readline().strip()
        print(f"✓ Respuesta: {respuesta} (Debería ser COMANDO_DESCONOCIDO)")
        
        # Despedida
        print("\n[TEST 8] Cerrando conexión...")
        archivo.write("SALIR\n")
        archivo.flush()
        respuesta = archivo.readline().strip()
        print(f"✓ Respuesta: {respuesta}")
        
        archivo.close()
        sock.close()
        
        print("\n" + "=" * 60)
        print("✓ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print("=" * 60)
        
    except ConnectionRefusedError:
        print("✗ Error: No se pudo conectar al servidor")
        print("  Asegúrate de que el servidor esté ejecutándose:")
        print("  python servidor.py")
    except Exception as e:
        print(f"✗ Error durante las pruebas: {e}")
        import traceback
        traceback.print_exc()


def prueba_concurrencia():
    """
    Prueba con múltiples clientes simultáneos.
    """
    import threading
    
    print("\n" + "=" * 60)
    print("PRUEBA DE CONCURRENCIA - 5 CLIENTES SIMULTÁNEOS")
    print("=" * 60)
    
    def cliente_concurrente(id_cliente, num_operaciones=3):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 5000))
            archivo = sock.makefile('rw', encoding='utf-8', newline='\n')
            
            # Leer bienvenida
            archivo.readline()
            print(f"[Cliente {id_cliente}] Conectado")
            
            # Realizar operaciones
            for i in range(num_operaciones):
                archivo.write("VENDER_RANDOM\n")
                archivo.flush()
                respuesta = archivo.readline().strip()
                print(f"[Cliente {id_cliente}] Operación {i+1}: {respuesta}")
                time.sleep(0.1)  # Pequeña pausa
            
            # Despedirse
            archivo.write("SALIR\n")
            archivo.flush()
            archivo.readline()
            
            archivo.close()
            sock.close()
            print(f"[Cliente {id_cliente}] Desconectado")
            
        except Exception as e:
            print(f"[Cliente {id_cliente}] Error: {e}")
    
    # Crear y lanzar hilos
    hilos = []
    for i in range(5):
        hilo = threading.Thread(target=cliente_concurrente, args=(i+1,))
        hilos.append(hilo)
        hilo.start()
        time.sleep(0.05)  # Pequeño delay entre inicios
    
    # Esperar a que terminen todos
    for hilo in hilos:
        hilo.join()
    
    print("\n✓ Prueba de concurrencia completada")


if __name__ == "__main__":
    # Ejecutar prueba básica
    prueba_basica()
    
    # Pequeña pausa
    time.sleep(1)
    
    # Ejecutar prueba de concurrencia
    prueba_concurrencia()
    
    print("\n" + "=" * 60)
    print("FIN DE LAS PRUEBAS")
    print("=" * 60)
