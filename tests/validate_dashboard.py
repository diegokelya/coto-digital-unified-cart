#!/usr/bin/env python3
"""
Script de validación para la creación del dashboard de Coto Digital.
Ejecutar en el servidor de Home Assistant para verificar la creación del dashboard.
"""
import sys
import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
_LOGGER = logging.getLogger(__name__)


def check_integration_installed():
    """Verificar que la integración esté instalada."""
    print("\n=== Verificando instalación ===")
    
    config_dir = Path("/config") if Path("/config").exists() else Path.home() / ".homeassistant"
    integration_path = config_dir / "custom_components" / "coto_digital"
    
    if not integration_path.exists():
        print(f"✗ Integración NO encontrada en: {integration_path}")
        print("\nInstrucciones:")
        print("1. Instalar vía HACS o copiar manualmente")
        print("2. Reiniciar Home Assistant")
        return False
    
    print(f"✓ Integración encontrada en: {integration_path}")
    
    # Verificar archivos clave
    files_to_check = [
        "manifest.json",
        "__init__.py",
        "dashboard.py",
        "lovelace_dashboard.yaml",
    ]
    
    for file in files_to_check:
        file_path = integration_path / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - FALTA")
            return False
    
    return True


def check_lovelace_config():
    """Verificar configuración de Lovelace."""
    print("\n=== Verificando Lovelace ===")
    
    config_dir = Path("/config") if Path("/config").exists() else Path.home() / ".homeassistant"
    
    # Verificar dashboard en storage
    lovelace_dir = config_dir / ".storage"
    
    if not lovelace_dir.exists():
        print(f"✗ Directorio .storage no encontrado: {lovelace_dir}")
        return False
    
    print(f"✓ Directorio .storage: {lovelace_dir}")
    
    # Buscar archivo de dashboard
    dashboard_file = lovelace_dir / "lovelace.coto-digital"
    
    if dashboard_file.exists():
        print(f"✓ Dashboard encontrado: {dashboard_file}")
        
        # Leer contenido
        try:
            import json
            with open(dashboard_file) as f:
                data = json.load(f)
            
            if "views" in data:
                print(f"  ✓ Vistas: {len(data['views'])}")
                for i, view in enumerate(data['views']):
                    print(f"    Vista {i}: {view.get('title', 'Sin título')}")
                    print(f"      Cards: {len(view.get('cards', []))}")
            else:
                print("  ✗ No se encontraron vistas")
                return False
                
        except Exception as e:
            print(f"  ✗ Error leyendo dashboard: {e}")
            return False
    else:
        print(f"✗ Dashboard NO encontrado: {dashboard_file}")
        print("\nEl dashboard debería crearse automáticamente al agregar la integración.")
        print("Verifica que la integración esté agregada en:")
        print("  Configuración → Dispositivos y servicios → Integraciones")
        return False
    
    return True


def check_lovelace_dashboards():
    """Verificar dashboards registrados en lovelace_dashboards."""
    print("\n=== Verificando registro de dashboards ===")
    
    config_dir = Path("/config") if Path("/config").exists() else Path.home() / ".homeassistant"
    dashboards_file = config_dir / ".storage" / "lovelace_dashboards"
    
    if not dashboards_file.exists():
        print(f"  ℹ Archivo lovelace_dashboards no existe (normal en algunas instalaciones)")
        return None
    
    try:
        import json
        with open(dashboards_file) as f:
            data = json.load(f)
        
        dashboards = data.get("data", {}).get("items", [])
        
        print(f"  Dashboards registrados: {len(dashboards)}")
        
        coto_found = False
        for dashboard in dashboards:
            url = dashboard.get("url_path", "")
            title = dashboard.get("title", "")
            
            if "coto" in url.lower() or "coto" in title.lower():
                print(f"  ✓ Dashboard Coto encontrado:")
                print(f"    URL: {url}")
                print(f"    Título: {title}")
                print(f"    Sidebar: {dashboard.get('show_in_sidebar', False)}")
                coto_found = True
        
        if not coto_found:
            print("  ✗ Dashboard Coto Digital no encontrado en registro")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ✗ Error leyendo lovelace_dashboards: {e}")
        return False


