# v1.3.0 - Logo Profesional + Documentación de Actualización

## 🎨 Mejoras Visuales

### Logo Profesional Renovado

**Antes** (v1.0.0 - v1.2.0):
- Diseño básico de píxeles
- Fondo sólido rojo
- Sin efectos 3D
- 4KB PNG simple

**Ahora** (v1.3.0):
- ✅ **Carrito moderno 3D** con sombras y profundidad
- ✅ **Gradiente radial** (rojo Coto #E31837 → rojo oscuro #BD132D)
- ✅ **Check verde** (#4CAF50) - verificación/seguridad
- ✅ **Badge "AR"** - Argentina, identidad local
- ✅ **Ruedas detalladas** con efecto 3D
- ✅ **Esquinas redondeadas** - diseño moderno
- ✅ **14KB PNG optimizado** - mejor calidad sin sacrificar tamaño
- ✅ **SVG editable** incluido con efectos profesionales

**Archivos**:
- `logo.png` - 512x512, listo para HACS
- `logo.svg` - Vector escalable con gradientes y sombras

---

## 📚 Nueva Documentación

### docs/ACTUALIZACION.md

Guía completa de actualización con 3 métodos:

#### 1. Actualización vía HACS ⭐ Recomendado
- Paso a paso desde la interfaz
- Desde lista de integraciones
- Desde detalle de integración
- Screenshots y ejemplos

#### 2. Actualización Manual
- Descarga desde GitHub Releases
- Reemplazo de archivos
- Gestión de permisos
- Verificación de instalación

#### 3. Actualización vía Git (Desarrolladores)
- Pull y checkout de tags
- Actualización de archivos
- Workflow para contribuidores

### Verificación Post-Actualización
- Comprobar versión instalada
- Revisar logs de errores
- Validar entidades creadas
- Verificar dashboard funcional

### Notas de Versión Específicas
- **v1.0.0 → v1.1.0**: Dashboard automático añadido
- **v1.1.0 → v1.2.0**: Fix crítico creación dashboard
- **v1.2.0 → v1.3.0**: Logo profesional + docs

### Rollback
- Instrucciones para volver a versión anterior
- Vía HACS (reinstalar versión anterior)
- Manual (restaurar backup)

### Troubleshooting
- **Integration failed to load**: Permisos y archivos corruptos
- **Dashboard desaparece**: Recrear con script manual
- **Entidades no actualizan**: Recargar integración

### FAQ
- ¿Pierdo datos al actualizar? **No** - SQLite se mantiene
- ¿Debo reconfigurar? **No** - Config se preserva
- ¿Cuánto tarda? **2-3 minutos** (descarga + reinicio)

---

## 📝 CHANGELOG.md Completo

Nuevo archivo con historial completo de versiones:
- Formato [Keep a Changelog](https://keepachangelog.com)
- Versionado semántico
- Categorías: Añadido, Mejorado, Corregido, Seguridad
- Enlaces a cada release

---

## 🔄 Cómo Actualizar

### Desde HACS (2-3 minutos)

1. **HACS** → **Integraciones**
2. Buscar **"Coto Digital"**
3. Clic en **"Actualizar"**
4. Seleccionar **v1.3.0**
5. **Descargar**
6. **Configuración** → **Sistema** → **Reiniciar**
7. ✅ Listo - Logo y documentación actualizados

### Verificación

```bash
# Verificar versión
cat /config/custom_components/coto_digital/manifest.json | grep version

# Debería mostrar:
# "version": "1.3.0"

# Verificar logo
ls -lh /config/custom_components/coto_digital/../../logo.png

# Debería ser ~14KB
```

---

## 📊 Cambios Técnicos

### Archivos Modificados
- `custom_components/coto_digital/manifest.json` - Versión 1.3.0
- `logo.png` - Logo profesional 14KB
- `logo.svg` - Vector mejorado con efectos
- `README.md` - Enlaces a documentación

### Archivos Nuevos
- `docs/ACTUALIZACION.md` - Guía de actualización completa
- `CHANGELOG.md` - Historial de versiones

### Sin Cambios en Funcionalidad
- ✅ Mismos sensores (productos, unidades, total)
- ✅ Mismos botones (sincronizar, vaciar)
- ✅ Mismos servicios (buscar, agregar, eliminar, vaciar, sincronizar)
- ✅ Mismo dashboard (creación automática)
- ✅ Mismas automatizaciones de ejemplo

**No hay breaking changes** - actualización 100% segura.

---

## 🎯 Beneficios de Actualizar

### Visual
- Logo profesional en HACS store
- Mejor reconocimiento de marca
- Aspecto más pulido en listados

### Documentación
- Saber exactamente cómo actualizar en el futuro
- Troubleshooting fácil
- Historial de cambios claro

### Mantenimiento
- CHANGELOG para seguir evolución
- Notas de versión específicas
- Proceso de actualización documentado

---

## 📦 Compatibilidad

### Actualización desde:
- ✅ **v1.0.0** → v1.3.0 (directa, sin pasos intermedios)
- ✅ **v1.1.0** → v1.3.0 (directa)
- ✅ **v1.2.0** → v1.3.0 (directa)

### Requisitos:
- Home Assistant 2023.1.0+
- Python 3.11+
- HACS (opcional pero recomendado)

### Base de datos:
- No requiere migración
- SQLite compatible con todas las versiones

---

## 🆘 Soporte

Si tienes problemas actualizando:

1. **Leer**: [docs/ACTUALIZACION.md](https://github.com/diegokelya/coto-digital-unified-cart/blob/main/docs/ACTUALIZACION.md)
2. **Verificar**: Logs en `/config/home-assistant.log`
3. **Ejecutar**: Script de validación
   ```bash
   python3 /config/tests/validate_dashboard.py
   ```
4. **Reportar**: [GitHub Issues](https://github.com/diegokelya/coto-digital-unified-cart/issues)

---

## 🔗 Enlaces Útiles

- **Repositorio**: https://github.com/diegokelya/coto-digital-unified-cart
- **Documentación**: https://github.com/diegokelya/coto-digital-unified-cart#documentación
- **Releases**: https://github.com/diegokelya/coto-digital-unified-cart/releases
- **Issues**: https://github.com/diegokelya/coto-digital-unified-cart/issues

---

🇦🇷 **Hecho en Argentina** | MIT License | Versión 1.3.0
