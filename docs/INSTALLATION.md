# Coto Digital - Guía de instalación y uso

## Instalación vía HACS

### Paso 1: Agregar repositorio custom

1. Abrir HACS en Home Assistant
2. Clic en los tres puntos (⋮) en la esquina superior derecha
3. Seleccionar "Custom repositories"
4. Agregar:
   - **URL**: `https://github.com/diegokelya/coto-digital-unified-cart`
   - **Categoría**: `Integration`
5. Clic en "Add"

### Paso 2: Instalar integración

1. En HACS, ir a la sección "Integrations"
2. Buscar "Coto Digital"
3. Clic en "Download"
4. Seleccionar la última versión
5. Reiniciar Home Assistant

### Paso 3: Configurar integración

1. Ir a **Configuración → Dispositivos y servicios**
2. Clic en **"+ Agregar integración"**
3. Buscar **"Coto Digital"**
4. Seguir el asistente:
   - Nombre: Coto Digital (o personalizar)
   - Intervalo de actualización: 300 segundos (5 minutos)
5. Clic en "Enviar"

### Paso 4: Verificar instalación

#### Sensores creados

- `sensor.coto_digital_productos` - Cantidad de productos
- `sensor.coto_digital_unidades` - Total de unidades
- `sensor.coto_digital_total` - Total en pesos (ARS)

#### Botones creados

- `button.vaciar_carrito_coto_digital`
- `button.sincronizar_coto_digital`

#### Dashboard automático

Se crea automáticamente en: **`/lovelace/coto-digital`**

Para acceder:
1. Ir al menú lateral de Home Assistant
2. Buscar "Coto Digital" en la barra lateral
3. O navegar directamente a: `http://TU_HA_IP:8123/lovelace/coto-digital`

Si no aparece en el menú lateral:
1. Ir a Configuración → Dashboards
2. Buscar "Coto Digital"
3. Activar "Mostrar en barra lateral"

## Uso básico

### Buscar productos

**Vía servicio:**

1. Ir a Herramientas de desarrollo → Servicios
2. Servicio: `coto_digital.buscar_producto`
3. YAML:
   ```yaml
   service: coto_digital.buscar_producto
   data:
     query: "leche"
   ```
4. Llamar servicio

**Vía automatización:**

```yaml
automation:
  - alias: "Buscar leche los lunes"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: time
        weekday:
          - mon
    action:
      - service: coto_digital.buscar_producto
        data:
          query: "leche la serenisima"
```

### Agregar productos al carrito

```yaml
service: coto_digital.agregar_al_carrito
data:
  producto_id: "prod_123456"
  nombre: "Leche La Serenísima Entera 1L"
  precio: 450.50
  cantidad: 2
  imagen_url: "https://www.cotodigital3.com.ar/images/producto.jpg"
```

### Eliminar productos

```yaml
service: coto_digital.eliminar_del_carrito
data:
  producto_id: "prod_123456"
```

### Vaciar carrito

**Desde el dashboard:**
- Clic en el botón "Vaciar Carrito"

**Vía servicio:**
```yaml
service: coto_digital.vaciar_carrito
```

### Sincronizar con Coto Digital

**Desde el dashboard:**
- Clic en el botón "Sincronizar"

**Vía servicio:**
```yaml
service: coto_digital.sincronizar
```

## Automatizaciones

### Recordatorio diario

```yaml
automation:
  - alias: "Recordar compras Coto Digital"
    trigger:
      - platform: time
        at: "19:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.coto_digital_productos
        above: 0
    action:
      - service: notify.mobile_app_iphone_de_diego
        data:
          title: "🛒 Carrito Coto Digital"
          message: >
            Tienes {{ states('sensor.coto_digital_productos') }} productos
            por un total de ${{ states('sensor.coto_digital_total') }}
```

### Alerta de carrito grande

```yaml
automation:
  - alias: "Alerta carrito grande"
    trigger:
      - platform: numeric_state
        entity_id: sensor.coto_digital_total
        above: 50000
    action:
      - service: notify.mobile_app_iphone_de_diego
        data:
          title: "⚠️ Carrito Grande"
          message: "Tu carrito supera los $50.000"
```

