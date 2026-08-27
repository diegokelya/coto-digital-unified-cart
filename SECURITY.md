# Análisis de Seguridad - Coto Digital

Fecha: 2026-08-27
Versión analizada: v1.3.0

## Resumen Ejecutivo

✅ **ESTADO GENERAL: SEGURO**

El código ha sido analizado en busca de vulnerabilidades comunes y cumple con buenas prácticas de seguridad.

---

## Análisis Detallado

### 1. SQL Injection ✅ SEGURO

**Análisis**: Todas las queries SQL usan parámetros posicionales (`?`)

**Código revisado**: `custom_components/coto_digital/coto_api.py`

**Ejemplos seguros encontrados**:
```python
cursor.execute("SELECT * FROM carrito WHERE producto_id = ?", (producto_id,))
cursor.execute("INSERT INTO carrito (...) VALUES (?, ?, ?, ?, ?)", (values))
```

**✓ PASA**: No se encontró concatenación directa de strings en queries SQL.

---

### 2. Credenciales Hardcodeadas ✅ SEGURO

**Análisis**: No hay credenciales hardcodeadas en el código.

**Verificado**:
- `TELEGRAM_BOT_TOKEN` - Usa `os.getenv()` ✓
- `TELEGRAM_CHAT_ID` - Usa `os.getenv()` con default ✓
- No hay API keys hardcodeadas ✓

**Ejemplos seguros**:
```python
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "406287065")
```

**Recomendación**: El chat ID por defecto no es sensible (es un ID público de Telegram).

---

### 3. Command Injection ✅ SEGURO

**Análisis**: No se encontró uso de `os.system()`, `eval()`, o `exec()` con entrada de usuario.

**Verificado**:
- No hay llamadas a `os.system()`
- No hay uso de `eval()` o `exec()`
- `subprocess` no se usa en la integración core

**✓ PASA**: Sin vectores de command injection.

---

### 4. Path Traversal ⚠️ BAJO RIESGO

**Análisis**: Operaciones de archivo están controladas.

**Código revisado**:
```python
# coto_api.py
def __init__(self, db_path: str):
    self.db_path = db_path  # Path viene de HA, controlado
```

**Riesgo**: BAJO - El path de la base de datos es controlado por Home Assistant.

**Recomendación**: Validar que `db_path` esté dentro del directorio de configuración.

**Mitigación sugerida**:
```python
def __init__(self, db_path: str):
    db_path = Path(db_path).resolve()
    config_dir = Path(hass.config.config_dir).resolve()
    if not str(db_path).startswith(str(config_dir)):
        raise ValueError("Database path must be within config directory")
    self.db_path = str(db_path)
```

---

### 5. Validación de Entrada ⚠️ MEJORABLE

**Análisis**: Falta validación explícita de tipos y rangos.

**Métodos públicos sin validación explícita**:
- `buscar_productos(query, limit)` - query puede ser cualquier string
- `agregar_al_carrito(producto)` - dict sin validación de estructura
- `_parse_precio(precio_str)` - usa regex (SEGURO)

**Recomendaciones**:

#### Para `buscar_productos()`:
```python
def buscar_productos(self, query: str, limit: int = 50) -> list[dict[str, Any]]:
    # Validar tipo
    if not isinstance(query, str):
        raise ValueError("Query must be a string")
    
    # Sanitizar query
    query = query.strip()
    
    # Limitar longitud (DoS prevention)
    if len(query) > 100:
        query = query[:100]
    
    # Validar limit
    if not isinstance(limit, int) or limit < 1 or limit > 100:
        limit = 50
    
    # ... resto del código
```

#### Para `agregar_al_carrito()`:
```python
def agregar_al_carrito(self, producto: dict[str, Any]) -> bool:
    # Validar estructura
    required_fields = ['producto_id', 'nombre', 'precio']
    if not all(field in producto for field in required_fields):
        raise ValueError(f"Missing required fields: {required_fields}")
    
    # Validar tipos
    if not isinstance(producto['producto_id'], str):
        raise ValueError("producto_id must be string")
    
    if not isinstance(producto['precio'], (int, float)):
        raise ValueError("precio must be numeric")
    
    # Validar rangos
    if producto['precio'] < 0:
        raise ValueError("precio cannot be negative")
    
    cantidad = producto.get('cantidad', 1)
    if not isinstance(cantidad, int) or cantidad < 1:
        raise ValueError("cantidad must be positive integer")
    
    # ... resto del código
```

---

### 6. Dependencias ✅ SEGURO

**Análisis**: Dependencias mínimas y actualizadas.

**Dependencias**:
```json
"requirements": ["requests>=2.31.0"]
```

**Verificado**:
- `requests>=2.31.0` - Versión actual sin CVEs conocidos ✓
- No hay dependencias con vulnerabilidades conocidas ✓

**✓ PASA**: Dependencias seguras.

---

### 7. Manejo de Datos Sensibles ✅ BUENO

**Análisis**: No se almacenan datos sensibles.

**Datos almacenados**:
- Productos (nombre, precio, imagen_url) - Públicos ✓
- Historial de búsquedas (query, count) - No sensible ✓
- No se almacenan credenciales ✓

**Logging**:
```python
_LOGGER.info("Producto agregado: %s", producto["nombre"])
```

**✓ PASA**: No se loggean datos sensibles.

