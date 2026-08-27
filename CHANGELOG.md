# Changelog

Todos los cambios notables del proyecto están documentados aquí.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [1.4.0] - 2026-08-27

### Mejorado
- Logo completamente rediseñado: minimalista y profesional
- Diseño flat/material design solo con carrito de compras
- Reducido a 2 colores: rojo Coto + blanco
- Líneas limpias y gruesas para mejor legibilidad
- Sin elementos innecesarios (badges, checks, efectos 3D)
- Perfecto para HACS store y cualquier tamaño
- Logo SVG optimizado con formas simples

### Visual
- Carrito wireframe blanco sobre fondo rojo
- Manija curva simple
- Dos ruedas limpias con centro rojo
- Gradiente radial suave en fondo
- 17KB PNG optimizado (512x512)

## [1.3.0] - 2026-08-27

### Añadido
- Logo profesional mejorado con efecto 3D y gradiente radial
- Documentación completa de actualización (docs/ACTUALIZACION.md)
- Logo SVG editable con efectos y sombras profesionales
- Enlaces a documentación en README

### Mejorado
- Diseño del logo: carrito 3D, check verde, badge AR
- Calidad visual del logo de 4KB a 14KB optimizado
- Gradiente radial en fondo (rojo Coto → oscuro)
- Ruedas con detalle 3D y efecto de profundidad

### Documentación
- Guía de actualización vía HACS, manual y Git
- Verificación post-actualización
- Notas de versión específicas
- Instrucciones de rollback
- FAQ de actualización

## [1.2.0] - 2026-08-27

### Corregido
- **CRÍTICO**: Dashboard ahora se crea correctamente al instalar la integración
- Uso directo de `homeassistant.helpers.storage` en lugar de API lovelace
- Mejor manejo de errores y logging en creación de dashboard

### Añadido
- `tests/test_dashboard.py` - Tests unitarios de dashboard
- `tests/validate_dashboard.py` - Validador runtime en HA
- `custom_components/coto_digital/create_dashboard_manual.py` - Creación manual
- `DASHBOARD_VALIDATION.md` - Guía completa de troubleshooting
- `tests/README.md` - Documentación de herramientas de test

### Mejorado
- Dashboard se guarda directamente en `.storage/lovelace.coto-digital`
- Registro en `lovelace_dashboards` para visibilidad en sidebar
- Logging detallado del proceso de creación

## [1.1.0] - 2026-08-27

### Añadido
- Dashboard Lovelace creado automáticamente al instalar
- 7 automatizaciones de ejemplo en `automations_example.yaml`
- `lovelace_dashboard.yaml` para importación manual
- Documentación completa de instalación (docs/INSTALLATION.md)
- `dashboard.py` módulo para creación automática

### Dashboard
- Estadísticas del carrito (productos, unidades, total)
- Botones de acción (sincronizar, vaciar)
- Gráfico histórico de totales (168 horas)
- Gauge visual del total
- Ejemplos de código de servicios

### Automatizaciones
- Recordatorio diario de compras (19:00)
- Alerta de carrito grande (>$50.000)
- Sincronización automática (cada 6 horas)
- Notificación al actualizar carrito
- Recordatorio semanal si carrito vacío
- Búsqueda automática productos favoritos (lunes 8:00)

## [1.0.0] - 2026-08-27

### Añadido
- Integración completa para Home Assistant vía HACS
- Config flow para configuración desde UI
- 3 sensores: productos, unidades, total (ARS)
- 2 botones: sincronizar, vaciar carrito
- 5 servicios: buscar, agregar, eliminar, vaciar, sincronizar
- API de Coto Digital con búsqueda de productos
- Base de datos SQLite para persistencia
- Traducciones español e inglés
- Metadata HACS (hacs.json, info.md)
- Logo inicial para HACS
- Documentación README completa

### Componentes
- `__init__.py` - Setup integración y servicios
- `config_flow.py` - Configuración UI
- `sensor.py` - Sensores con coordinator
- `button.py` - Botones de acción
- `coto_api.py` - API Coto Digital + SQLite
- `const.py` - Constantes
- `manifest.json` - Metadata integración
- `services.yaml` - Definición de servicios
- `strings.json` - Textos UI
- `translations/` - es.json, en.json

### Base de datos
- Tabla `carrito` - Productos en el carrito
- Tabla `historial_busquedas` - Historial de búsquedas
- Inicialización automática al instalar

---

## Tipos de cambios

- **Añadido** - para nuevas funcionalidades
- **Mejorado** - para cambios en funcionalidad existente
- **Obsoleto** - para características que pronto se eliminarán
- **Eliminado** - para características eliminadas
- **Corregido** - para corrección de bugs
- **Seguridad** - en caso de vulnerabilidades

## Enlaces

- [1.3.0]: https://github.com/diegokelya/coto-digital-unified-cart/releases/tag/v1.3.0
- [1.2.0]: https://github.com/diegokelya/coto-digital-unified-cart/releases/tag/v1.2.0
- [1.1.0]: https://github.com/diegokelya/coto-digital-unified-cart/releases/tag/v1.1.0
- [1.0.0]: https://github.com/diegokelya/coto-digital-unified-cart/releases/tag/v1.0.0
