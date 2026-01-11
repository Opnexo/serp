"""Tests for the health check system."""

import pytest

from serp_core.plugins import (
    ComponentHealth,
    HealthCheckBuilder,
    HealthStatus,
    ModuleHealthReport,
    ModuleRegistry,
    create_simple_health_check,
)


class TestHealthStatus:
    """Test HealthStatus enum."""

    def test_health_status_values(self):
        """Verify HealthStatus enum values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.DEGRADED.value == "degraded"
        assert HealthStatus.UNHEALTHY.value == "unhealthy"


class TestComponentHealth:
    """Test ComponentHealth dataclass."""

    def test_component_health_creation(self):
        """Test creating a ComponentHealth instance."""
        component = ComponentHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Connected",
            response_time_ms=5.2,
        )
        assert component.name == "database"
        assert component.status == HealthStatus.HEALTHY
        assert component.message == "Connected"
        assert component.response_time_ms == 5.2

    def test_component_health_optional_fields(self):
        """Test ComponentHealth with only required fields."""
        component = ComponentHealth(
            name="cache",
            status=HealthStatus.DEGRADED,
        )
        assert component.name == "cache"
        assert component.status == HealthStatus.DEGRADED
        assert component.message is None
        assert component.response_time_ms is None


class TestModuleHealthReport:
    """Test ModuleHealthReport dataclass."""

    def test_module_health_report_creation(self):
        """Test creating a ModuleHealthReport instance."""
        report = ModuleHealthReport(
            module_id="test-module",
            module_name="Test Module",
            status=HealthStatus.HEALTHY,
            version="1.0.0",
        )
        assert report.module_id == "test-module"
        assert report.module_name == "Test Module"
        assert report.status == HealthStatus.HEALTHY
        assert report.version == "1.0.0"
        assert report.components == []

    def test_module_health_report_with_components(self):
        """Test ModuleHealthReport with components."""
        components = [
            ComponentHealth(name="db", status=HealthStatus.HEALTHY),
            ComponentHealth(name="cache", status=HealthStatus.DEGRADED),
        ]
        report = ModuleHealthReport(
            module_id="test-module",
            module_name="Test Module",
            status=HealthStatus.DEGRADED,
            components=components,
        )
        assert len(report.components) == 2

    def test_module_health_report_to_dict(self):
        """Test converting ModuleHealthReport to dictionary."""
        report = ModuleHealthReport(
            module_id="test-module",
            module_name="Test Module",
            status=HealthStatus.HEALTHY,
            version="1.0.0",
            components=[
                ComponentHealth(
                    name="database",
                    status=HealthStatus.HEALTHY,
                    response_time_ms=10.5,
                )
            ],
        )
        result = report.to_dict()

        assert result["module_id"] == "test-module"
        assert result["module_name"] == "Test Module"
        assert result["status"] == "healthy"
        assert result["version"] == "1.0.0"
        assert len(result["components"]) == 1
        assert result["components"][0]["name"] == "database"
        assert result["components"][0]["status"] == "healthy"


class TestHealthCheckBuilder:
    """Test HealthCheckBuilder class."""

    def test_builder_basic(self):
        """Test basic builder usage."""
        builder = HealthCheckBuilder("mod-1", "Module One", "1.0.0")
        report = builder.build()

        assert report.module_id == "mod-1"
        assert report.module_name == "Module One"
        assert report.version == "1.0.0"
        assert report.status == HealthStatus.HEALTHY
        assert report.components == []

    def test_builder_add_component(self):
        """Test adding a component to the builder."""
        builder = HealthCheckBuilder("mod-1", "Module One", "1.0.0")
        component = ComponentHealth(name="db", status=HealthStatus.HEALTHY)
        builder.add_component(component)
        report = builder.build()

        assert len(report.components) == 1
        assert report.components[0].name == "db"
        assert report.status == HealthStatus.HEALTHY

    def test_builder_degraded_component(self):
        """Test that degraded component sets overall status to degraded."""
        builder = HealthCheckBuilder("mod-1", "Module One", "1.0.0")
        builder.add_component(
            ComponentHealth(name="db", status=HealthStatus.HEALTHY)
        )
        builder.add_component(
            ComponentHealth(name="cache", status=HealthStatus.DEGRADED)
        )
        report = builder.build()

        assert report.status == HealthStatus.DEGRADED

    def test_builder_unhealthy_component(self):
        """Test that unhealthy component sets overall status to unhealthy."""
        builder = HealthCheckBuilder("mod-1", "Module One", "1.0.0")
        builder.add_component(
            ComponentHealth(name="db", status=HealthStatus.UNHEALTHY)
        )
        builder.add_component(
            ComponentHealth(name="cache", status=HealthStatus.HEALTHY)
        )
        report = builder.build()

        assert report.status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_builder_add_async_check_success(self):
        """Test adding an async health check that succeeds."""

        async def check_db() -> bool:
            return True

        builder = HealthCheckBuilder("mod-1", "Module One", "1.0.0")
        await builder.add_async_check("database", check_db)
        report = builder.build()

        assert len(report.components) == 1
        assert report.components[0].name == "database"
        assert report.components[0].status == HealthStatus.HEALTHY
        assert report.components[0].response_time_ms is not None

    @pytest.mark.asyncio
    async def test_builder_add_async_check_failure(self):
        """Test adding an async health check that fails."""

        async def check_db() -> bool:
            return False

        builder = HealthCheckBuilder("mod-1", "Module One", "1.0.0")
        await builder.add_async_check("database", check_db, critical=True)
        report = builder.build()

        assert report.components[0].status == HealthStatus.UNHEALTHY
        assert report.status == HealthStatus.UNHEALTHY

    @pytest.mark.asyncio
    async def test_builder_add_async_check_exception(self):
        """Test adding an async health check that raises an exception."""

        async def check_db() -> bool:
            raise ConnectionError("Connection refused")

        builder = HealthCheckBuilder("mod-1", "Module One", "1.0.0")
        await builder.add_async_check("database", check_db, critical=True)
        report = builder.build()

        assert report.components[0].status == HealthStatus.UNHEALTHY
        assert "Connection refused" in (report.components[0].message or "")

    @pytest.mark.asyncio
    async def test_builder_non_critical_failure(self):
        """Test that non-critical failure sets status to degraded."""

        async def check_cache() -> bool:
            return False

        builder = HealthCheckBuilder("mod-1", "Module One", "1.0.0")
        await builder.add_async_check("cache", check_cache, critical=False)
        report = builder.build()

        assert report.components[0].status == HealthStatus.DEGRADED
        assert report.status == HealthStatus.DEGRADED

    def test_builder_sync_check_success(self):
        """Test adding a sync health check that succeeds."""

        def check_config() -> bool:
            return True

        builder = HealthCheckBuilder("mod-1", "Module One", "1.0.0")
        builder.add_sync_check("config", check_config)
        report = builder.build()

        assert report.components[0].status == HealthStatus.HEALTHY


class TestCreateSimpleHealthCheck:
    """Test create_simple_health_check function."""

    @pytest.mark.asyncio
    async def test_simple_health_check(self):
        """Test that simple health check returns healthy status."""
        health_check = create_simple_health_check(
            module_id="simple-mod",
            module_name="Simple Module",
            version="2.0.0",
        )

        report = await health_check()

        assert report.module_id == "simple-mod"
        assert report.module_name == "Simple Module"
        assert report.version == "2.0.0"
        assert report.status == HealthStatus.HEALTHY
        assert len(report.components) == 1


class TestModuleRegistryHealth:
    """Test health check functionality in ModuleRegistry."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test."""
        return ModuleRegistry()

    @pytest.mark.asyncio
    async def test_register_health_check(self, registry):
        """Test registering a health check."""
        from serp_core.plugins import ModuleInfo

        module_info = ModuleInfo(
            name="test-mod",
            version="1.0.0",
            display_name="Test Module",
        )
        registry.register(module_info)
        registry.mark_loaded("test-mod")

        health_check = create_simple_health_check(
            "test-mod", "Test Module", "1.0.0"
        )
        registry.register_health_check("test-mod", health_check)

        assert registry.has_health_check("test-mod")

    @pytest.mark.asyncio
    async def test_check_module_health(self, registry):
        """Test checking health for a specific module."""
        from serp_core.plugins import ModuleInfo

        module_info = ModuleInfo(
            name="test-mod",
            version="1.0.0",
            display_name="Test Module",
        )
        registry.register(module_info)
        registry.mark_loaded("test-mod")

        health_check = create_simple_health_check(
            "test-mod", "Test Module", "1.0.0"
        )
        registry.register_health_check("test-mod", health_check)

        report = await registry.check_module_health("test-mod")

        assert report is not None
        assert report.module_id == "test-mod"
        assert report.status == HealthStatus.HEALTHY

    @pytest.mark.asyncio
    async def test_check_all_health(self, registry):
        """Test checking health for all modules."""
        from serp_core.plugins import ModuleInfo

        # Register two modules
        for name in ["mod-a", "mod-b"]:
            module_info = ModuleInfo(
                name=name,
                version="1.0.0",
                display_name=f"Module {name}",
            )
            registry.register(module_info)
            registry.mark_loaded(name)

            health_check = create_simple_health_check(
                name, f"Module {name}", "1.0.0"
            )
            registry.register_health_check(name, health_check)

        reports = await registry.check_all_health()

        assert len(reports) == 2
        assert "mod-a" in reports
        assert "mod-b" in reports
        assert all(r.status == HealthStatus.HEALTHY for r in reports.values())

    def test_get_overall_status_healthy(self, registry):
        """Test overall status when all modules are healthy."""
        reports = {
            "mod-a": ModuleHealthReport(
                module_id="mod-a",
                module_name="Module A",
                status=HealthStatus.HEALTHY,
            ),
            "mod-b": ModuleHealthReport(
                module_id="mod-b",
                module_name="Module B",
                status=HealthStatus.HEALTHY,
            ),
        }

        status = registry.get_overall_status(reports)
        assert status == HealthStatus.HEALTHY

    def test_get_overall_status_degraded(self, registry):
        """Test overall status when one module is degraded."""
        reports = {
            "mod-a": ModuleHealthReport(
                module_id="mod-a",
                module_name="Module A",
                status=HealthStatus.HEALTHY,
            ),
            "mod-b": ModuleHealthReport(
                module_id="mod-b",
                module_name="Module B",
                status=HealthStatus.DEGRADED,
            ),
        }

        status = registry.get_overall_status(reports)
        assert status == HealthStatus.DEGRADED

    def test_get_overall_status_unhealthy(self, registry):
        """Test overall status when one module is unhealthy."""
        reports = {
            "mod-a": ModuleHealthReport(
                module_id="mod-a",
                module_name="Module A",
                status=HealthStatus.UNHEALTHY,
            ),
            "mod-b": ModuleHealthReport(
                module_id="mod-b",
                module_name="Module B",
                status=HealthStatus.HEALTHY,
            ),
        }

        status = registry.get_overall_status(reports)
        assert status == HealthStatus.UNHEALTHY

    def test_get_overall_status_empty(self, registry):
        """Test overall status with no modules."""
        status = registry.get_overall_status({})
        assert status == HealthStatus.HEALTHY