### Sincronización automática

```yaml
automation:
  - alias: "Sincronizar Coto cada 6 horas"
    trigger:
      - platform: time_pattern
        hours: "/6"
    action:
      - service: button.press
        target:
          entity_id: button.sincronizar_coto_digital
```

## Dashboard personalizado

### Importar dashboard

1. Ir a Configuración → Dashboards
2. Clic en "+ Agregar dashboard"
3. Nombre: "Coto Digital"
4. Icono: `mdi:cart`
5. Guardar
6. Editar dashboard → Vista YAML
7. Copiar contenido de `custom_components/coto_digital/lovelace_dashboard.yaml`
8. Pegar y guardar

### Cards recomendadas

#### Gauge de total

```yaml
type: gauge
entity: sensor.coto_digital_total
name: Total del Carrito
min: 0
max: 100000
needle: true
severity:
  green: 0
  yellow: 30000
  red: 70000
```

#### Historial gráfico

```yaml
type: history-graph
title: Historial de Total
entities:
  - sensor.coto_digital_total
hours_to_show: 168
```

## Base de datos

La integración crea automáticamente una base de datos SQLite en:

```
/config/custom_components/coto_digital/data/coto_carrito.db
```

### Estructura

#### Tabla `carrito`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | ID autoincremental |
| producto_id | TEXT | ID único del producto |
| nombre | TEXT | Nombre del producto |
| precio | REAL | Precio unitario |
| imagen_url | TEXT | URL de la imagen |
| cantidad | INTEGER | Cantidad de unidades |
| fecha_agregado | TIMESTAMP | Fecha de agregado |

#### Tabla `historial_busquedas`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | ID autoincremental |
| query | TEXT | Término de búsqueda |
| resultados_count | INTEGER | Cantidad de resultados |
| timestamp | TIMESTAMP | Fecha de búsqueda |

### Consultar la base de datos

```bash
sqlite3 /config/custom_components/coto_digital/data/coto_carrito.db

# Ver productos en el carrito
SELECT * FROM carrito;

# Ver historial de búsquedas
SELECT * FROM historial_busquedas ORDER BY timestamp DESC LIMIT 10;

# Total del carrito
SELECT SUM(precio * cantidad) as total FROM carrito;
```

## Solución de problemas

### Dashboard no aparece en la barra lateral

1. Ir a Configuración → Dashboards
2. Buscar "Coto Digital"
3. Clic en el dashboard
4. Activar "Mostrar en barra lateral"

### Sensores no actualizan

1. Verificar que la integración esté activa en Dispositivos y servicios
2. Reiniciar Home Assistant
3. Verificar logs en Configuración → Sistema → Logs

### Error al buscar productos

Verificar conexión a internet y acceso a `www.cotodigital3.com.ar`

### Base de datos corrupta

```bash
# Backup
cp /config/custom_components/coto_digital/data/coto_carrito.db \
   /config/custom_components/coto_digital/data/coto_carrito.db.backup

# Verificar integridad
sqlite3 /config/custom_components/coto_digital/data/coto_carrito.db \
   "PRAGMA integrity_check;"

# Si está corrupta, eliminar y recrear
rm /config/custom_components/coto_digital/data/coto_carrito.db
# Reiniciar HA - se recrea automáticamente
```

## Desinstalación

1. Ir a Configuración → Dispositivos y servicios
2. Buscar "Coto Digital"
3. Clic en los tres puntos → Eliminar
4. Ir a HACS → Integraciones
5. Buscar "Coto Digital" → Eliminar
6. Reiniciar Home Assistant

El dashboard permanece después de desinstalar. Para eliminarlo:

1. Configuración → Dashboards
2. Buscar "Coto Digital"
3. Clic en los tres puntos → Eliminar

## Soporte

Para problemas o preguntas:

- **Issues**: https://github.com/diegokelya/coto-digital-unified-cart/issues
- **Documentación**: https://github.com/diegokelya/coto-digital-unified-cart

## Actualización

1. Ir a HACS → Integraciones
2. Buscar "Coto Digital"
3. Si hay actualización disponible, clic en "Actualizar"
4. Reiniciar Home Assistant
