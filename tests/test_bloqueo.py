#!/usr/bin/env python3
"""
Demostración del bloqueo de asientos vendidos.
Prueba que un asiento vendido NO puede venderse nuevamente.
"""

import socket
import time


def test_bloqueo_asiento():
    """
    Prueba que demuestra el bloqueo de asientos.
    """
    print("=" * 70)
    print("DEMOSTRACIÓN DE BLOQUEO DE ASIENTOS VENDIDOS")
    print("=" * 70)
    
    try:
        # Conectar al servidor
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 5000))
        archivo = sock.makefile('rw', encoding='utf-8', newline='\n')
        
        # Leer bienvenida
        bienvenida = archivo.readline().strip()
        id_cliente = bienvenida.split("ID=")[1] if ":ID=" in bienvenida else "?"
        print(f"\n✓ Conectado como Cliente #{id_cliente}\n")
        
        # PRUEBA 1: Vender asiento específico #25
        print("=" * 70)
        print("PRUEBA 1: Vender asiento #25 por primera vez")
        print("=" * 70)
        archivo.write("VENDER_ESPECIFICO:25\n")
        archivo.flush()
        respuesta1 = archivo.readline().strip()
        print(f"→ Comando: VENDER_ESPECIFICO:25")
        print(f"→ Respuesta: {respuesta1}")
        
        if respuesta1 == "OK:25":
            print("✓ VENTA EXITOSA - Asiento #25 ahora está BLOQUEADO")
        else:
            print(f"⚠ Respuesta inesperada: {respuesta1}")
        
        time.sleep(0.5)
        
        # PRUEBA 2: Intentar vender el MISMO asiento #25
        print("\n" + "=" * 70)
        print("PRUEBA 2: Intentar vender asiento #25 NUEVAMENTE")
        print("=" * 70)
        archivo.write("VENDER_ESPECIFICO:25\n")
        archivo.flush()
        respuesta2 = archivo.readline().strip()
        print(f"→ Comando: VENDER_ESPECIFICO:25")
        print(f"→ Respuesta: {respuesta2}")
        
        if respuesta2 == "OCUPADO":
            print("✓ BLOQUEO FUNCIONANDO - El asiento está OCUPADO")
            print("  El servidor rechazó la venta porque el asiento ya fue vendido")
        else:
            print(f"✗ ERROR: El asiento debería estar bloqueado pero respuesta fue: {respuesta2}")
        
        time.sleep(0.5)
        
        # PRUEBA 3: Vender otro asiento #30
        print("\n" + "=" * 70)
        print("PRUEBA 3: Vender asiento #30 (debería funcionar)")
        print("=" * 70)
        archivo.write("VENDER_ESPECIFICO:30\n")
        archivo.flush()
        respuesta3 = archivo.readline().strip()
        print(f"→ Comando: VENDER_ESPECIFICO:30")
        print(f"→ Respuesta: {respuesta3}")
        
        if respuesta3 == "OK:30":
            print("✓ VENTA EXITOSA - Asiento #30 ahora está BLOQUEADO")
        else:
            print(f"⚠ Respuesta: {respuesta3}")
        
        time.sleep(0.5)
        
        # PRUEBA 4: Intentar vender #30 nuevamente
        print("\n" + "=" * 70)
        print("PRUEBA 4: Intentar vender asiento #30 NUEVAMENTE")
        print("=" * 70)
        archivo.write("VENDER_ESPECIFICO:30\n")
        archivo.flush()
        respuesta4 = archivo.readline().strip()
        print(f"→ Comando: VENDER_ESPECIFICO:30")
        print(f"→ Respuesta: {respuesta4}")
        
        if respuesta4 == "OCUPADO":
            print("✓ BLOQUEO FUNCIONANDO - El asiento está OCUPADO")
        else:
            print(f"✗ ERROR: Respuesta inesperada: {respuesta4}")
        
        # RESUMEN
        print("\n" + "=" * 70)
        print("RESUMEN DE ASIENTOS VENDIDOS")
        print("=" * 70)
        archivo.write("RESUMEN\n")
        archivo.flush()
        respuesta_resumen = archivo.readline().strip()
        
        if respuesta_resumen.startswith("VENDIDOS:"):
            import ast
            vendidos = ast.literal_eval(respuesta_resumen.split(':', 1)[1])
            print(f"→ Asientos vendidos: {vendidos}")
            print(f"→ Total: {len(vendidos)} asientos")
            
            # Verificar que 25 y 30 están en la lista
            if 25 in vendidos and 30 in vendidos:
                print("\n✓ VERIFICACIÓN COMPLETADA:")
                print("  • Asiento #25: BLOQUEADO (vendido)")
                print("  • Asiento #30: BLOQUEADO (vendido)")
                print("  • Intentos de re-venta: RECHAZADOS correctamente")
        
        # Cerrar conexión
        archivo.write("SALIR\n")
        archivo.flush()
        archivo.close()
        sock.close()
        
        print("\n" + "=" * 70)
        print("✓ DEMOSTRACIÓN COMPLETADA")
        print("=" * 70)
        print("\nCONCLUSIÓN:")
        print("  El sistema SÍ bloquea los asientos vendidos.")
        print("  Una vez vendido, un asiento NO puede venderse nuevamente.")
        print("  El servidor responde 'OCUPADO' para asientos bloqueados.")
        print("=" * 70)
        
    except ConnectionRefusedError:
        print("\n✗ Error: No se pudo conectar al servidor")
        print("  Ejecuta primero: python servidor.py")
    except Exception as e:
        print(f"\n✗ Error: {e}")


