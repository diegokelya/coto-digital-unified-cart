# Testing y Validación - Coto Digital

Scripts para validar y debuggear la integración.

## Scripts de test

### 1. Test de Dashboard (Unit Tests)

```bash
cd tests/
python3 test_dashboard.py
```

Ejecuta tests unitarios de la funcionalidad de creación de dashboard:
- Validación de configuración
- Creación básica
- Manejo de dashboard existente
- Creación de storage

### 2. Validación de Dashboard (En HA)

**Ejecutar en el servidor de Home Assistant:**

```bash
# Desde el contenedor de HA o servidor
python3 /config/custom_components/coto_digital/../../../tests/validate_dashboard.py
```

O copiar el script directamente:

```bash
# Copiar script al servidor
scp tests/validate_dashboard.py user@ha-server:/config/

# Ejecutar en HA
ssh user@ha-server
python3 /config/validate_dashboard.py
```

**Verifica:**
- ✓ Integración instalada
- ✓ Integración cargada en HA
- ✓ Entidades creadas
- ✓ Dashboard en storage
- ✓ Dashboard registrado

### 3. Creación Manual de Dashboard

Si la creación automática falla:

```bash
# En el servidor de HA
python3 /config/custom_components/coto_digital/create_dashboard_manual.py
```

Crea manualmente:
- Archivo de dashboard en `.storage/lovelace.coto-digital`
- Registro en `lovelace_dashboards`

## Troubleshooting

### Dashboard no aparece

1. **Verificar integración cargada:**
   ```
   Configuración → Dispositivos y servicios → Buscar "Coto Digital"
   ```

2. **Verificar archivo de dashboard:**
   ```bash
   ls -la /config/.storage/lovelace.coto-digital
   ```

3. **Ejecutar validación:**
   ```bash
   python3 validate_dashboard.py
   ```

4. **Crear manualmente si falla:**
   ```bash
   python3 /config/custom_components/coto_digital/create_dashboard_manual.py
   ```

5. **Reiniciar Home Assistant**

### Verificar logs

```bash
# Ver logs de la integración
grep -i "coto" /config/home-assistant.log

# Ver logs específicos de dashboard
grep -i "dashboard" /config/home-assistant.log | grep -i coto
```

### Dashboard existe pero no en sidebar

1. Ir a **Configuración → Dashboards**
2. Buscar "Coto Digital"
3. Clic en el dashboard
4. Activar "Mostrar en barra lateral"
5. Refrescar navegador

### Recrear dashboard

```bash
# Eliminar dashboard existente
rm /config/.storage/lovelace.coto-digital

# Recrear
python3 /config/custom_components/coto_digital/create_dashboard_manual.py

# Reiniciar HA
```

## Estructura de archivos de dashboard

### `.storage/lovelace.coto-digital`

```json
{
  "version": 1,
  "minor_version": 1,
  "key": "lovelace.coto-digital",
  "data": {
    "config": {
      "views": [
        {
          "title": "Coto Digital",
          "path": "coto-digital",
          "cards": [...]
        }
      ]
    }
  }
}
```

### `.storage/lovelace_dashboards`

```json
{
  "data": {
    "items": [
      {
        "id": "coto_digital_...",
        "url_path": "coto-digital",
        "title": "Coto Digital",
        "icon": "mdi:cart",
        "show_in_sidebar": true
      }
    ]
  }
}
```

## Debugging avanzado

### Habilitar debug logging

Agregar a `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.coto_digital: debug
    custom_components.coto_digital.dashboard: debug
```

Reiniciar HA y revisar logs:

```bash
tail -f /config/home-assistant.log | grep coto_digital
```

### Verificar creación en código

El dashboard se crea en `__init__.py` línea ~75:

```python
# Crear dashboard automáticamente
await async_create_dashboard(hass)
```

Verificar que esta línea se ejecute revisando logs con debug habilitado.

## Reporte de bugs

Si los tests fallan, reportar issue con:

1. Output de `validate_dashboard.py`
2. Logs de HA con debug habilitado
3. Versión de Home Assistant
4. Método de instalación (HACS/manual)

GitHub Issues: https://github.com/diegokelya/coto-digital-unified-cart/issues
