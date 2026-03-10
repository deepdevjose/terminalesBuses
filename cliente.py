#!/usr/bin/env python3
"""
Cliente terminal para la venta de asientos.
Se conecta al servidor y permite comprar asientos interactivamente.
"""

import socket
import sys


class ClienteAsientos:
    """
    Cliente que se conecta al servidor de venta de asientos.
    """
    
    def __init__(self, host='localhost', puerto=5000):
        self.host = host
        self.puerto = puerto
        self.socket = None
        self.archivo = None
        self.conectado = False
        self.id_cliente = None  # ID asignado por el servidor
    
    def conectar(self):
        """
        Establece conexión con el servidor.
        Retorna True si la conexión es exitosa, False en caso contrario.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.puerto))
            
            # Convertir socket a archivo para usar readline/write
            self.archivo = self.socket.makefile('rw', encoding='utf-8', newline='\n')
            
            # Leer mensaje de bienvenida
            bienvenida = self.archivo.readline().strip()
            if bienvenida.startswith("BIENVENIDO_SERVIDOR"):
                # Extraer ID del cliente si está presente
                if ":ID=" in bienvenida:
                    self.id_cliente = bienvenida.split("ID=")[1]
                    print(f"✓ Conectado al servidor {self.host}:{self.puerto}")
                    print(f"  → Asignado como Cliente #{self.id_cliente}")
                else:
                    print(f"✓ Conectado al servidor {self.host}:{self.puerto}")
                self.conectado = True
                return True
            else:
                print("⚠ Respuesta inesperada del servidor")
                return False
                
        except ConnectionRefusedError:
            print(f"✗ No se pudo conectar al servidor en {self.host}:{self.puerto}")
            print("  Asegúrate de que el servidor esté ejecutándose.")
            return False
        except Exception as e:
            print(f"✗ Error al conectar: {e}")
            return False
    
    def enviar_comando(self, comando):
        """
        Envía un comando al servidor y retorna la respuesta.
        Retorna None si hay error de comunicación.
        """
        try:
            self.archivo.write(comando + '\n')
            self.archivo.flush()
            
            respuesta = self.archivo.readline().strip()
            return respuesta
        except Exception as e:
            print(f"✗ Error de comunicación: {e}")
            self.conectado = False
            return None
    
    def vender_aleatorio(self):
        """
        Solicita la venta de un asiento aleatorio.
        """
        print("\n--- Venta Aleatoria ---")
        respuesta = self.enviar_comando("VENDER_RANDOM")
        
        if respuesta is None:
            return
        
        if respuesta.startswith("OK:"):
            numero = respuesta.split(':')[1]
            print(f"✓ ¡Asiento {numero} vendido exitosamente!")
        elif respuesta == "NO_QUEDAN":
            print("⚠ No quedan asientos disponibles")
        else:
            print(f"⚠ Respuesta inesperada: {respuesta}")
    
    def vender_especifico(self):
        """
        Solicita la venta de un asiento específico.
        """
        print("\n--- Venta Específica ---")
        
        try:
            numero = input("Ingresa el número de asiento (1-40): ").strip()
            
            if not numero.isdigit():
                print("⚠ Debes ingresar un número válido")
                return
            
            respuesta = self.enviar_comando(f"VENDER_ESPECIFICO:{numero}")
            
            if respuesta is None:
                return
            
            if respuesta.startswith("OK:"):
                num = respuesta.split(':')[1]
                print(f"✓ ¡Asiento {num} vendido exitosamente!")
            elif respuesta == "OCUPADO":
                print(f"⚠ El asiento {numero} ya está ocupado")
            elif respuesta == "INVALIDO":
                print(f"⚠ Número de asiento inválido (debe ser entre 1 y 40)")
            else:
                print(f"⚠ Respuesta inesperada: {respuesta}")
                
        except KeyboardInterrupt:
            print("\n⚠ Operación cancelada")
    
    def ver_vendidos(self):
        """
        Solicita y muestra la lista de asientos vendidos.
        """
        print("\n--- Asientos Vendidos ---")
        respuesta = self.enviar_comando("RESUMEN")
        
        if respuesta is None:
            return
        
        if respuesta.startswith("VENDIDOS:"):
            lista_str = respuesta.split(':', 1)[1]
            try:
                # Evaluar la lista de forma segura
                import ast
                lista = ast.literal_eval(lista_str)
                
                if not lista:
                    print("No hay asientos vendidos aún")
                else:
                    print(f"Total vendidos: {len(lista)}")
                    print(f"Asientos: {lista}")
                    
                    # Mostrar de forma visual
                    print("\nRepresentación visual:")
                    for fila in range(4):
                        inicio = fila * 10 + 1
                        fin = inicio + 10
                        fila_str = ""
                        for num in range(inicio, fin):
                            if num in lista:
                                fila_str += f"[X{num:2d}] "
                            else:
                                fila_str += f"[_{num:2d}] "
                        print(fila_str)
                    print("\n[X] = Vendido  [_] = Disponible")
                    
            except Exception as e:
                print(f"⚠ Error al procesar respuesta: {e}")
        else:
            print(f"⚠ Respuesta inesperada: {respuesta}")
    
    def mostrar_menu(self):
        """
        Muestra el menú de opciones.
        """
        print("\n" + "=" * 50)
        print("  SISTEMA DE VENTA DE ASIENTOS".center(50))
        print("=" * 50)
        print("1. Vender asiento aleatorio")
        print("2. Vender asiento específico")
        print("3. Ver asientos vendidos")
        print("4. Salir")
        print("=" * 50)
    
    def ejecutar(self):
        """
        Ejecuta el bucle principal del cliente.
        """
        if not self.conectar():
            return
        
        try:
            while self.conectado:
                self.mostrar_menu()
                
                try:
                    opcion = input("\nSelecciona una opción (1-4): ").strip()
                    
                    if opcion == '1':
                        self.vender_aleatorio()
                    elif opcion == '2':
                        self.vender_especifico()
                    elif opcion == '3':
                        self.ver_vendidos()
                    elif opcion == '4':
                        print("\n--- Cerrando sesión ---")
                        respuesta = self.enviar_comando("SALIR")
                        if respuesta == "ADIOS" or respuesta is None:
                            print("✓ Desconectado del servidor")
                        break
                    else:
                        print("⚠ Opción inválida. Selecciona una opción del 1 al 4.")
                
                except KeyboardInterrupt:
                    print("\n\n--- Interrupción detectada ---")
                    self.enviar_comando("SALIR")
                    break
                    
        finally:
            self.cerrar()
    
    def cerrar(self):
        """
        Cierra la conexión con el servidor.
        """
        try:
            if self.archivo:
                self.archivo.close()
            if self.socket:
                self.socket.close()
        except:
            pass
        self.conectado = False


def main():
    """
    Función principal del cliente.
    """
    host = 'localhost'
    puerto = 5000
    
    # Permitir especificar host y puerto por línea de comandos
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            puerto = int(sys.argv[2])
        except ValueError:
            print("Uso: python cliente.py [host] [puerto]")
            sys.exit(1)
    
    print("=" * 50)
    print("  CLIENTE - SISTEMA DE VENTA DE ASIENTOS".center(50))
    print("=" * 50)
    
    cliente = ClienteAsientos(host=host, puerto=puerto)
    cliente.ejecutar()
    
    print("\n¡Hasta luego!")


if __name__ == "__main__":
    main()