def check_integration_loaded():
    """Verificar que la integración esté cargada en HA."""
    print("\n=== Verificando integración cargada ===")
    
    config_dir = Path("/config") if Path("/config").exists() else Path.home() / ".homeassistant"
    core_config = config_dir / ".storage" / "core.config_entries"
    
    if not core_config.exists():
        print(f"  ✗ Archivo config_entries no encontrado: {core_config}")
        return False
    
    try:
        import json
        with open(core_config) as f:
            data = json.load(f)
        
        entries = data.get("data", {}).get("entries", [])
        
        coto_entries = [e for e in entries if e.get("domain") == "coto_digital"]
        
        if coto_entries:
            print(f"  ✓ Integración cargada ({len(coto_entries)} entrada(s))")
            for entry in coto_entries:
                print(f"    Entry ID: {entry.get('entry_id')}")
                print(f"    Título: {entry.get('title')}")
                print(f"    Estado: {'Disabled' if entry.get('disabled_by') else 'Enabled'}")
        else:
            print("  ✗ Integración NO cargada")
            print("\nPara cargarla:")
            print("  1. Ir a Configuración → Dispositivos y servicios")
            print("  2. Clic en '+ Agregar integración'")
            print("  3. Buscar 'Coto Digital'")
            print("  4. Seguir el asistente")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ✗ Error leyendo config_entries: {e}")
        return False


def check_entities():
    """Verificar que las entidades estén creadas."""
    print("\n=== Verificando entidades ===")
    
    config_dir = Path("/config") if Path("/config").exists() else Path.home() / ".homeassistant"
    entity_registry = config_dir / ".storage" / "core.entity_registry"
    
    if not entity_registry.exists():
        print(f"  ⚠ Entity registry no encontrado: {entity_registry}")
        return None
    
    try:
        import json
        with open(entity_registry) as f:
            data = json.load(f)
        
        entities = data.get("data", {}).get("entities", [])
        
        coto_entities = [e for e in entities if "coto_digital" in e.get("entity_id", "")]
        
        if coto_entities:
            print(f"  ✓ Entidades encontradas: {len(coto_entities)}")
            for entity in coto_entities:
                print(f"    {entity.get('entity_id')}")
        else:
            print("  ✗ No se encontraron entidades")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ✗ Error leyendo entity_registry: {e}")
        return False


def provide_manual_steps():
    """Proveer pasos manuales para crear el dashboard."""
    print("\n" + "=" * 60)
    print("PASOS MANUALES PARA CREAR EL DASHBOARD")
    print("=" * 60)
    
    print("\nOpción 1: Esperar creación automática")
    print("1. Ir a Configuración → Dispositivos y servicios")
    print("2. Verificar que 'Coto Digital' esté en la lista")
    print("3. Si no está, clic en '+ Agregar integración' → Buscar 'Coto Digital'")
    print("4. Después de agregar, el dashboard debería aparecer en la barra lateral")
    
    print("\nOpción 2: Crear dashboard manualmente")
    print("1. Ir a Configuración → Dashboards")
    print("2. Clic en '+ Agregar dashboard'")
    print("3. Configurar:")
    print("   - Título: Coto Digital")
    print("   - Icono: mdi:cart")
    print("   - URL: coto-digital")
    print("   - Mostrar en barra lateral: ✓")
    print("4. Guardar")
    print("5. Editar dashboard → Vista YAML")
    print("6. Copiar contenido de:")
    print("   custom_components/coto_digital/lovelace_dashboard.yaml")
    print("7. Pegar y guardar")
    
    print("\nOpción 3: Forzar creación vía script")
    print("1. Desde terminal de HA:")
    print("   python3 /config/custom_components/coto_digital/create_dashboard_manual.py")


def main():
    """Ejecutar todas las verificaciones."""
    print("=" * 60)
    print("VALIDACIÓN DE DASHBOARD - COTO DIGITAL")
    print("=" * 60)
    
    checks = [
        ("Integración instalada", check_integration_installed),
        ("Integración cargada", check_integration_loaded),
        ("Entidades creadas", check_entities),
        ("Configuración Lovelace", check_lovelace_config),
        ("Registro de dashboards", check_lovelace_dashboards),
    ]
    
    results = {}
    
    for name, check_func in checks:
        try:
            result = check_func()
            results[name] = result
        except Exception as e:
            print(f"\n✗ Error en {name}: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    
    for name, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⚠ N/A"
        
        print(f"{status:10} {name}")
    
    # Determinar si el dashboard está operativo
    dashboard_ok = results.get("Configuración Lovelace") is True
    
    if dashboard_ok:
        print("\n✓ DASHBOARD CREADO Y OPERATIVO")
        print("\nAcceder en:")
        print("  http://TU_HA_IP:8123/lovelace/coto-digital")
    else:
        print("\n✗ DASHBOARD NO ENCONTRADO")
        provide_manual_steps()
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
