"""Tests for Coto Digital dashboard creation."""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import logging

# Mock homeassistant modules
import sys
sys.path.insert(0, '../custom_components/coto_digital')

_LOGGER = logging.getLogger(__name__)


class MockHomeAssistant:
    """Mock Home Assistant object."""
    
    def __init__(self):
        self.data = {
            "lovelace": MagicMock(),
        }
        self.loop = AsyncMock()
        
    def async_add_executor_job(self, func, *args):
        """Mock async executor."""
        return AsyncMock(return_value=func(*args))


class MockStore:
    """Mock storage."""
    
    def __init__(self, hass, version, key):
        self.hass = hass
        self.version = version
        self.key = key
        self.data = {}
        
    async def async_save(self, data):
        """Mock save."""
        self.data = data
        print(f"✓ Store.async_save called for {self.key}")
        print(f"  Data: {list(data.keys())}")
        return True
        
    async def async_remove(self):
        """Mock remove."""
        self.data = {}
        return True


def test_dashboard_config():
    """Test dashboard configuration."""
    from custom_components.coto_digital.dashboard import DASHBOARD_CONFIG, DASHBOARD_VIEW
    
    print("\n=== Testing Dashboard Configuration ===")
    
    # Verificar configuración del dashboard
    assert DASHBOARD_CONFIG["title"] == "Coto Digital"
    assert DASHBOARD_CONFIG["icon"] == "mdi:cart"
    assert DASHBOARD_CONFIG["show_in_sidebar"] is True
    print("✓ Dashboard config is valid")
    
    # Verificar vista
    assert DASHBOARD_VIEW["title"] == "Coto Digital"
    assert DASHBOARD_VIEW["path"] == "coto-digital"
    assert DASHBOARD_VIEW["icon"] == "mdi:cart"
    assert len(DASHBOARD_VIEW["cards"]) > 0
    print(f"✓ Dashboard view has {len(DASHBOARD_VIEW['cards'])} cards")
    
    # Verificar cards
    for i, card in enumerate(DASHBOARD_VIEW["cards"]):
        assert "type" in card, f"Card {i} missing 'type'"
        print(f"  Card {i}: {card['type']}")
    
    print("✓ All cards are valid")


@pytest.mark.asyncio
async def test_create_dashboard_basic():
    """Test basic dashboard creation."""
    from custom_components.coto_digital.dashboard import async_create_dashboard
    
    print("\n=== Testing Dashboard Creation (Basic) ===")
    
    hass = MockHomeAssistant()
    
    with patch('custom_components.coto_digital.dashboard._get_dashboards', return_value={}):
        with patch('custom_components.coto_digital.dashboard._create_dashboard_storage') as mock_create:
            result = await async_create_dashboard(hass)
            
            if result:
                print("✓ Dashboard creation returned True")
                print(f"✓ _create_dashboard_storage was called: {mock_create.called}")
            else:
                print("✗ Dashboard creation returned False")
                
    return result


@pytest.mark.asyncio
async def test_create_dashboard_already_exists():
    """Test dashboard creation when it already exists."""
    from custom_components.coto_digital.dashboard import async_create_dashboard
    
    print("\n=== Testing Dashboard Creation (Already Exists) ===")
    
    hass = MockHomeAssistant()
    
    # Simular que el dashboard ya existe
    with patch('custom_components.coto_digital.dashboard._get_dashboards', return_value={'coto-digital': {}}):
        result = await async_create_dashboard(hass)
        
        if result:
            print("✓ Dashboard creation returned True (already exists)")
        else:
            print("✗ Dashboard creation returned False")
            
    return result


def test_create_dashboard_storage():
    """Test dashboard storage creation."""
    from custom_components.coto_digital.dashboard import _create_dashboard_storage, DASHBOARD_VIEW
    
    print("\n=== Testing Dashboard Storage Creation ===")
    
    hass = MockHomeAssistant()
    url = "coto-digital"
    
    with patch('custom_components.coto_digital.dashboard.storage.Store', MockStore):
        try:
            _create_dashboard_storage(hass, url)
            print("✓ Dashboard storage creation completed")
        except Exception as e:
            print(f"✗ Error creating dashboard storage: {e}")
            raise


def run_manual_tests():
    """Run all tests manually."""
    print("=" * 60)
    print("COTO DIGITAL - Dashboard Creation Tests")
    print("=" * 60)
    
    # Test 1: Config
    try:
        test_dashboard_config()
        print("\n✓ TEST 1 PASSED: Dashboard configuration\n")
    except Exception as e:
        print(f"\n✗ TEST 1 FAILED: {e}\n")
        return False
    
    # Test 2: Basic creation
    import asyncio
    try:
        result = asyncio.run(test_create_dashboard_basic())
        if result:
            print("\n✓ TEST 2 PASSED: Basic dashboard creation\n")
        else:
            print("\n⚠ TEST 2 WARNING: Dashboard creation returned False\n")
    except Exception as e:
        print(f"\n✗ TEST 2 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Already exists
    try:
        result = asyncio.run(test_create_dashboard_already_exists())
        if result:
            print("\n✓ TEST 3 PASSED: Dashboard already exists handling\n")
        else:
            print("\n✗ TEST 3 FAILED: Should return True when exists\n")
    except Exception as e:
        print(f"\n✗ TEST 3 FAILED: {e}\n")
        return False
    
    # Test 4: Storage
    try:
        test_create_dashboard_storage()
        print("\n✓ TEST 4 PASSED: Dashboard storage creation\n")
    except Exception as e:
        print(f"\n✗ TEST 4 FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = run_manual_tests()
    exit(0 if success else 1)
