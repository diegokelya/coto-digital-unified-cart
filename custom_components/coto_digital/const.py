"""Constants for the Coto Digital integration."""

DOMAIN = "coto_digital"
CONF_UPDATE_INTERVAL = "update_interval"
DEFAULT_UPDATE_INTERVAL = 300  # 5 minutos

# URLs de Coto Digital
COTO_BASE_URL = "https://www.cotodigital3.com.ar"
COTO_SEARCH_URL = f"{COTO_BASE_URL}/sitios/cdigi/browse/search"

# Base de datos
DB_NAME = "coto_carrito.db"

# Atributos
ATTR_PRODUCTO_ID = "producto_id"
ATTR_NOMBRE = "nombre"
ATTR_PRECIO = "precio"
ATTR_IMAGEN_URL = "imagen_url"
ATTR_CANTIDAD = "cantidad"
ATTR_TOTAL = "total"

# Servicios
SERVICE_BUSCAR = "buscar_producto"
SERVICE_AGREGAR = "agregar_al_carrito"
SERVICE_ELIMINAR = "eliminar_del_carrito"
SERVICE_VACIAR = "vaciar_carrito"
SERVICE_SINCRONIZAR = "sincronizar"

# Sensores
SENSOR_CARRITO_COUNT = "carrito_count"
SENSOR_CARRITO_TOTAL = "carrito_total"
