#!/usr/bin/env python3
"""
Script de utilidad para limpiar puertos en uso.
Útil cuando el servidor se cierra inesperadamente y el puerto queda bloqueado.
"""

import subprocess
import sys
import os


def limpiar_puerto(puerto=5000):
    """
    Intenta limpiar/liberar un puerto que quedó en uso.
    """
    print("=" * 60)
    print(f"LIMPIEZA DE PUERTO {puerto}")
    print("=" * 60)
    
    # Verificar si el puerto está en uso
    print(f"\n1️⃣  Verificando puerto {puerto}...")
    
    try:
        # Linux/Mac
        resultado = subprocess.run(
            ['lsof', '-ti', f':{puerto}'],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        if resultado.returncode == 0 and resultado.stdout.strip():
            pids = resultado.stdout.strip().split('\n')
            print(f"   ✓ Puerto {puerto} está siendo usado por proceso(s): {', '.join(pids)}")
            
            # Preguntar antes de matar
            respuesta = input(f"\n¿Matar estos procesos? (s/n): ").strip().lower()
            
            if respuesta == 's':
                for pid in pids:
                    try:
                        subprocess.run(['kill', '-9', pid], check=True)
                        print(f"   ✓ Proceso {pid} terminado")
                    except subprocess.CalledProcessError:
                        print(f"   ✗ Error al terminar proceso {pid}")
                        print(f"     Intenta manualmente: sudo kill -9 {pid}")
                
                print(f"\n✓ Puerto {puerto} liberado")
                return True
            else:
                print("   Operación cancelada")
                return False
        else:
            print(f"   ✓ Puerto {puerto} está libre")
            return True
            
    except FileNotFoundError:
        print("   ⚠ Comando 'lsof' no disponible")
        print("\n   Alternativas manuales:")
        print(f"   • Linux: sudo lsof -ti:{puerto} | xargs kill -9")
        print(f"   • Linux: sudo fuser -k {puerto}/tcp")
        print(f"   • Reiniciar la máquina")
        return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def verificar_puertos_comunes():
    """
    Verifica el estado de puertos comunes.
    """
    print("\n" + "=" * 60)
    print("VERIFICACIÓN DE PUERTOS COMUNES")
    print("=" * 60)
    
    puertos = [5000, 5001, 8000, 8080]
    
    for puerto in puertos:
        try:
            resultado = subprocess.run(
                ['lsof', '-ti', f':{puerto}'],
                capture_output=True,
                text=True,
                timeout=2
            )
            
            if resultado.returncode == 0 and resultado.stdout.strip():
                pids = resultado.stdout.strip().split('\n')
                print(f"   • Puerto {puerto}: EN USO (PID: {', '.join(pids)})")
            else:
                print(f"   • Puerto {puerto}: LIBRE ✓")
        except:
            break
    
    print("=" * 60)


def mostrar_comandos_utiles():
    """
    Muestra comandos útiles para gestión de puertos.
    """
    print("\n" + "=" * 60)
    print("COMANDOS ÚTILES")
    print("=" * 60)
    print("\n📋 Ver qué proceso usa un puerto:")
    print("   sudo lsof -i :5000")
    print("   sudo netstat -tulpn | grep 5000")
    print("   sudo ss -tulpn | grep 5000")
    
    print("\n🔪 Matar proceso en puerto:")
    print("   sudo lsof -ti:5000 | xargs kill -9")
    print("   sudo fuser -k 5000/tcp")
    
    print("\n👀 Ver todos los puertos en uso:")
    print("   sudo netstat -tulpn")
    print("   sudo ss -tulpn")
    
    print("\n⏰ Esperar a que el puerto se libere:")
    print("   watch -n 1 'lsof -i :5000'")
    
    print("=" * 60)


def modo_rapido():
    """
    Modo rápido: intenta limpiar el puerto sin preguntar.
    """
    puerto = 5000
    print(f"[MODO RÁPIDO] Limpiando puerto {puerto}...")
    
    try:
        resultado = subprocess.run(
            ['lsof', '-ti', f':{puerto}'],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        if resultado.returncode == 0 and resultado.stdout.strip():
            pids = resultado.stdout.strip().split('\n')
            for pid in pids:
                subprocess.run(['kill', '-9', pid], capture_output=True)
            print(f"✓ Puerto {puerto} limpiado")
            return True
        else:
            print(f"✓ Puerto {puerto} ya estaba libre")
            return True
    except:
        print("✗ No se pudo limpiar automáticamente")
        print("  Intenta manualmente: sudo lsof -ti:5000 | xargs kill -9")
        return False


def main():
    """
    Función principal.
    """
    print("\n" + "=" * 60)
    print("UTILIDAD DE LIMPIEZA DE PUERTOS".center(60))
    print("=" * 60)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--rapido' or sys.argv[1] == '-r':
            modo_rapido()
            return
        elif sys.argv[1] == '--verificar' or sys.argv[1] == '-v':
            verificar_puertos_comunes()
            return
        elif sys.argv[1] == '--ayuda' or sys.argv[1] == '-h':
            mostrar_comandos_utiles()
            return
        else:
            try:
                puerto = int(sys.argv[1])
                limpiar_puerto(puerto)
                return
            except ValueError:
                print(f"✗ Puerto inválido: {sys.argv[1]}")
                sys.exit(1)
    
    # Menú interactivo
    print("\nOpciones:")
    print("1. Limpiar puerto 5000 (por defecto)")
    print("2. Limpiar puerto personalizado")
    print("3. Verificar puertos comunes")
    print("4. Mostrar comandos útiles")
    print("5. Salir")
    
    try:
        opcion = input("\nSelecciona una opción (1-5): ").strip()
        
        if opcion == '1':
            limpiar_puerto(5000)
        elif opcion == '2':
            puerto = int(input("Ingresa el número de puerto: ").strip())
            limpiar_puerto(puerto)
        elif opcion == '3':
            verificar_puertos_comunes()
        elif opcion == '4':
            mostrar_comandos_utiles()
        elif opcion == '5':
            print("Saliendo...")
        else:
            print("Opción inválida")
    except KeyboardInterrupt:
        print("\n\nOperación cancelada")
    except ValueError:
        print("✗ Número de puerto inválido")


if __name__ == "__main__":
    # Verificar si se está ejecutando en Linux/Mac
    if os.name != 'posix':
        print("⚠ Este script está diseñado para Linux/Mac")
        print("  En Windows, usa: netstat -ano | findstr :5000")
        sys.exit(1)
    
    main()
