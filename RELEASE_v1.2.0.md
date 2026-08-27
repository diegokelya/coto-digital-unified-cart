# v1.2.0 - Dashboard Creation Fix + Validation Tools

## 🔧 Critical Fix - Dashboard Creation

Esta versión soluciona el problema de creación automática del dashboard.

### Problema Resuelto

El dashboard **no se creaba automáticamente** al instalar la integración debido a:
- Dependencia en `lovelace.dashboard` API que no siempre está disponible
- Timing issues durante la inicialización de HA

### Solución Implementada

✅ **Nueva implementación simplificada**:
- Usa `homeassistant.helpers.storage` directamente
- No depende de módulos lovelace internos
- Crea `.storage/lovelace.coto-digital` inmediatamente
- Registra en `lovelace_dashboards` para visibilidad en sidebar

### Nuevas Herramientas de Validación

#### 1. Test Unitario (`tests/test_dashboard.py`)

Valida la lógica sin necesidad de HA:

```bash
python3 tests/test_dashboard.py
```

#### 2. Validador en Runtime (`tests/validate_dashboard.py`)

Ejecutar **en el servidor de Home Assistant**:

```bash
python3 /config/tests/validate_dashboard.py
```

Verifica:
- ✓ Integración instalada
- ✓ Integración cargada
- ✓ Entidades creadas
- ✓ Dashboard en storage
- ✓ Dashboard registrado

#### 3. Creador Manual (`create_dashboard_manual.py`)

Si la creación automática falla:

```bash
python3 /config/custom_components/coto_digital/create_dashboard_manual.py
```

Crea el dashboard directamente en `.storage/`

---

## Instalación / Actualización

### Vía HACS

1. HACS → Integraciones → Coto Digital
2. Actualizar a v1.2.0
3. Reiniciar Home Assistant
4. Dashboard disponible en `/lovelace/coto-digital`

### Manual

1. Descargar `coto_digital.zip`
2. Extraer a `/config/custom_components/`
3. Reiniciar HA
4. Agregar integración desde UI

---

## Verificación Post-Instalación

**Opción 1: Automática (recomendado)**

Ejecutar el validador en HA:

```bash
wget https://raw.githubusercontent.com/diegokelya/coto-digital-unified-cart/v1.2.0/tests/validate_dashboard.py
python3 validate_dashboard.py
```

**Opción 2: Manual**

1. Verificar archivo existe:
   ```bash
   ls -la /config/.storage/lovelace.coto-digital
   ```

2. Acceder al dashboard:
   ```
   http://homeassistant.local:8123/lovelace/coto-digital
   ```

3. Si no aparece en sidebar:
   - Configuración → Dashboards
   - Buscar "Coto Digital"
   - Activar "Mostrar en barra lateral"

---

## Troubleshooting

Si el dashboard **aún no aparece** después de actualizar:

1. **Habilitar debug logging**:
   ```yaml
   logger:
     logs:
       custom_components.coto_digital.dashboard: debug
   ```

2. **Verificar logs**:
   ```bash
   grep -i "coto.*dashboard" /config/home-assistant.log
   ```
   
   Buscar:
   - `Starting Coto Digital dashboard creation`
   - `Successfully created Coto Digital dashboard`

3. **Crear manualmente**:
   ```bash
   python3 /config/custom_components/coto_digital/create_dashboard_manual.py
   ```

4. **Reiniciar HA**

---

## Documentación

- **DASHBOARD_VALIDATION.md** - Guía completa de troubleshooting
- **tests/README.md** - Documentación de herramientas de test

---

## Cambios en el Código

```python
# Antes (problemático)
lovelace_config = hass.data.get("lovelace")  # Puede ser None
dashboards = dashboard.LovelaceConfig.async_get_dashboards(hass)

# Ahora (confiable)
from homeassistant.helpers import storage
store = storage.Store(hass, 1, "lovelace.coto-digital")
await store.async_save(lovelace_data)
```

---

## Archivos Nuevos

- `tests/test_dashboard.py` - Unit tests
- `tests/validate_dashboard.py` - Runtime validator
- `tests/README.md` - Docs de testing
- `custom_components/coto_digital/create_dashboard_manual.py` - Creador manual
- `DASHBOARD_VALIDATION.md` - Guía troubleshooting

## Archivos Modificados

- `custom_components/coto_digital/dashboard.py` - Fix creación

---

🇦🇷 **Hecho en Argentina** | MIT License
