#!/usr/bin/env python3
"""
Script para crear manualmente el dashboard de Coto Digital en Home Assistant.
Ejecutar cuando la creación automática falla.

Uso:
    python3 create_dashboard_manual.py
"""
import json
import sys
from pathlib import Path
from datetime import datetime


def find_config_dir():
    """Encontrar el directorio de configuración de HA."""
    possible_dirs = [
        Path("/config"),
        Path.home() / ".homeassistant",
        Path("/usr/share/hassio/homeassistant"),
    ]
    
    for config_dir in possible_dirs:
        if config_dir.exists():
            return config_dir
    
    return None


def create_dashboard_file(config_dir: Path):
    """Crear el archivo de dashboard en .storage."""
    
    dashboard_data = {
        "version": 1,
        "minor_version": 1,
        "key": "lovelace.coto-digital",
        "data": {
            "config": {
                "views": [
                    {
                        "title": "Coto Digital",
                        "path": "coto-digital",
                        "icon": "mdi:cart",
                        "badges": [],
                        "cards": [
                            # Header con estadísticas
                            {
                                "type": "vertical-stack",
                                "cards": [
                                    {
                                        "type": "markdown",
                                        "content": "# 🛒 Coto Digital\n## Tu carrito de compras"
                                    },
                                    {
                                        "type": "horizontal-stack",
                                        "cards": [
                                            {
                                                "type": "entity",
                                                "entity": "sensor.coto_digital_productos",
                                                "name": "Productos",
                                                "icon": "mdi:cart-variant"
                                            },
                                            {
                                                "type": "entity",
                                                "entity": "sensor.coto_digital_unidades",
                                                "name": "Unidades",
                                                "icon": "mdi:package-variant"
                                            },
                                            {
                                                "type": "entity",
                                                "entity": "sensor.coto_digital_total",
                                                "name": "Total",
                                                "icon": "mdi:currency-usd"
                                            }
                                        ]
                                    }
                                ]
                            },
                            # Botones de acción
                            {
                                "type": "entities",
                                "title": "Acciones",
                                "entities": [
                                    {
                                        "entity": "button.sincronizar_coto_digital",
                                        "name": "Sincronizar con Coto Digital",
                                        "icon": "mdi:sync"
                                    },
                                    {
                                        "entity": "button.vaciar_carrito_coto_digital",
                                        "name": "Vaciar Carrito",
                                        "icon": "mdi:delete-empty"
                                    }
                                ]
                            },
                            # Gráfico histórico
                            {
                                "type": "history-graph",
                                "title": "Historial de Total",
                                "entities": [
                                    {"entity": "sensor.coto_digital_total"}
                                ],
                                "hours_to_show": 168
                            },
                            # Gauge
                            {
                                "type": "gauge",
                                "entity": "sensor.coto_digital_total",
                                "name": "Total del Carrito",
                                "min": 0,
                                "max": 100000,
                                "needle": True,
                                "severity": {
                                    "green": 0,
                                    "yellow": 30000,
                                    "red": 70000
                                }
                            },
                            # Documentación
                            {
                                "type": "markdown",
                                "content": """
## Servicios Disponibles

### Buscar Producto
```yaml
service: coto_digital.buscar_producto
data:
  query: "leche"
```

### Agregar al Carrito
```yaml
service: coto_digital.agregar_al_carrito
data:
  producto_id: "prod_123"
  nombre: "Leche 1L"
  precio: 450.50
  cantidad: 2
```
                                """
                            }
                        ]
                    }
                ]
            }
        }
    }
    
    # Crear archivo en .storage
    storage_dir = config_dir / ".storage"
    storage_dir.mkdir(exist_ok=True)
    
    dashboard_file = storage_dir / "lovelace.coto-digital"
    
    with open(dashboard_file, 'w') as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"✓ Dashboard creado: {dashboard_file}")
    
    return dashboard_file


def register_dashboard(config_dir: Path):
    """Registrar el dashboard en lovelace_dashboards."""
    
    dashboards_file = config_dir / ".storage" / "lovelace_dashboards"
    
    # Si no existe, crear estructura base
    if not dashboards_file.exists():
        dashboards_data = {
            "version": 1,
            "minor_version": 1,
            "key": "lovelace_dashboards",
            "data": {
                "items": []
            }
        }
    else:
        with open(dashboards_file) as f:
            dashboards_data = json.load(f)
    
    # Verificar si ya existe
    items = dashboards_data.get("data", {}).get("items", [])
    
    coto_exists = any(item.get("url_path") == "coto-digital" for item in items)
    
    if not coto_exists:
        # Agregar dashboard
        new_dashboard = {
            "id": "coto_digital_" + datetime.now().strftime("%Y%m%d%H%M%S"),
            "url_path": "coto-digital",
            "require_admin": False,
            "show_in_sidebar": True,
            "icon": "mdi:cart",
            "title": "Coto Digital"
        }
        
        items.append(new_dashboard)
        dashboards_data["data"]["items"] = items
        
        with open(dashboards_file, 'w') as f:
            json.dump(dashboards_data, f, indent=2)
        
        print(f"✓ Dashboard registrado en: {dashboards_file}")
    else:
        print("  Dashboard ya registrado")


def main():
    """Crear dashboard manualmente."""
    print("=" * 60)
    print("CREACIÓN MANUAL DE DASHBOARD - COTO DIGITAL")
    print("=" * 60)
    
    # Encontrar directorio de configuración
    config_dir = find_config_dir()
    
    if not config_dir:
        print("✗ No se pudo encontrar el directorio de configuración de HA")
        print("\nDirectorios verificados:")
        print("  - /config")
        print("  - ~/.homeassistant")
        print("  - /usr/share/hassio/homeassistant")
        sys.exit(1)
    
    print(f"\n✓ Directorio de configuración: {config_dir}")
    
    # Crear archivo de dashboard
    try:
        dashboard_file = create_dashboard_file(config_dir)
    except Exception as e:
        print(f"\n✗ Error creando dashboard: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Registrar dashboard
    try:
        register_dashboard(config_dir)
    except Exception as e:
        print(f"\n⚠ Advertencia al registrar dashboard: {e}")
        print("  El dashboard existe pero puede no aparecer en la barra lateral")
    
    print("\n" + "=" * 60)
    print("✓ DASHBOARD CREADO EXITOSAMENTE")
    print("=" * 60)
    
    print("\nPasos finales:")
    print("1. Reiniciar Home Assistant")
    print("2. Ir a la barra lateral → Buscar 'Coto Digital'")
    print("3. O navegar a: http://TU_HA_IP:8123/lovelace/coto-digital")
    
    print("\nSi no aparece en la barra lateral:")
    print("1. Ir a Configuración → Dashboards")
    print("2. Buscar 'Coto Digital'")
    print("3. Activar 'Mostrar en barra lateral'")
    
    print("\n✓ Dashboard creado en:")
    print(f"  {dashboard_file}")


if __name__ == "__main__":
    main()
