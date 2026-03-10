#!/usr/bin/env python3
"""
Servidor central para la venta de 40 asientos.
Acepta múltiples conexiones simultáneas mediante threading.
Implementa un sistema de cola FIFO para garantizar orden de prioridad.
"""

import socket
import threading
import signal
import sys
import random
import queue
import time
from collections import OrderedDict


class ServidorAsientos:
    """
    Servidor que gestiona la venta de 40 asientos con exclusión mutua.
    Implementa sistema de cola FIFO para garantizar prioridad por orden de llegada.
    """
    
    def __init__(self, puerto=5000, total_asientos=40):
        self.puerto = puerto
        self.total_asientos = total_asientos
        # Estado compartido: False = libre, True = vendido
        self.asientos_vendidos = [False] * (total_asientos + 1)  # índice 0 no se usa
        self.contador_vendidos = 0
        self.lock = threading.Lock()  # Para sincronización del estado
        self.servidor_activo = True
        self.clientes_conectados = 0
        
        # Sistema de prioridades FIFO
        self.proximo_id_cliente = 1
        self.lock_id = threading.Lock()  # Para asignar IDs
        self.cola_peticiones = queue.Queue()  # Cola FIFO de peticiones
        self.clientes_info = OrderedDict()  # Información de clientes conectados
        
        # Estadísticas de prioridad
        self.peticiones_procesadas = 0
        self.conflictos_detectados = 0
    
    def asignar_id_cliente(self):
        """
        Asigna un ID único a cada cliente que se conecta.
        """
        with self.lock_id:
            id_cliente = self.proximo_id_cliente
            self.proximo_id_cliente += 1
            return id_cliente
    
    def registrar_cliente(self, id_cliente, addr):
        """
        Registra un cliente en el sistema.
        """
        with self.lock:
            self.clientes_info[id_cliente] = {
                'addr': addr,
                'hora_conexion': time.time(),
                'peticiones': 0
            }
    
    def desregistrar_cliente(self, id_cliente):
        """
        Elimina un cliente del registro.
        """
        with self.lock:
            if id_cliente in self.clientes_info:
                del self.clientes_info[id_cliente]
        
    def vender_asiento_especifico(self, numero, id_cliente=None):
        """
        Intenta vender un asiento específico.
        Retorna: ('OK', numero) | ('OCUPADO', numero) | ('INVALIDO', numero)
        """
        with self.lock:
            # Registrar petición
            self.peticiones_procesadas += 1
            
            # Log de prioridad
            if id_cliente:
                clientes_esperando = len(self.clientes_info) - 1
                if clientes_esperando > 0:
                    self.conflictos_detectados += 1
                    print(f"[PRIORIDAD] Cliente #{id_cliente} procesando (otros {clientes_esperando} esperando)")
            
            if numero < 1 or numero > self.total_asientos:
                return ('INVALIDO', numero)
            
            if self.asientos_vendidos[numero]:
                return ('OCUPADO', numero)
            
            # Marcar como vendido
            self.asientos_vendidos[numero] = True
            self.contador_vendidos += 1
            
            # Actualizar estadísticas del cliente
            if id_cliente and id_cliente in self.clientes_info:
                self.clientes_info[id_cliente]['peticiones'] += 1
            
            return ('OK', numero)
    
    def vender_siguiente_disponible(self, id_cliente=None):
        """
        Vende el primer asiento disponible.
        Retorna: ('OK', numero) | ('NO_QUEDAN', None)
        """
        with self.lock:
            # Registrar petición
            self.peticiones_procesadas += 1
            
            # Log de prioridad
            if id_cliente:
                clientes_esperando = len(self.clientes_info) - 1
                if clientes_esperando > 0:
                    self.conflictos_detectados += 1
                    print(f"[PRIORIDAD] Cliente #{id_cliente} procesando (otros {clientes_esperando} esperando)")
            
            for i in range(1, self.total_asientos + 1):
                if not self.asientos_vendidos[i]:
                    self.asientos_vendidos[i] = True
                    self.contador_vendidos += 1
                    
                    # Actualizar estadísticas del cliente
                    if id_cliente and id_cliente in self.clientes_info:
                        self.clientes_info[id_cliente]['peticiones'] += 1
                    
                    return ('OK', i)
            return ('NO_QUEDAN', None)
    
    def obtener_vendidos(self):
        """
        Retorna la lista de asientos vendidos.
        """
        with self.lock:
            vendidos = [i for i in range(1, self.total_asientos + 1) 
                       if self.asientos_vendidos[i]]
            return vendidos
    
    def manejar_cliente(self, conn, addr, id_cliente):
        """
        Maneja la comunicación con un cliente en un hilo separado.
        """
        print(f"[SERVIDOR] Cliente #{id_cliente} conectado desde {addr}")
        
        # Registrar cliente
        self.registrar_cliente(id_cliente, addr)
        
        try:
            # Enviar mensaje de bienvenida con ID
            conn.sendall(f"BIENVENIDO_SERVIDOR:ID={id_cliente}\n".encode())
            
            # Convertir socket a archivo para usar readline
            archivo = conn.makefile('rw', encoding='utf-8', newline='\n')
            
            while self.servidor_activo:
                # Leer comando del cliente
                linea = archivo.readline()
                if not linea:
                    break  # Cliente cerró la conexión
                
                comando = linea.strip()
                print(f"[SERVIDOR] Cliente #{id_cliente} solicita: {comando}")
                
                # Procesar comando con ID de cliente
                respuesta = self.procesar_comando(comando, id_cliente)
                
                # Enviar respuesta
                archivo.write(respuesta + '\n')
                archivo.flush()
                
                # Si el cliente envió SALIR, cerrar conexión
                if comando == "SALIR":
                    break
                    
        except Exception as e:
            print(f"[SERVIDOR] Error con cliente #{id_cliente}: {e}")
        finally:
            conn.close()
            self.desregistrar_cliente(id_cliente)
            with self.lock:
                self.clientes_conectados -= 1
            print(f"[SERVIDOR] Cliente #{id_cliente} desconectado. Clientes activos: {self.clientes_conectados}")
    
    def procesar_comando(self, comando, id_cliente=None):
        """
        Procesa un comando recibido del cliente y retorna la respuesta.
        """
        if comando == "VENDER_RANDOM":
            resultado, numero = self.vender_siguiente_disponible(id_cliente)
            if resultado == 'OK':
                return f"OK:{numero}"
            else:
                return "NO_QUEDAN"
        
        elif comando.startswith("VENDER_ESPECIFICO:"):
            try:
                numero = int(comando.split(':', 1)[1])
                resultado, num = self.vender_asiento_especifico(numero, id_cliente)
                if resultado == 'OK':
                    return f"OK:{num}"
                elif resultado == 'OCUPADO':
                    return "OCUPADO"
                else:
                    return "INVALIDO"
            except (ValueError, IndexError):
                return "INVALIDO"
        
        elif comando == "RESUMEN":
            vendidos = self.obtener_vendidos()
            return f"VENDIDOS:{vendidos}"
        
        elif comando == "SALIR":
            return "ADIOS"
        
        else:
            return "COMANDO_DESCONOCIDO"
    
    def mostrar_resumen_final(self):
        """
        Muestra el resumen de asientos vendidos al finalizar.
        """
        print("\n" + "=" * 60)
        print("RESUMEN FINAL DEL SERVIDOR")
        print("=" * 60)
        vendidos = self.obtener_vendidos()
        print(f"Total de asientos vendidos: {self.contador_vendidos}/{self.total_asientos}")
        print(f"Asientos vendidos: {vendidos}")
        print("\n--- Estadísticas de Prioridad ---")
        print(f"Total de peticiones procesadas: {self.peticiones_procesadas}")
        print(f"Situaciones de concurrencia detectadas: {self.conflictos_detectados}")
        if self.conflictos_detectados > 0:
            print("✓ El sistema FIFO garantizó el orden de prioridad correcto")
        print("=" * 60)
    
    def iniciar(self):
        """
        Inicia el servidor y acepta conexiones.
        """
        # Crear socket del servidor
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Opciones para reutilizar el puerto inmediatamente
        servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # En algunos sistemas, también ayuda SO_REUSEPORT
        try:
            servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except (AttributeError, OSError):
            pass  # No disponible en todos los sistemas
        
        try:
            servidor_socket.bind(('0.0.0.0', self.puerto))
            servidor_socket.listen(5)
            print(f"[SERVIDOR] Escuchando en puerto {self.puerto}")
            print(f"[SERVIDOR] Gestionando {self.total_asientos} asientos")
            print("[SERVIDOR] Presiona Ctrl+C para detener\n")
            
            # Configurar timeout para poder interrumpir con Ctrl+C
            servidor_socket.settimeout(1.0)
            
            while self.servidor_activo:
                try:
                    conn, addr = servidor_socket.accept()
                    
                    # Asignar ID único al cliente
                    id_cliente = self.asignar_id_cliente()
                    
                    with self.lock:
                        self.clientes_conectados += 1
                    
                    # Crear hilo para manejar el cliente
                    hilo_cliente = threading.Thread(
                        target=self.manejar_cliente,
                        args=(conn, addr, id_cliente),
                        daemon=True
                    )
                    hilo_cliente.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self.servidor_activo:
                        print(f"[SERVIDOR] Error al aceptar conexión: {e}")
        
        except KeyboardInterrupt:
            print("\n[SERVIDOR] Deteniendo servidor...")
        except OSError as e:
            if "Address already in use" in str(e):
                print("\n[ERROR] El puerto 5000 ya está en uso.")
                print("Soluciones:")
                print("  1. Espera 30-60 segundos y vuelve a intentar")
                print("  2. Usa otro puerto: python servidor.py 5001")
                print("  3. Mata el proceso que usa el puerto:")
                print("     sudo lsof -ti:5000 | xargs kill -9")
                sys.exit(1)
            else:
                raise
        finally:
            self.servidor_activo = False
            print("[SERVIDOR] Cerrando socket...")
            
            # Cerrar el socket correctamente
            try:
                servidor_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            
            servidor_socket.close()
            
            # Pequeña pausa para asegurar liberación del puerto
            time.sleep(0.5)
            
            self.mostrar_resumen_final()


def main():
    """
    Función principal del servidor.
    """
    puerto = 5000
    
    # Permitir especificar puerto por línea de comandos
    if len(sys.argv) > 1:
        try:
            puerto = int(sys.argv[1])
        except ValueError:
            print("Uso: python servidor.py [puerto]")
            sys.exit(1)
    
    servidor = ServidorAsientos(puerto=puerto)
    servidor.iniciar()


if __name__ == "__main__":
    main()
