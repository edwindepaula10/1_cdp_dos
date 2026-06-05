```markdown
# Laboratorio 1: Ataque y Mitigación de CDP DoS (Denial of Service)

## 1. Información General

* **Institución:** Instituto Tecnológico de las Américas (ITLA)
* **Materia:** Seguridad de Redes
* **Estudiante:** Edwin De Paula
* **Matrícula:** 2024-2415
* **Enlace de Demostración:** [Lista de Reproducción de YouTube](https://www.youtube.com/playlist?list=TU_PLAYLIST_AQUI)

---

## 2. Objetivos del Laboratorio

* **Objetivo General:** Evaluar el impacto de la recepción descontrolada de anuncios del protocolo propietario de Cisco (CDP) en la tabla de vecinos de un switch de Capa 2 y aplicar contramedidas eficientes.
* **Objetivo del Script:** Automatizar la inyección masiva de tramas CDP versión 2 estructuradas con identidades de hardware, versiones de software y direcciones de red aleatorias utilizando la interfaz física de un atacante.

---

## 3. Requisitos y Parámetros del Script

### Requisitos del Sistema

* Entorno de ejecución Linux (Parrot OS o similar).
* Privilegios de administrador (`sudo`).
* Python 3 y la suite de manipulación de red **Scapy** instalada:

```bash
sudo apt update && sudo apt install python3-scapy -y

```

### Parámetros utilizados en la herramienta

* **Interfaz de red objetivo:** Determina la tarjeta física (ej. `eth0`) conectada al switch Cisco.
* **Destino de Multicast:** `01:00:0c:cc:cc:cc` (Dirección física oficial reservada para el tráfico de control de Cisco en capa de enlace).
* **Campos TLV (Type-Length-Value) Generados:**
* **Device ID:** Nombres aleatorios con prefijo `SW_Falso_`.
* **Port ID:** Puertos de origen falsos (ej. `GigabitEthernet0/15`).
* **IP Address:** Direcciones IPv4 generadas de forma aleatoria para emular interfaces de gestión.
* **Capabilities & Platform:** Simulación de modelos Cisco de gama media (ej. WS-C2960).



---

## 4. Funcionamiento del Script

El script carga de manera dinámica el módulo de contribución CDP de Scapy. A través de un bucle infinito, genera valores de hardware e IP aleatorios en cada ciclo para simular nuevos vecinos legítimos de Cisco.

Las variables se introducen en las estructuras de datos de tipo TLV (DeviceID, Address, PortID, Capabilities, SoftwareVersion, Platform), las cuales son empaquetadas dentro de un formato SNAP con identificador de protocolo Cisco (`0x2000`) sobre un encabezado LLC (`dsap=0xaa, ssap=0xaa`). Las tramas resultantes son inyectadas a alta velocidad directo a la interfaz del switch, forzándolo a registrar y mantener en la memoria RAM cientos de vecinos falsos en cuestión de segundos.

---

## 5. Documentación de la Red y Topología

### Detalles de Infraestructura

* **Entorno de Simulación:** PNetLab
* **Switch Principal:** SW1-CISCO (Cisco vIOS L2)
* **Interfaz de Conexión del Atacante:** `Ethernet0/1`
* **Segmento de Red:** VLAN 10 (Datos)
* **Direccionamiento IP de Prueba:** `192.168.10.0/24`

---

## 6. Documentación de la Contra-medida (Mitigación)

Debido a que CDP es un protocolo que transmite información confidencial en texto plano sin autenticación, la recomendación de seguridad para puertos orientados al usuario (interfaces de acceso) es desactivar el protocolo por completo.

### Comandos de Configuración Aplicados

#### Opción A: Desactivar CDP de forma Global en el Switch

```cisconet
SW1-CISCO# configure terminal
SW1-CISCO(config)# no cdp run
SW1-CISCO(config)# end

```

#### Opción B: Desactivar CDP específicamente en los puertos de acceso (Recomendado)

```cisconet
SW1-CISCO# configure terminal
SW1-CISCO(config)# interface Ethernet0/1
SW1-CISCO(config-if)# no cdp enable
SW1-CISCO(config-if)# end

```

### Justificación Técnica de la Defensa

El comando `no cdp enable` detiene por completo el procesamiento y la recepción de tramas destinadas a la dirección multicast `01:00:0c:cc:cc:cc` en la interfaz específica del atacante. El switch simplemente descarta los paquetes entrantes, previniendo el agotamiento de memoria, la inyección de vecinos falsos y bloqueando la fuga de información de infraestructura sensible (como nombres de equipos de red y sus IPs de administración).

```

```
