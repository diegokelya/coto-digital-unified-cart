# Actualización de Versión - Coto Digital HACS

Guía completa para actualizar la integración a una nueva versión.

## Método 1: Actualización vía HACS (Recomendado)

### Desde la interfaz de Home Assistant

#### Paso 1: Verificar si hay actualizaciones disponibles

1. Abrir **HACS** en el menú lateral de Home Assistant
2. Ir a la sección **Integraciones**
3. Buscar **"Coto Digital"** en la lista
4. Si hay actualización disponible, verás un badge **"Actualización disponible"** o un número de versión en rojo

#### Paso 2: Actualizar

**Opción A: Desde la lista de integraciones**

1. En HACS → Integraciones
2. Localizar "Coto Digital"
3. Si hay actualización, clic en el card
4. Clic en **"Actualizar"** o **"Update"**
5. Seleccionar la versión (normalmente la última)
6. Clic en **"Descargar"** o **"Download"**
7. Esperar a que descargue

**Opción B: Desde el detalle de la integración**

1. HACS → Integraciones → Clic en "Coto Digital"
2. Verás un banner de actualización en la parte superior
3. Clic en **"Actualizar a v1.X.X"**
4. Confirmar descarga

#### Paso 3: Reiniciar Home Assistant

**⚠️ IMPORTANTE**: Los cambios solo se aplican después de reiniciar

1. Ir a **Configuración** → **Sistema**
2. Clic en **"Reiniciar"** en la esquina superior derecha
3. Seleccionar **"Reiniciar Home Assistant"**
4. Esperar 1-2 minutos a que reinicie

#### Paso 4: Verificar la actualización

1. Ir a **Configuración** → **Dispositivos y servicios**
2. Buscar **"Coto Digital"**
3. Clic en la integración
4. En la esquina superior derecha, verás la versión instalada

---

## Método 2: Actualización Manual

Si HACS no detecta la actualización o prefieres hacerlo manualmente.

### Paso 1: Descargar la nueva versión

**Desde GitHub Releases:**

1. Ir a: https://github.com/diegokelya/coto-digital-unified-cart/releases
2. Buscar la última versión (ej: v1.2.0)
3. En "Assets", descargar el archivo **Source code (zip)**

**Desde terminal:**

```bash
cd /tmp
wget https://github.com/diegokelya/coto-digital-unified-cart/archive/refs/tags/v1.2.0.zip
unzip v1.2.0.zip
```

### Paso 2: Reemplazar archivos

```bash
# Backup de la versión actual (recomendado)
cp -r /config/custom_components/coto_digital /config/custom_components/coto_digital.backup

# Eliminar versión anterior
rm -rf /config/custom_components/coto_digital

# Copiar nueva versión
cp -r /tmp/coto-digital-unified-cart-1.2.0/custom_components/coto_digital /config/custom_components/

# Verificar permisos
chown -R homeassistant:homeassistant /config/custom_components/coto_digital
```

### Paso 3: Reiniciar Home Assistant

```bash
# Desde terminal
ha core restart

# O desde la UI como en el Método 1
```

---

## Método 3: Actualización vía Git (Desarrolladores)

Si instalaste manualmente clonando el repositorio.

### Paso 1: Actualizar el repositorio

```bash
cd ~/coto-digital-unified-cart
git fetch --tags
git checkout v1.2.0  # O la versión que quieras
```

### Paso 2: Copiar archivos actualizados

```bash
cp -r custom_components/coto_digital /config/custom_components/
```

### Paso 3: Reiniciar HA

---

## Verificación Post-Actualización

### 1. Verificar versión instalada

```bash
# Desde terminal
cat /config/custom_components/coto_digital/manifest.json | grep version

# Debería mostrar:
# "version": "1.2.0"
```

### 2. Verificar logs

```bash
# Buscar errores después del reinicio
grep -i "coto_digital" /config/home-assistant.log | tail -20

# Si ves errores como "Import Error" o "Component failed to load", 
# puede que falten dependencias
```

### 3. Verificar entidades

1. Ir a **Herramientas de desarrollo** → **Estados**
2. Buscar `coto_digital`
3. Deberías ver:
   - `sensor.coto_digital_productos`
   - `sensor.coto_digital_unidades`
   - `sensor.coto_digital_total`
   - `button.sincronizar_coto_digital`
   - `button.vaciar_carrito_coto_digital`

### 4. Verificar dashboard

