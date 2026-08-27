# v1.4.1 - Corrección del logo en Home Assistant

## Corrección

La versión 1.4.0 incluía el nuevo logo, pero los archivos añadidos posteriormente estaban en una carpeta `icons/` que Home Assistant no reconoce para el branding de integraciones.

La versión 1.4.1 usa la estructura oficial disponible desde Home Assistant 2026.3:

```text
custom_components/coto_digital/brand/
├── icon.png       # 256x256
└── icon@2x.png    # 512x512
```

## Cómo actualizar

1. HACS → Integraciones → Coto Digital.
2. Descargar v1.4.1.
3. Reiniciar Home Assistant.
4. Recargar el navegador.

No hay cambios funcionales ni de configuración.

## Compatibilidad

- Home Assistant 2026.3 o posterior: usa automáticamente el branding local.
- Versiones anteriores: requieren que el logo esté registrado en `home-assistant/brands` o actualizar Home Assistant.

Documentación: `docs/LOGO_EN_HA.md`.
