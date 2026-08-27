# Iconos para Home Assistant

## Estructura de Iconos

Para que el logo aparezca en Home Assistant, los archivos deben estar en:

```
custom_components/coto_digital/
└── icons/
    ├── icon.png      (512x512 recomendado)
    └── icon@2x.png   (alta resolución, opcional)
```

## Archivos Creados

✅ `icons/icon.png` - Logo principal (17KB, 512x512)
✅ `icons/icon@2x.png` - Versión alta resolución

## Configuración

Home Assistant buscará automáticamente el icono en `icons/icon.png`.

### Tamaños Recomendados

- **icon.png**: 256x256 o 512x512
- **icon@2x.png**: 512x512 o 1024x1024 (para pantallas retina)

## Reiniciar Home Assistant

Después de actualizar los iconos:

1. Copiar archivos a `/config/custom_components/coto_digital/icons/`
2. Reiniciar Home Assistant
3. Limpiar caché del navegador (Ctrl+Shift+R)
4. El logo aparecerá en:
   - Configuración → Dispositivos y servicios
   - Tarjetas de entidades
   - Dashboard HACS

## Verificación

```bash
# Verificar que los iconos existan
ls -lh /config/custom_components/coto_digital/icons/

# Debería mostrar:
# icon.png
# icon@2x.png
```

## Troubleshooting

### El icono no aparece

1. **Limpiar caché del navegador**:
   - Chrome: Ctrl+Shift+R
   - Firefox: Ctrl+F5
   - Safari: Cmd+Shift+R

2. **Verificar permisos**:
   ```bash
   chmod 644 /config/custom_components/coto_digital/icons/*.png
   chown homeassistant:homeassistant /config/custom_components/coto_digital/icons/*.png
   ```

3. **Reiniciar HA completamente**:
   ```bash
   ha core restart
   ```

4. **Verificar logs**:
   ```bash
   grep -i "icon\|coto_digital" /config/home-assistant.log
   ```

### "Icon not available"

Si sigue mostrando "Icon not available":

1. Verificar que el archivo `icons/icon.png` existe
2. Verificar que el PNG es válido:
   ```bash
   file icons/icon.png
   # Debe decir: PNG image data, 512 x 512
   ```

3. Asegurarse de que la integración está instalada en:
   `/config/custom_components/coto_digital/`

4. Recargar la integración:
   - Configuración → Dispositivos y servicios
   - Coto Digital → ⋮ → Recargar

## Formato del Icono

El icono actual:
- **Formato**: PNG con transparencia (RGBA)
- **Tamaño**: 512x512 píxeles
- **Peso**: 17KB
- **Fondo**: Transparente con círculo rojo
- **Diseño**: Carrito minimalista blanco

Perfect para Home Assistant ✓

## Alternativa: Icono de Material Design

Si prefieres usar un icono de MDI en lugar de custom:

Editar `manifest.json`:
```json
{
  "domain": "coto_digital",
  "name": "Coto Digital",
  "icon": "mdi:cart",
  ...
}
```

Pero el icono custom (logo.png) es más profesional y único.