```bash
# Verificar que el dashboard existe
ls -la /config/.storage/lovelace.coto-digital

# Acceder en el navegador
http://homeassistant.local:8123/lovelace/coto-digital
```

---

## Notas de Actualización por Versión

### v1.0.0 → v1.1.0

**Cambios:**
- Agregado dashboard automático
- 7 automatizaciones de ejemplo

**Requiere:**
- Reinicio de HA
- El dashboard se crea automáticamente

---

### v1.1.0 → v1.2.0

**Cambios:**
- Fix crítico en creación de dashboard
- Herramientas de validación

**Requiere:**
- Reinicio de HA
- Si el dashboard no se había creado antes, se creará ahora

**Verificación recomendada:**

```bash
python3 /config/tests/validate_dashboard.py
```

---

## Rollback (Volver a versión anterior)

Si la nueva versión causa problemas:

### Vía HACS

1. HACS → Integraciones → Coto Digital
2. Clic en los tres puntos (⋮)
3. Seleccionar **"Reinstalar"**
4. Elegir la versión anterior de la lista
5. Descargar
6. Reiniciar HA

### Manual

```bash
# Restaurar backup
rm -rf /config/custom_components/coto_digital
cp -r /config/custom_components/coto_digital.backup /config/custom_components/coto_digital

# Reiniciar
ha core restart
```

---

## Troubleshooting

### "Integration failed to load" después de actualizar

**Causa**: Archivos corruptos o permisos incorrectos

**Solución**:
```bash
# Verificar permisos
ls -la /config/custom_components/coto_digital/

# Todos los archivos deben ser propiedad de homeassistant
# Si no, ejecutar:
chown -R homeassistant:homeassistant /config/custom_components/coto_digital/

# Reiniciar
ha core restart
```

### Dashboard desaparece después de actualizar

**Solución**:
```bash
# Verificar si el archivo existe
ls -la /config/.storage/lovelace.coto-digital

# Si no existe, recrear
python3 /config/custom_components/coto_digital/create_dashboard_manual.py

# Reiniciar HA
```

### Entidades no actualizan después de actualización

**Solución**:
1. Ir a Configuración → Dispositivos y servicios
2. Buscar "Coto Digital"
3. Clic en los tres puntos (⋮) → **"Recargar"**
4. Si no funciona, eliminar y volver a agregar la integración

---

## Actualizaciones Automáticas

HACS **no actualiza automáticamente** las integraciones custom. Debes hacerlo manualmente.

### Notificaciones de actualización

Para recibir notificaciones cuando hay actualizaciones:

1. Configurar en HACS:
   - HACS → Configuración
   - Activar "Mostrar notificaciones de actualización"

2. Crear automatización:

```yaml
automation:
  - alias: "Notificar actualización Coto Digital"
    trigger:
      - platform: state
        entity_id: update.coto_digital_update
        to: "on"
    action:
      - service: notify.mobile_app_iphone_de_diego
        data:
          title: "Actualización Disponible"
          message: "Hay una nueva versión de Coto Digital: {{ state_attr('update.coto_digital_update', 'latest_version') }}"
```

---

## Changelog y Release Notes

Siempre revisa las notas de la versión antes de actualizar:

**GitHub Releases**: https://github.com/diegokelya/coto-digital-unified-cart/releases

Cada release incluye:
- ✓ Cambios principales
- ✓ Bugs corregidos
- ✓ Nuevas características
- ✓ Cambios que rompen compatibilidad (breaking changes)
- ✓ Instrucciones especiales de actualización

---

## Preguntas Frecuentes

### ¿Pierdo datos al actualizar?

**No**. La base de datos SQLite (`coto_carrito.db`) se mantiene intacta.

### ¿Debo reconfigurar la integración?

**No**, normalmente. Solo si hay breaking changes indicados en el release.

### ¿Cuánto tarda la actualización?

- Descarga vía HACS: 10-30 segundos
- Reinicio de HA: 1-2 minutos
- **Total**: ~2-3 minutos

### ¿Puedo actualizar sin reiniciar?

**No**. Home Assistant requiere reinicio para cargar nuevos archivos de componentes.

---

## Contacto y Soporte

- **Issues**: https://github.com/diegokelya/coto-digital-unified-cart/issues
- **Releases**: https://github.com/diegokelya/coto-digital-unified-cart/releases
- **Documentación**: https://github.com/diegokelya/coto-digital-unified-cart
