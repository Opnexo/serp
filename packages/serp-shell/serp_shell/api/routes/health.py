"""
Health check routes
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from serp_core.plugins import (
    HealthStatus,
    ModuleHealthReport,
    get_module_registry,
)
from serp_core.resilience import get_circuit_breaker_registry

router = APIRouter()


# Response models
class HealthResponse(BaseModel):
    status: str
    version: str


class ComponentHealthResponse(BaseModel):
    name: str
    status: str
    message: Optional[str] = None
    response_time_ms: Optional[float] = None


class ModuleHealthResponse(BaseModel):
    module_id: str
    module_name: str
    status: str
    version: str
    components: List[ComponentHealthResponse] = []
    message: Optional[str] = None
    checked_at: str


class SystemHealthResponse(BaseModel):
    status: str
    version: str
    checked_at: str
    modules: Dict[str, ModuleHealthResponse]
    total_modules: int
    healthy_modules: int
    degraded_modules: int
    unhealthy_modules: int


def _report_to_response(report: ModuleHealthReport) -> ModuleHealthResponse:
    """Convert a ModuleHealthReport to a response model."""
    return ModuleHealthResponse(
        module_id=report.module_id,
        module_name=report.module_name,
        status=report.status.value,
        version=report.version,
        components=[
            ComponentHealthResponse(
                name=c.name,
                status=c.status.value,
                message=c.message,
                response_time_ms=c.response_time_ms,
            )
            for c in report.components
        ],
        message=report.message,
        checked_at=report.checked_at.isoformat(),
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.

    Returns a simple health status for load balancer checks.
    For detailed module health, use /health/modules.
    """
    return HealthResponse(status="healthy", version="1.0.0")


@router.get("/health/modules", response_model=SystemHealthResponse)
async def get_all_modules_health():
    """
    Get health status for all loaded modules.

    Returns aggregated health information including:
    - Overall system status
    - Individual module health reports
    - Component-level health details
    """
    registry = get_module_registry()
    reports = await registry.check_all_health()
    overall_status = registry.get_overall_status(reports)

    # Count modules by status
    healthy = sum(1 for r in reports.values() if r.status == HealthStatus.HEALTHY)
    degraded = sum(1 for r in reports.values() if r.status == HealthStatus.DEGRADED)
    unhealthy = sum(1 for r in reports.values() if r.status == HealthStatus.UNHEALTHY)

    return SystemHealthResponse(
        status=overall_status.value,
        version="1.0.0",
        checked_at=datetime.utcnow().isoformat(),
        modules={name: _report_to_response(report) for name, report in reports.items()},
        total_modules=len(reports),
        healthy_modules=healthy,
        degraded_modules=degraded,
        unhealthy_modules=unhealthy,
    )


@router.get("/health/modules/{module_id}", response_model=ModuleHealthResponse)
async def get_module_health(module_id: str):
    """
    Get health status for a specific module.

    Args:
        module_id: The module identifier (e.g., "serp-crm", "serp-users")

    Returns:
        Detailed health report for the specified module

    Raises:
        404: If the module is not found or has no health check
    """
    registry = get_module_registry()

    # Check if module exists
    if not registry.exists(module_id):
        raise HTTPException(
            status_code=404,
            detail=f"Module '{module_id}' not found"
        )

    # Check if module has a health check
    if not registry.has_health_check(module_id):
        raise HTTPException(
            status_code=404,
            detail=f"Module '{module_id}' does not have a health check registered"
        )

    report = await registry.check_module_health(module_id)
    if report is None:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get health report for module '{module_id}'"
        )

    return _report_to_response(report)


@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SimpleERP API", "docs": "/docs"}


# Circuit Breaker endpoints
class CircuitBreakerStatsResponse(BaseModel):
    total_calls: int
    successful_calls: int
    failed_calls: int
    rejected_calls: int
    success_rate: float
    last_failure_time: Optional[str] = None
    last_success_time: Optional[str] = None


class CircuitBreakerResponse(BaseModel):
    name: str
    state: str
    failure_threshold: int
    success_threshold: int
    recovery_timeout: float
    recent_failures: int
    consecutive_successes: int
    remaining_recovery_time: Optional[float] = None
    stats: CircuitBreakerStatsResponse


class AllCircuitBreakersResponse(BaseModel):
    total: int
    open_count: int
    half_open_count: int
    closed_count: int
    circuits: Dict[str, CircuitBreakerResponse]


@router.get("/health/circuits", response_model=AllCircuitBreakersResponse)
async def get_all_circuit_breakers():
    """
    Get status of all circuit breakers.

    Returns status information for all registered circuit breakers,
    useful for monitoring cross-module communication health.
    """
    registry = get_circuit_breaker_registry()
    statuses = registry.get_all_statuses()

    # Count by state
    open_count = sum(1 for s in statuses.values() if s["state"] == "open")
    half_open_count = sum(1 for s in statuses.values() if s["state"] == "half_open")
    closed_count = sum(1 for s in statuses.values() if s["state"] == "closed")

    circuits = {}
    for name, status in statuses.items():
        circuits[name] = CircuitBreakerResponse(
            name=status["name"],
            state=status["state"],
            failure_threshold=status["failure_threshold"],
            success_threshold=status["success_threshold"],
            recovery_timeout=status["recovery_timeout"],
            recent_failures=status["recent_failures"],
            consecutive_successes=status["consecutive_successes"],
            remaining_recovery_time=status["remaining_recovery_time"],
            stats=CircuitBreakerStatsResponse(**status["stats"]),
        )

    return AllCircuitBreakersResponse(
        total=len(statuses),
        open_count=open_count,
        half_open_count=half_open_count,
        closed_count=closed_count,
        circuits=circuits,
    )


@router.get("/health/circuits/{circuit_name}", response_model=CircuitBreakerResponse)
async def get_circuit_breaker(circuit_name: str):
    """
    Get status of a specific circuit breaker.

    Args:
        circuit_name: The circuit breaker name (e.g., "crm-api")

    Returns:
        Detailed status for the specified circuit breaker

    Raises:
        404: If the circuit breaker is not found
    """
    registry = get_circuit_breaker_registry()
    breaker = registry.get(circuit_name)

    if breaker is None:
        raise HTTPException(
            status_code=404,
            detail=f"Circuit breaker '{circuit_name}' not found"
        )

    status = breaker.get_status()
    return CircuitBreakerResponse(
        name=status["name"],
        state=status["state"],
        failure_threshold=status["failure_threshold"],
        success_threshold=status["success_threshold"],
        recovery_timeout=status["recovery_timeout"],
        recent_failures=status["recent_failures"],
        consecutive_successes=status["consecutive_successes"],
        remaining_recovery_time=status["remaining_recovery_time"],
        stats=CircuitBreakerStatsResponse(**status["stats"]),
    )


@router.post("/health/circuits/{circuit_name}/reset")
async def reset_circuit_breaker(circuit_name: str):
    """
    Manually reset a circuit breaker to closed state.

    This is useful for recovering from false positives or after
    a dependent service has been fixed.

    Args:
        circuit_name: The circuit breaker name to reset

    Returns:
        Success message

    Raises:
        404: If the circuit breaker is not found
    """
    registry = get_circuit_breaker_registry()
    breaker = registry.get(circuit_name)

    if breaker is None:
        raise HTTPException(
            status_code=404,
            detail=f"Circuit breaker '{circuit_name}' not found"
        )

    breaker.reset()
    return {"message": f"Circuit breaker '{circuit_name}' has been reset to closed state"}
