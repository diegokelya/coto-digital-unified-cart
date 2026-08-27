# Coto Digital para Home Assistant

Integración completa de Coto Digital para Home Assistant.

## Características

- 🛒 **Gestión de carrito**: Agrega, elimina y administra productos
- 🔍 **Búsqueda de productos**: Busca en el catálogo de Coto Digital
- 📊 **Sensores**: Total en pesos, cantidad de productos y unidades
- 🔘 **Botones**: Vaciar carrito y sincronizar con un clic
- 📡 **Servicios**: Automatiza compras con servicios HA
- 🗄️ **Base de datos local**: SQLite para persistencia

## Instalación vía HACS

1. Agregar este repositorio a HACS como repositorio custom
2. Buscar "Coto Digital" en HACS
3. Clic en "Download"
4. Reiniciar Home Assistant
5. Ir a Configuración → Dispositivos y servicios → Agregar integración
6. Buscar "Coto Digital"

## Sensores disponibles

- `sensor.coto_digital_productos` - Cantidad de productos diferentes
- `sensor.coto_digital_unidades` - Total de unidades
- `sensor.coto_digital_total` - Total en pesos (ARS)

## Servicios disponibles

### `coto_digital.buscar_producto`

Busca productos en Coto Digital.

```yaml
service: coto_digital.buscar_producto
data:
  query: "leche"
```

### `coto_digital.agregar_al_carrito`

Agrega un producto al carrito.

```yaml
service: coto_digital.agregar_al_carrito
data:
  producto_id: "prod_123"
  nombre: "Leche La Serenísima 1L"
  precio: 450.50
  cantidad: 2
```

### `coto_digital.eliminar_del_carrito`

Elimina un producto del carrito.

```yaml
service: coto_digital.eliminar_del_carrito
data:
  producto_id: "prod_123"
```

### `coto_digital.vaciar_carrito`

Vacía todo el carrito.

```yaml
service: coto_digital.vaciar_carrito
```

### `coto_digital.sincronizar`

Sincroniza con Coto Digital.

```yaml
service: coto_digital.sincronizar
```

## Ejemplo de automatización

```yaml
automation:
  - alias: "Recordar hacer compras"
    trigger:
      - platform: time
        at: "19:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.coto_digital_productos
        above: 0
    action:
      - service: notify.mobile_app
        data:
          message: "Tienes {{ states('sensor.coto_digital_productos') }} productos en tu carrito de Coto"
```

## Configuración

La integración se configura desde la UI de Home Assistant. No requiere archivos YAML.

## Soporte

Para reportar problemas o sugerir mejoras, visita:
https://github.com/diegokelya/coto-digital-unified-cart/issues
