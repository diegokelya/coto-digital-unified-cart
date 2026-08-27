# Validación y Troubleshooting del Dashboard

## Problema reportado

El dashboard no se crea automáticamente al instalar la integración.

## Scripts de validación

Se crearon 3 scripts para diagnosticar y resolver el problema:

### 1. `tests/test_dashboard.py` - Tests unitarios

Valida la lógica de creación del dashboard sin necesidad de Home Assistant.

**Ejecutar:**

```bash
cd ~/projects/coto-digital-unified-cart
python3 tests/test_dashboard.py
```

**Qué verifica:**
- ✓ Configuración del dashboard (título, icono, cards)
- ✓ Lógica de creación básica
- ✓ Manejo de dashboard existente
- ✓ Creación de storage

**Output esperado:**
```
============================================================
COTO DIGITAL - Dashboard Creation Tests
============================================================

=== Testing Dashboard Configuration ===
✓ Dashboard config is valid
✓ Dashboard view has 5 cards
✓ All cards are valid

✓ TEST 1 PASSED: Dashboard configuration

...

✓ ALL TESTS PASSED
```

---

### 2. `tests/validate_dashboard.py` - Validación en HA

Verifica el estado del dashboard en un servidor de Home Assistant en ejecución.

**⚠️ Debe ejecutarse en el servidor de Home Assistant**

**Opción A: Ejecutar localmente en HA**

```bash
# Si tienes acceso directo al servidor HA
python3 /config/tests/validate_dashboard.py
```

**Opción B: Copiar y ejecutar vía SSH**

```bash
# Desde tu máquina local
scp ~/projects/coto-digital-unified-cart/tests/validate_dashboard.py user@HA_IP:/config/

# SSH al servidor
ssh user@HA_IP

# Ejecutar
python3 /config/validate_dashboard.py
```

**Qué verifica:**
- ✓ Integración instalada en `/config/custom_components/coto_digital`
- ✓ Integración cargada en `core.config_entries`
- ✓ Entidades creadas (sensores, botones)
- ✓ Dashboard en `.storage/lovelace.coto-digital`
- ✓ Dashboard registrado en `lovelace_dashboards`

**Output esperado (si todo está bien):**

```
============================================================
RESUMEN
============================================================
✓ PASS     Integración instalada
✓ PASS     Integración cargada
✓ PASS     Entidades creadas
✓ PASS     Configuración Lovelace
✓ PASS     Registro de dashboards

✓ DASHBOARD CREADO Y OPERATIVO

Acceder en:
  http://homeassistant.local:8123/lovelace/coto-digital
```

**Output si falla:**

```
============================================================
RESUMEN
============================================================
✓ PASS     Integración instalada
✓ PASS     Integración cargada
⚠ N/A      Entidades creadas
✗ FAIL     Configuración Lovelace

✗ DASHBOARD NO ENCONTRADO

[Muestra pasos manuales...]
```

---

### 3. `custom_components/coto_digital/create_dashboard_manual.py` - Creación manual

Si la creación automática falla, este script crea el dashboard manualmente.

**⚠️ Debe ejecutarse en el servidor de Home Assistant**

**Ejecutar:**

```bash
# En el servidor HA
python3 /config/custom_components/coto_digital/create_dashboard_manual.py
```

**Qué hace:**
1. Encuentra el directorio de configuración de HA
2. Crea `.storage/lovelace.coto-digital` con la configuración completa
3. Registra el dashboard en `lovelace_dashboards`
4. Muestra instrucciones para finalizar

**Output esperado:**

```
============================================================
CREACIÓN MANUAL DE DASHBOARD - COTO DIGITAL
============================================================

✓ Directorio de configuración: /config
✓ Dashboard creado: /config/.storage/lovelace.coto-digital
✓ Dashboard registrado en: /config/.storage/lovelace_dashboards

============================================================
✓ DASHBOARD CREADO EXITOSAMENTE
============================================================

Pasos finales:
1. Reiniciar Home Assistant
2. Ir a la barra lateral → Buscar 'Coto Digital'
3. O navegar a: http://TU_HA_IP:8123/lovelace/coto-digital
```

---

## Pasos de diagnóstico recomendados

### Paso 1: Verificar tests unitarios (local)

```bash
cd ~/projects/coto-digital-unified-cart
python3 tests/test_dashboard.py
```

Si falla aquí, hay un problema en la lógica del código.

### Paso 2: Validar en HA

```bash
# Copiar script a HA
scp tests/validate_dashboard.py user@HA_IP:/config/

# Ejecutar en HA
ssh user@HA_IP "python3 /config/validate_dashboard.py"
```

Esto muestra exactamente qué está faltando.

### Paso 3: Crear dashboard manualmente (si es necesario)

Si el paso 2 muestra que el dashboard no existe:

```bash
ssh user@HA_IP "python3 /config/custom_components/coto_digital/create_dashboard_manual.py"
```

Luego reiniciar Home Assistant.

### Paso 4: Verificar logs de HA

```bash
# En el servidor HA
grep -i "coto.*dashboard" /config/home-assistant.log

# O con debug habilitado
tail -f /config/home-assistant.log | grep -i coto
```

---

## Habilitar debug logging

Agregar a `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.coto_digital: debug
    custom_components.coto_digital.dashboard: debug
```

Reiniciar HA y buscar líneas como:

```
DEBUG (MainThread) [custom_components.coto_digital] Dashboard creation...
INFO (MainThread) [custom_components.coto_digital.dashboard] Successfully created Coto Digital dashboard
```

---

## Posibles causas del problema

### 1. Integración no cargada

**Verificar:**
```bash
grep "coto_digital" /config/.storage/core.config_entries
```

**Solución:**
- Ir a Configuración → Dispositivos y servicios
- Agregar integración "Coto Digital"

### 2. Error en creación de storage

**Verificar:**
```bash
ls -la /config/.storage/lovelace.coto-digital
```

**Solución:**
```bash
python3 /config/custom_components/coto_digital/create_dashboard_manual.py
```

### 3. Permisos incorrectos

**Verificar:**
```bash
ls -la /config/.storage/ | head -5
```

**Solución:**
```bash
# Ajustar permisos si es necesario
chown -R homeassistant:homeassistant /config/.storage/
```

### 4. Lovelace no está en modo storage

**Verificar** en `configuration.yaml`:
```yaml
lovelace:
  mode: storage  # Debe estar en modo storage
```

Si está en modo `yaml`, la creación automática no funcionará.

---

## Verificación post-creación

Después de crear el dashboard (automático o manual):

1. **Reiniciar Home Assistant**

2. **Verificar en barra lateral:**
   - Debería aparecer "Coto Digital" con ícono 🛒

3. **Acceder directamente:**
   ```
   http://homeassistant.local:8123/lovelace/coto-digital
   ```

4. **Si no aparece en sidebar:**
   - Configuración → Dashboards
   - Buscar "Coto Digital"
   - Activar "Mostrar en barra lateral"

---

## Reportar resultado

Por favor ejecutar los scripts y reportar:

1. Output de `test_dashboard.py` (local)
2. Output de `validate_dashboard.py` (en HA)
3. Si fue necesario usar `create_dashboard_manual.py`
4. Logs relevantes de `/config/home-assistant.log`

Esto ayudará a identificar si:
- La creación automática tiene un bug
- Falta alguna dependencia
- Hay un problema de permisos
- El problema es específico de tu instalación
