# Mostrar el logo en Home Assistant

## Home Assistant 2026.3 o posterior

Las integraciones personalizadas pueden incluir sus imágenes directamente en una carpeta `brand/` dentro de la integración:

```text
custom_components/coto_digital/
├── manifest.json
└── brand/
    ├── icon.png       # 256x256
    └── icon@2x.png    # 512x512
```

No hay que agregar ninguna propiedad `icon` al `manifest.json`. Home Assistant detecta estos archivos automáticamente y les da prioridad sobre el CDN de Brands.

## Instalación de la corrección

1. En HACS, abrir Coto Digital.
2. Descargar la versión 1.4.1 o posterior.
3. Reiniciar Home Assistant completamente.
4. Recargar la página del navegador.

Verificación desde Terminal/SSH de Home Assistant:

```bash
ls -lh /config/custom_components/coto_digital/brand/
```

Deben existir `icon.png` e `icon@2x.png`.

## Si todavía aparece “Icon not available”

1. Confirmar en **Configuración → Acerca de** que Home Assistant sea 2026.3 o posterior.
2. Confirmar que el dominio sea exactamente `coto_digital`.
3. Confirmar que la ruta sea `brand/`, no `brands/` ni `icons/`.
4. Reiniciar Home Assistant; recargar solamente la integración puede no actualizar el frontend.
5. Hacer una recarga forzada del navegador o probar en una ventana privada.

No se debe borrar `.storage`, Lovelace ni otras cachés internas de Home Assistant para resolver el logo.

## Home Assistant anterior a 2026.3

Las versiones anteriores no admiten branding incluido dentro de una integración personalizada. Para ellas, el icono debe estar publicado en el repositorio central `home-assistant/brands`, bajo:

```text
custom_integrations/coto_digital/
├── icon.png
└── icon@2x.png
```

Eso requiere enviar y conseguir la aprobación de un pull request en:

https://github.com/home-assistant/brands

Como alternativa inmediata, actualizar Home Assistant a 2026.3 o posterior.

## Referencias oficiales

- Anuncio de Brands Proxy API: https://developers.home-assistant.io/blog/2026/02/24/brands-proxy-api
- Repositorio Home Assistant Brands: https://github.com/home-assistant/brands