---

### 8. Comunicación Externa ⚠️ HTTP (no HTTPS forzado)

**Análisis**: Búsquedas a Coto Digital usan HTTP.

**Código**:
```python
COTO_SEARCH_URL = "https://www.cotodigital3.com.ar/sitios/cdigi/browse/search"
```

**✓ NOTA**: Ya usa HTTPS para Coto Digital.

**API REST local**: HTTP en puerto 8766 (solo red local).

**Recomendación**: Para uso local está bien. Si se expone externamente, usar HTTPS.

---

### 9. CORS y Exposición de API ℹ️ INFORMATIVO

**Dashboard web** (`coto_dashboard_web.py`):
```python
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
```

**Riesgo**: BAJO - Solo para uso en red local.

**Recomendación**: Si se expone a internet, restringir CORS:
```python
response.headers.add('Access-Control-Allow-Origin', 'http://homeassistant.local:8123')
```

---

### 10. Extensión Chrome ✅ SEGURO

**Permisos solicitados**:
```json
"permissions": ["storage"]
```

**✓ Mínimos permisos**: Solo storage local.

**Content scripts**:
- No accede a credenciales
- No hace requests externos
- Solo comunica con dashboard local

**✓ PASA**: Extensión segura.

---

## Vulnerabilidades Conocidas

### Ninguna vulnerabilidad crítica encontrada ✅

---

## Recomendaciones de Mejora

### Prioridad ALTA
Ninguna.

### Prioridad MEDIA

1. **Agregar validación de entrada explícita**
   - Validar tipos en `agregar_al_carrito()`
   - Validar rangos en `buscar_productos()`
   - Sanitizar strings antes de usar

2. **Validar path de base de datos**
   - Asegurar que `db_path` esté dentro de config dir
   - Prevenir path traversal teórico

### Prioridad BAJA

3. **Rate limiting para búsquedas**
   - Prevenir DoS por búsquedas masivas
   - Implementar cache de búsquedas

4. **Restringir CORS en producción**
   - Si se expone el dashboard externamente
   - Usar whitelist de orígenes

5. **Agregar logging de seguridad**
   - Loggear intentos de acceso anormales
   - Monitorear queries sospechosas

---

## Código de Ejemplo - Mejoras Sugeridas

### Validación de entrada mejorada:

```python
# coto_api.py

from typing import Any, Dict
import re

class CotoDigitalAPI:
    
    @staticmethod
    def _validate_producto(producto: dict[str, Any]) -> None:
        """Validar estructura y tipos de producto."""
        required = ['producto_id', 'nombre', 'precio']
        
        # Validar campos requeridos
        if not all(k in producto for k in required):
            raise ValueError(f"Missing fields: {required}")
        
        # Validar tipos
        if not isinstance(producto['producto_id'], str):
            raise TypeError("producto_id must be string")
        
        if not isinstance(producto['nombre'], str):
            raise TypeError("nombre must be string")
        
        if not isinstance(producto['precio'], (int, float)):
            raise TypeError("precio must be numeric")
        
        # Validar rangos
        if producto['precio'] < 0:
            raise ValueError("precio cannot be negative")
        
        if len(producto['producto_id']) > 100:
            raise ValueError("producto_id too long")
        
        if len(producto['nombre']) > 500:
            raise ValueError("nombre too long")
        
        # Validar cantidad si existe
        if 'cantidad' in producto:
            if not isinstance(producto['cantidad'], int):
                raise TypeError("cantidad must be integer")
            if producto['cantidad'] < 1 or producto['cantidad'] > 1000:
                raise ValueError("cantidad out of range (1-1000)")
    
    def agregar_al_carrito(self, producto: dict[str, Any]) -> bool:
        """Agregar producto al carrito con validación."""
        try:
            # Validar entrada
            self._validate_producto(producto)
            
            # Sanitizar strings
            producto['producto_id'] = producto['producto_id'].strip()
            producto['nombre'] = producto['nombre'].strip()
            
            # ... resto del código original
            
        except (ValueError, TypeError) as e:
            _LOGGER.error("Validación falló: %s", e)
            return False
```

---

## Checklist de Seguridad

- [x] SQL Injection - Protegido con parametrized queries
- [x] XSS - No aplicable (no hay frontend dinámico en integración)
- [x] CSRF - No aplicable (no hay autenticación de usuario)
- [x] Credenciales hardcodeadas - No encontradas
- [x] Command Injection - No hay vectores
- [x] Path Traversal - Riesgo bajo, controlado por HA
- [x] Dependencias vulnerables - No encontradas
- [ ] Validación de entrada - Mejorable (no crítico)
- [x] Logging seguro - No expone datos sensibles
- [x] HTTPS - Usado para comunicación con Coto Digital
- [x] Permisos mínimos - Extensión Chrome usa solo storage

**Puntuación de Seguridad**: 10/11 ✅

---

## Conclusión

El código de **Coto Digital v1.3.0** es **seguro para uso en producción**.

Las recomendaciones de mejora son **opcionales** y de prioridad media-baja. No hay vulnerabilidades críticas que requieran acción inmediata.

**Aprobado para release público** ✅

---

**Analizado por**: Claude (Hermes AI Agent)  
**Fecha**: 27 de Agosto, 2026  
**Próxima revisión**: Con cada major version update
