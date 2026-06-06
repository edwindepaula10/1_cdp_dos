```markdown
# Laboratorio 1: CDP DoS Attack (Cisco Discovery Protocol)

## 1. Información General

- **Institución:** Instituto Tecnológico de las Américas (ITLA), República Dominicana
- **Materia:** Seguridad en Redes - Ataques de Capa 2
- **Estudiante:** Edwin De Paula
- **Matrícula:** 2024-2415
- **Enlace del Video:** [PENDIENTE - Insertar URL de YouTube]

## 2. Objetivos del Laboratorio

### Objetivo General
Demostrar la vulnerabilidad del protocolo CDP (Cisco Discovery Protocol) ante un ataque de denegación de servicio (DoS) mediante inundación de vecinos falsos, y aplicar las contra-medidas necesarias para mitigar este vector de ataque en infraestructura de Capa 2.

### Objetivo del Script
Desarrollar un script en Python 3 con Scapy que inyecte paquetes CDP maliciosos hacia la dirección multicast `01:00:0c:cc:cc:cc`, saturando la tabla de vecinos CDP del switch objetivo y provocando consumo excesivo de CPU/memoria o desbordamiento de la tabla CDP.

## 3. Requisitos y Parámetros del Script

### Requisitos del Sistema
- **Sistema Operativo:** Parrot Security OS / Kali Linux
- **Privilegios:** Root (sudo) - necesario para inyección de paquetes raw
- **Dependencias Python:**
  ```bash
  pip3 install scapy
  ```
- **Interfaz de Red:** Interfaz conectada al switch objetivo (ens33, eth0, etc.)

### Comandos de Ejecución
```bash
# Ubicación del script
cd src/
sudo python3 cdp_dos_attack.py [interfaz]

# Ejemplo con interfaz específica
sudo python3 cdp_dos_attack.py ens33
```

### Parámetros del Script
| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `interfaz` | Interfaz de red para inyectar paquetes | ens33, eth0 |

## 4. Documentación del Funcionamiento del Script

### Flujo de Ejecución

1. **Inicialización**
   - Verifica privilegios root
   - Detecta o recibe interfaz de red
   - Genera valores aleatorios para los TLVs

2. **Construcción del Paquete CDP**
   - Capa Ethernet: MAC origen aleatoria, destino multicast `01:00:0c:cc:cc:cc`
   - Capa LLC: DSAP=0xaa, SSAP=0xaa, Control=3
   - Capa SNAP: OUI=0x00000c (Cisco), Code=0x2000 (CDP)
   - Payload CDP construido con TLVs manuales:
     - Tipo 0x0001: Device ID
     - Tipo 0x0002: Address (IPv4)
     - Tipo 0x0003: Port ID
     - Tipo 0x0004: Capabilities
     - Tipo 0x0005: Software Version
     - Tipo 0x0006: Platform

3. **Cálculo de Checksum CDP**
   - Implementa algoritmo RFC 1071 específico para CDP
   - El switch rechaza paquetes con checksum incorrecto
   - Se calcula sobre header CDP + TLVs con campo checksum en cero

4. **Inundación (DoS)**
   - Bucle infinito enviando paquetes
   - Delay variable de 5-15ms
   - Estadísticas cada 50 paquetes

### Efectos del Ataque
- La tabla `show cdp neighbors` se llena de entradas falsas `ITLA-SW-XXXX`
- Aumento de CPU del switch por procesamiento de CDP
- Posible desbordamiento de la tabla CDP

## 5. Documentación de la Red y Topología

### Entorno de Simulación
- **Plataforma:** PNetLab
- **Switch:** Cisco vIOS L2 / IOL (Cisco IOS 15.x)
- **Atacante:** Parrot Security OS
- **Interfaz atacante:** ens33 (conectada a Ethernet0/1 del switch)

### Topología

```
                    ┌─────────────────────┐
                    │   PNetLab Switch    │
                    │   Cisco IOL L2      │
                    └─────────────────────┘
                              │
                    Ethernet0/1│
                              │
                    ┌─────────┴─────────┐
                    │   Atacante        │
                    │   Parrot OS       │
                    │   ens33           │
                    │   172.24.15.100   │
                    └───────────────────┘
```

### Interfaces
| Dispositivo | Interfaz | VLAN | Dirección IP | Propósito |
|-------------|----------|------|--------------|-----------|
| Switch | Ethernet0/1 | VLAN 1 | N/A | Puerto atacante |
| Atacante | ens33 | VLAN 1 | 172.24.15.100/24 | Inyección CDP |

## 6. Documentación de la Contra-medida / Mitigación

### Comandos de Configuración

```cisconet
! Verificar estado actual
show cdp
show cdp neighbors
show cdp interface Ethernet0/1

! Mitigación: deshabilitar CDP en el puerto del atacante
configure terminal
interface Ethernet0/1
 no cdp enable
 end

! Verificar mitigación
show cdp interface Ethernet0/1

! Alternativa global (más drástica)
configure terminal
 no cdp run
 end
```

### Justificación Técnica

**¿Por qué funciona esta mitigación?**

1. **CDP opera sin autenticación** en Capa 2. Cualquier dispositivo puede inyectar paquetes CDP válidos.

2. **El ataque explota la falta de control de origen:**
   - El switch procesa todos los paquetes CDP recibidos
   - No diferencia entre vecino legítimo y malicioso

3. **`no cdp enable` en interfaces de acceso:**
   - Previene inyección CDP desde el puerto del atacante
   - No afecta CDP en troncales (útil para discovery)
   - Reduce superficie de ataque

### Verificación de la Mitigación

```cisconet
! Antes del hardening
show cdp neighbors
! Muestra entradas ITLA-SW-XXXX

! Después de `no cdp enable`
show cdp neighbors
! Ya no aparecen nuevas entradas falsas
```

### Evidencia del Laboratorio

| Estado | show cdp neighbors | show cdp traffic (Chksum error) |
|--------|-------------------|-------------------------------|
| Antes del ataque | Vecinos reales | 0 |
| Durante el ataque | ITLA-SW-XXXX aparecen | 0 (checksum válido) |
| Después de mitigación | No aumentan | Paquetes ignorados |

### Recomendaciones Adicionales

| Medida | Comando | Justificación |
|--------|---------|---------------|
| Port Security | `switchport port-security` | Previene MAC spoofing |
| BPDU Guard | `spanning-tree bpduguard enable` | Previene ataques STP |
| Rate limiting | `cdp rate-limit 10` | Limita CDP por segundo |

## 7. Estructura del Repositorio

```
1_cdp_dos/
├── README.md
├── screenshots/
│   ├── antes_ataque.png
│   ├── durante_ataque.png
│   └── despues_mitigacion.png
└── src/
    └── cdp_dos_attack.py
```

## 8. Referencias

- Cisco CDP Documentation: https://www.cisco.com/c/en/us/support/docs/lan-switching/cisco-discovery-protocol-cdp/44805-cdp-discover-protocol.html
- RFC 1071 - Computing the Internet Checksum
- MITRE ATT&CK: T1200 - Hardware Additions

---

**Laboratorio completado por Edwin De Paula (2024-2415)**
**ITLA - Seguridad en Redes**
```

Este README ahora:
- No contiene el código del script (está en `src/`)
- Mantiene tu estructura obligatoria
- Incluye la referencia a la carpeta `src/` en comandos y estructura
- Está en texto plano crudo, listo para copiar