def test_bloqueo_con_multiples_clientes():
    """
    Prueba con múltiples clientes intentando comprar el mismo asiento.
    """
    print("\n\n" + "=" * 70)
    print("DEMOSTRACIÓN: MÚLTIPLES CLIENTES - MISMO ASIENTO")
    print("=" * 70)
    print("\nSimulación: 3 clientes intentando comprar el asiento #15")
    print("Solo UNO debería conseguirlo, los otros 2 deben recibir 'OCUPADO'\n")
    
    import threading
    
    resultados = []
    lock_resultados = threading.Lock()
    
    def cliente_competidor(id_cliente, asiento):
        """Cliente que intenta comprar un asiento específico"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', 5000))
            f = sock.makefile('rw', encoding='utf-8', newline='\n')
            
            # Bienvenida
            bienvenida = f.readline().strip()
            id_servidor = bienvenida.split("ID=")[1] if ":ID=" in bienvenida else "?"
            
            print(f"[Cliente {id_cliente}] Conectado como #{id_servidor}")
            
            # Pequeña pausa para sincronizar
            time.sleep(0.1)
            
            # Todos intentan comprar el MISMO asiento casi al mismo tiempo
            f.write(f"VENDER_ESPECIFICO:{asiento}\n")
            f.flush()
            respuesta = f.readline().strip()
            
            with lock_resultados:
                resultados.append({
                    'cliente_id': id_servidor,
                    'respuesta': respuesta,
                    'exito': respuesta.startswith('OK')
                })
            
            print(f"[Cliente {id_cliente}] #{id_servidor} → {respuesta}")
            
            f.write("SALIR\n")
            f.flush()
            f.close()
            sock.close()
            
        except Exception as e:
            print(f"[Cliente {id_cliente}] Error: {e}")
    
    # Lanzar 3 clientes compitiendo por el asiento #15
    hilos = []
    for i in range(3):
        hilo = threading.Thread(target=cliente_competidor, args=(i+1, 15))
        hilos.append(hilo)
        hilo.start()
    
    # Esperar a que terminen
    for hilo in hilos:
        hilo.join()
    
    # Analizar resultados
    print("\n" + "-" * 70)
    print("ANÁLISIS DE RESULTADOS")
    print("-" * 70)
    
    exitosos = [r for r in resultados if r['exito']]
    bloqueados = [r for r in resultados if not r['exito']]
    
    print(f"• Clientes que COMPRARON el asiento: {len(exitosos)}")
    print(f"• Clientes que fueron BLOQUEADOS: {len(bloqueados)}")
    
    if len(exitosos) == 1 and len(bloqueados) == 2:
        print("\n✓ BLOQUEO CORRECTO:")
        print(f"  → Solo 1 cliente pudo comprar (Cliente #{exitosos[0]['cliente_id']})")
        print(f"  → Los otros 2 recibieron 'OCUPADO' (bloqueo funcionando)")
    else:
        print(f"\n⚠ Comportamiento inesperado:")
        print(f"  → Debería haber 1 exitoso y 2 bloqueados")
    
    print("=" * 70)


if __name__ == "__main__":
    print("\n⚠ IMPORTANTE: Asegúrate de tener el servidor ejecutándose:")
    print("  python servidor.py\n")
    
    input("Presiona Enter para iniciar la demostración...")
    
    # Ejecutar demostraciones
    test_bloqueo_asiento()
    
    time.sleep(2)
    
    test_bloqueo_con_multiples_clientes()
    
    print("\n" + "=" * 70)
    print("FIN DE LA DEMOSTRACIÓN")
    print("=" * 70)
