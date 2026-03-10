#!/usr/bin/env python3
"""
Ejemplo de uso de la API del cliente de asientos.
Muestra cómo usar las clases en otros programas.
"""

from cliente import ClienteAsientos
import time


def ejemplo_uso_basico():
    """
    Ejemplo básico de uso del cliente programáticamente.
    """
    print("=== Ejemplo de Uso Básico ===\n")
    
    # Crear instancia del cliente
    cliente = ClienteAsientos(host='localhost', puerto=5000)
    
    # Conectar al servidor
    if not cliente.conectar():
        print("No se pudo conectar. Asegúrate de ejecutar el servidor primero.")
        return
    
    print("\n1. Comprando 5 asientos aleatorios...\n")
    for i in range(5):
        respuesta = cliente.enviar_comando("VENDER_RANDOM")
        if respuesta and respuesta.startswith("OK:"):
            numero = respuesta.split(':')[1]
            print(f"   ✓ Asiento {numero} comprado")
        time.sleep(0.2)
    
    print("\n2. Comprando asientos específicos (25, 30, 35)...\n")
    for num in [25, 30, 35]:
        respuesta = cliente.enviar_comando(f"VENDER_ESPECIFICO:{num}")
        if respuesta:
            if respuesta.startswith("OK:"):
                print(f"   ✓ Asiento {num} comprado")
            elif respuesta == "OCUPADO":
                print(f"   ⚠ Asiento {num} ya estaba ocupado")
        time.sleep(0.2)
    
    print("\n3. Consultando asientos vendidos...\n")
    respuesta = cliente.enviar_comando("RESUMEN")
    if respuesta and respuesta.startswith("VENDIDOS:"):
        lista_str = respuesta.split(':', 1)[1]
        import ast
        vendidos = ast.literal_eval(lista_str)
        print(f"   Total vendidos: {len(vendidos)}")
        print(f"   Números: {vendidos[:10]}..." if len(vendidos) > 10 else f"   Números: {vendidos}")
    
    print("\n4. Cerrando conexión...\n")
    cliente.enviar_comando("SALIR")
    cliente.cerrar()
    
    print("✓ Ejemplo completado\n")


def ejemplo_manejo_errores():
    """
    Ejemplo de manejo de errores comunes.
    """
    print("=== Ejemplo de Manejo de Errores ===\n")
    
    cliente = ClienteAsientos(host='localhost', puerto=5000)
    
    if not cliente.conectar():
        return
    
    print("1. Intentando comprar asiento inválido (fuera de rango)...")
    respuesta = cliente.enviar_comando("VENDER_ESPECIFICO:100")
    print(f"   Respuesta: {respuesta}\n")
    
    print("2. Intentando comprar el mismo asiento dos veces...")
    respuesta1 = cliente.enviar_comando("VENDER_ESPECIFICO:10")
    print(f"   Primera compra: {respuesta1}")
    respuesta2 = cliente.enviar_comando("VENDER_ESPECIFICO:10")
    print(f"   Segunda compra: {respuesta2}\n")
    
    print("3. Enviando comando inválido...")
    respuesta = cliente.enviar_comando("COMANDO_INVALIDO")
    print(f"   Respuesta: {respuesta}\n")
    
    cliente.enviar_comando("SALIR")
    cliente.cerrar()
    
    print("✓ Ejemplo completado\n")


def ejemplo_compra_masiva():
    """
    Ejemplo de compra masiva de asientos.
    """
    print("=== Ejemplo de Compra Masiva ===\n")
    
    cliente = ClienteAsientos(host='localhost', puerto=5000)
    
    if not cliente.conectar():
        return
    
    print("Comprando asientos hasta que no quede ninguno disponible...\n")
    
    contador = 0
    while True:
        respuesta = cliente.enviar_comando("VENDER_RANDOM")
        if respuesta == "NO_QUEDAN":
            print(f"\n✓ Se compraron {contador} asientos")
            print("⚠ Ya no quedan asientos disponibles")
            break
        elif respuesta and respuesta.startswith("OK:"):
            contador += 1
            numero = respuesta.split(':')[1]
            if contador % 5 == 0:
                print(f"   Progreso: {contador} asientos comprados (último: {numero})")
        else:
            print(f"   Error inesperado: {respuesta}")
            break
        
        time.sleep(0.05)  # Pequeña pausa para no saturar
    
    cliente.enviar_comando("SALIR")
    cliente.cerrar()
    
    print("\n✓ Ejemplo completado\n")


if __name__ == "__main__":
    print("=" * 60)
    print("EJEMPLOS DE USO DEL SISTEMA DE VENTA DE ASIENTOS")
    print("=" * 60)
    print("\nAsegúrate de tener el servidor ejecutándose:")
    print("  python servidor.py\n")
    
    input("Presiona Enter para continuar con los ejemplos...")
    
    # Ejecutar ejemplos
    ejemplo_uso_basico()
    time.sleep(1)
    
    ejemplo_manejo_errores()
    time.sleep(1)
    
    # Descomentar si quieres probar la compra masiva
    # (esto comprará todos los asientos disponibles)
    # respuesta = input("\n¿Ejecutar ejemplo de compra masiva? (s/n): ")
    # if respuesta.lower() == 's':
    #     ejemplo_compra_masiva()
    
    print("=" * 60)
    print("FIN DE LOS EJEMPLOS")
    print("=" * 60)
