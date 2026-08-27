# Mostrar el Logo en Home Assistant

## Problema
El logo muestra "**icon not available**" en Home Assistant.

## Solución Implementada ✅

### Archivos Creados

```
custom_components/coto_digital/
└── icons/
    ├── icon.png         (512x512, logo principal)
    ├── icon@2x.png      (512x512, alta resolución)
    └── README.md        (documentación)
```

Home Assistant buscará automáticamente estos archivos.

---

## Pasos para que Aparezca el Logo

### 1. Actualizar la Integración

**Vía HACS**:
```
1. HACS → Integraciones
2. Coto Digital → Actualizar
3. Seleccionar última versión (incluye iconos)
4. Descargar
```

**Manual**:
```bash
# Los archivos de iconos ya están en el repositorio
# Solo actualiza normalmente y estarán incluidos
```

### 2. Reiniciar Home Assistant

```bash
# Desde la UI
Configuración → Sistema → Reiniciar

# O desde terminal
ha core restart
```

### 3. Limpiar Caché del Navegador

**Chrome / Edge**:
- `Ctrl + Shift + R` (Windows/Linux)
- `Cmd + Shift + R` (Mac)

**Firefox**:
- `Ctrl + F5` (Windows/Linux)
- `Cmd + Shift + R` (Mac)

**Safari**:
- `Cmd + Option + R`

### 4. Recargar la Integración (Opcional)

```
1. Configuración → Dispositivos y servicios
2. Buscar "Coto Digital"
3. Clic en ⋮ (tres puntos)
4. Seleccionar "Recargar"
```

---

## Dónde Aparecerá el Logo

Una vez configurado, el logo aparecerá en:

✅ **Configuración → Dispositivos y servicios**
- Card de la integración Coto Digital

✅ **HACS → Integraciones**
- Listado de integraciones instaladas

✅ **Cards de entidades**
- Cuando se muestran sensores y botones

✅ **Dashboard de integración**
- Si usas el dashboard automático

---

## Verificación

### Comprobar que los archivos existen

```bash
# En el servidor de HA
ls -lh /config/custom_components/coto_digital/icons/

# Debería mostrar:
# -rw-r--r-- 1 homeassistant homeassistant 17K icon.png
# -rw-r--r-- 1 homeassistant homeassistant 17K icon@2x.png
```

### Comprobar formato del icono

```bash
file /config/custom_components/coto_digital/icons/icon.png

# Debería decir:
# PNG image data, 512 x 512, 8-bit/color RGBA, non-interlaced
```

---

## Troubleshooting

### El icono sigue sin aparecer

#### 1. Verificar permisos

```bash
chmod 644 /config/custom_components/coto_digital/icons/*.png
chown homeassistant:homeassistant /config/custom_components/coto_digital/icons/*.png
```

#### 2. Verificar estructura de directorios

```bash
tree /config/custom_components/coto_digital/

# Debe incluir:
# ├── icons/
# │   ├── icon.png
# │   └── icon@2x.png
```

#### 3. Limpiar caché de HA

```bash
# Parar HA
ha core stop

# Limpiar caché
rm -rf /config/.storage/lovelace*
rm -rf /config/www/.cache

# Reiniciar
ha core start
```

#### 4. Modo incógnito del navegador

Abrir Home Assistant en modo incógnito:
- `Ctrl + Shift + N` (Chrome)
- `Ctrl + Shift + P` (Firefox)

Si el icono aparece en incógnito, es problema de caché.

#### 5. Revisar logs

```bash
grep -i "icon\|coto_digital" /config/home-assistant.log | tail -20
```

Buscar errores relacionados con:
- "Failed to load icon"
- "Icon not found"
- "Permission denied"

---

## Tamaños de Iconos Recomendados

| Archivo | Tamaño | Uso |
|---------|--------|-----|
| `icon.png` | 512x512 | Pantallas normales |
| `icon@2x.png` | 512x512 o 1024x1024 | Pantallas Retina |

**Nuestro logo**: 512x512 en ambos (suficiente para cualquier pantalla)

---

## Formato Técnico

**Especificaciones del icono**:
- Formato: PNG
- Profundidad: 8-bit RGBA (con transparencia)
- Tamaño: 512x512 píxeles
- Peso: ~17KB
- Optimización: Compresión zlib nivel 9

**Compatible con**:
- ✅ Home Assistant Core 2023.1+
- ✅ HACS
- ✅ Navegadores modernos
- ✅ Pantallas HD y Retina

---

## Resultado Esperado

### Antes
```
┌─────────────────────────┐
│ [?] Coto Digital        │
│ Icon not available      │
└─────────────────────────┘
```

### Después
```
┌─────────────────────────┐
│ [🛒] Coto Digital       │
│ (logo del carrito rojo) │
└─────────────────────────┘
```

---

## Alternativa Temporal: Icono MDI

Si el icono custom no carga, puedes usar temporalmente un icono de Material Design:

Editar `manifest.json`:
```json
{
  "domain": "coto_digital",
  "name": "Coto Digital",
  "icon": "mdi:cart",
  ...
}
```

Pero **el icono custom es mucho mejor**:
- ✅ Único y reconocible
- ✅ Branding de Coto Digital
- ✅ Más profesional
- ✅ Colores corporativos

---

## Resumen

**Cambios realizados** ✅:
1. Creado directorio `icons/`
2. Copiado `logo.png` como `icon.png`
3. Creado `icon@2x.png` para retina
4. Actualizado `strings.json`
5. Documentación en `icons/README.md`

**Para que funcione**:
1. ✅ Actualizar integración a última versión
2. ✅ Reiniciar Home Assistant
3. ✅ Limpiar caché del navegador
4. ✅ Esperar ~1 minuto

**Tiempo total**: 3-5 minutos

El logo del **carrito minimalista rojo** aparecerá en toda la interfaz de Home Assistant.
