# Laboratorio 1: Ataque y Mitigación de CDP DoS (Denial of Service)

## 1. Información General

* **Institución:** Instituto Tecnológico de las Américas (ITLA)
* **Materia:** Seguridad de Redes
* **Estudiante:** Edwin De Paula
* **Matrícula:** 2024-2415
* **Enlace del Video:** [Lista de Reproducción de YouTube - Demostración](https://www.google.com/search?q=AQU%C3%8D_PEGAS_EL_LINK_DE_TU_PLAYLIST_O_VIDEO)

---

## 2. Objetivos del Laboratorio

* **Objetivo General:** Evaluar el impacto de la recepción descontrolada de anuncios del protocolo propietario de Cisco (CDP) en la tabla de vecinos de un switch de Capa 2 y aplicar contramedidas eficientes.
* **Objetivo del Script:** Automatizar la inyección masiva de tramas CDP versión 2 estructuradas con identidades de hardware, versiones de software y direcciones de red aleatorias utilizando la interfaz física de un atacante.

---

## 3. Requisitos y Parámetros del Script

### Requisitos del Sistema:

* Entorno de ejecución Linux (Parrot OS / Kali Linux).
* Privilegios de superusuario (`sudo`).
* Python 3 instalado junto con la librería de manipulación de paquetes **Scapy**.

```bash
sudo apt install python3-scapy -y

```

### Parámetros utilizados en la herramienta:

* **Interfaz de red objetivo:** Determina la tarjeta física (ej. eth0) conectada al switch Cisco.
* **Destino de Multicast:** 01:00:0c:cc:cc:cc (Dirección física oficial reservada para el tráfico de control de Cisco en capa de enlace).
* **Campos TLV (Type-Length-Value) Generados:**
* **Device ID:** Nombres aleatorios con prefijo SW_Falso_.
* **Port ID:** Puertos de origen falsos (ej. GigabitEthernet0/15).
* **IP Address:** Direcciones IPv4 generadas de forma aleatoria para emular interfaces de gestión.
* **Capabilities & Platform:** Simulación de modelos Cisco de gama media (ej. WS-C2960).



---

## 4. Documentación del Funcionamiento del Script

El script carga de manera dinámica el módulo de contribución CDP de Scapy. A través de un bucle continuo (while True), genera valores de hardware e IP aleatorios en cada ciclo para simular nuevos vecinos legítimos de Cisco.

Las variables se introducen en las estructuras de datos de tipo TLV (DeviceID, Address, PortID, Capabilities, SoftwareVersion, Platform), las cuales son empaquetadas dentro de un formato SNAP con identificador de protocolo Cisco (0x2000) sobre un encabezado LLC (dsap=0xaa, ssap=0xaa). Las tramas resultantes son inyectadas a alta velocidad directo a la interfaz del switch, forzándolo a registrar y mantener en la memoria RAM cientos de vecinos falsos en cuestión de segundos, saturando los recursos asignados a este protocolo.

---

## 5. Documentación de la Red y Topología

### Detalles de Infraestructura:

* **Entorno de Simulación:** PNetLab
* **Switch Principal:** SW1-CISCO (Cisco vIOS L2 / IOL)
* **Interfaz de Conexión del Atacante:** Ethernet0/1
* **Segmento de Red:** VLAN 10 (Datos)
* **Direccionamiento IP de Prueba:** 192.168.10.0/24

---

## 6. Documentación de la Contra-medida (Mitigación)

Para mitigar de raíz esta vulnerabilidad en la capa de enlace de datos, se aplicó la desactivación selectiva del protocolo en los puertos de acceso perimetrales.

### Comandos de Configuración Aplicados:

```cisconet
SW1-CISCO# configure terminal
SW1-CISCO(config)# interface Ethernet0/1
SW1-CISCO(config-if)# no cdp enable
SW1-CISCO(config-if)# end

```

### Justificación Técnica de la Defensa:

* **no cdp enable:** Detiene por completo el procesamiento y la recepción de tramas destinadas a la dirección multicast de control 01:00:0c:cc:cc:cc de forma exclusiva en la interfaz física seleccionada.
* **Mitigación del agotamiento de memoria:** Al no procesar los paquetes maliciosos entrantes, el switch simplemente los descarta en el puerto, evitando la inyección de vecinos falsos en la RAM y estabilizando el consumo de CPU.
* **Bloqueo de fuga de información:** Evita que dispositivos no autorizados conectados a puertos de acceso reciban actualizaciones periódicas de CDP, protegiendo datos sensibles como el nombre del switch, el modelo de hardware y la dirección IP de administración.
