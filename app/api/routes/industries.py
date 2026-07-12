"""Industry plugin metadata endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.plugins.registry import create_default_plugin_registry


router = APIRouter(tags=["industries"])


@router.get("/industries")
async def list_industries() -> list[dict[str, object]]:
    """Return frontend contracts for available and upcoming industries."""
    registry = create_default_plugin_registry()
    payload = registry.list_frontend_metadata()
    payload.extend(
        [
            _healthcare_metadata(),
        ]
    )
    return payload


@router.get("/industries/{industry}")
async def get_industry(industry: str) -> dict[str, object]:
    """Return the UI contract for one industry plugin."""
    if industry == "healthcare":
        return _healthcare_metadata()
    try:
        return create_default_plugin_registry().frontend_metadata(industry)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from error


def _healthcare_metadata() -> dict[str, object]:
    fields = [
        _number_field("patients", "Patients", 10_000),
        _number_field("doctors", "Doctors", 500),
        _number_field("appointments", "Appointments", 50_000),
        _number_field("hospitals", "Hospitals", 25),
        _number_field("medical_claims", "Medical Claims", 30_000),
    ]
    return {
        "id": "healthcare",
        "name": "Healthcare",
        "description": "Patient, clinical operations, and claims analytics.",
        "version": "planned",
        "status": "coming_soon",
        "icon": "heart-pulse",
        "color": "#be123c",
        "configuration_fields": fields,
        "supported_scenarios": ["none", "seasonal_surge", "staff_shortage"],
        "supported_templates": [
            "Clinical Operations",
            "Patient Access",
            "Claims Analysis",
        ],
        "kpis": ["Wait Time", "Readmission Rate", "Claim Cost", "Appointment Volume"],
        "dashboard_suggestions": [
            "Patient access",
            "Hospital capacity",
            "Claims cost monitoring",
        ],
        "challenge_types": ["Care Delivery Review", "Claims Operations Investigation"],
        "field_layout": [
            {
                "title": "Dataset Size",
                "fields": [field["key"] for field in fields],
                "columns": 2,
            }
        ],
        "generation_available": False,
    }


def _number_field(key: str, label: str, default: int) -> dict[str, object]:
    return {
        "key": key,
        "label": label,
        "type": "number",
        "default": default,
        "minimum": 1,
        "maximum": 1_000_000,
    }
