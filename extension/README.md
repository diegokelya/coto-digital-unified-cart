# Hermes — Cargador de carrito Coto

Extensión local para cargar en Coto Digital los productos preparados en el dashboard de Home Assistant.

## Instalación en Chrome/Edge

1. Descomprimir `hermes-coto-loader.zip`.
2. Abrir `chrome://extensions` (o `edge://extensions`).
3. Activar **Modo de desarrollador**.
4. Elegir **Cargar extensión sin empaquetar** y seleccionar la carpeta descomprimida.
5. Volver al dashboard y pulsar **Cargar en Coto**.

La extensión no guarda usuario ni contraseña, no accede a pagos y no confirma compras. Solo conserva la lista pendiente en `chrome.storage.session`, que se elimina al cerrar el navegador o al completar la carga.
