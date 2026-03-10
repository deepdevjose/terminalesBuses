#!/usr/bin/env python3
"""
Script para obtener la IP del servidor.
Úsalo en la máquina donde ejecutarás el servidor.
"""

import socket


def obtener_ip_local():
    """
    Obtiene la IP local de la máquina.
    """
    try:
        # Crear socket temporal para descubrir la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # No necesita conectarse realmente
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def obtener_todas_las_ips():
    """
    Obtiene todas las IPs disponibles en la máquina.
    """
    import subprocess
    
    print("=" * 70)
    print("INFORMACIÓN DE RED - IPs DISPONIBLES")
    print("=" * 70)
    
    # IP local principal
    ip_local = obtener_ip_local()
    if ip_local:
        print(f"\n📍 IP Principal: {ip_local}")
        print(f"   → Usa esta IP para conectarte desde otras máquinas en la misma red")
    
    print("\n📋 Todas las interfaces de red:")
    print("-" * 70)
    
    try:
        # En Linux
        resultado = subprocess.run(['ip', 'addr'], capture_output=True, text=True, timeout=5)
        if resultado.returncode == 0:
            lineas = resultado.stdout.split('\n')
            for linea in lineas:
                if 'inet ' in linea and '127.0.0.1' not in linea:
                    partes = linea.strip().split()
                    if len(partes) >= 2:
                        ip_cidr = partes[1]
                        ip = ip_cidr.split('/')[0]
                        print(f"   • {ip}")
        else:
            raise Exception("Comando ip no disponible")
    except:
        # Alternativa
        try:
            resultado = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=5)
            if resultado.returncode == 0:
                ips = resultado.stdout.strip().split()
                for ip in ips:
                    if ip != '127.0.0.1':
                        print(f"   • {ip}")
        except:
            print("   No se pudieron obtener las IPs automáticamente")
    
    print("-" * 70)
    print("\n💡 INSTRUCCIONES PARA CLIENTES:")
    print("=" * 70)
    if ip_local:
        print(f"\nEn otra máquina, ejecuta:")
        print(f"  python cliente.py {ip_local}")
        print(f"\nO edita cliente.py y cambia:")
        print(f"  host = 'localhost'")
        print(f"  ↓")
        print(f"  host = '{ip_local}'")
    
    print("\n🔥 IMPORTANTE: Asegúrate de que el firewall permita conexiones")
    print("   al puerto 5000 (o el puerto que uses)")
    print("=" * 70)


def main():
    hostname = socket.gethostname()
    print("\n" + "=" * 70)
    print("CONFIGURACIÓN DE RED PARA SERVIDOR DE ASIENTOS")
    print("=" * 70)
    print(f"\n🖥️  Nombre del host: {hostname}")
    
    obtener_todas_las_ips()
    
    print("\n📖 Más información:")
    print("   • El servidor escucha en 0.0.0.0 (todas las interfaces)")
    print("   • Puerto por defecto: 5000")
    print("   • Protocolo: TCP")


if __name__ == "__main__":
    main()
