from pathlib import Path
from tempfile import TemporaryDirectory


from app.templates.repository import JsonTemplateRepository
from app.templates.schemas import TemplateCreate, TemplateUpdate
from app.templates.service import TemplateService


def test_template_crud_and_generation_from_template() -> None:
    with TemporaryDirectory() as temp_dir:
        repository = JsonTemplateRepository(storage_dir=Path(temp_dir))
        service = TemplateService(repository)

        created = service.create_template(
            TemplateCreate(
                name="Retail SQL Practice",
                description="Interview-ready SQL practice",
                industry="retail",
                scenario="none",
                customers=500,
                products=120,
                stores=8,
                orders=2500,
                export_type="zip",
                quality={"missing_values": 5.0, "duplicates": 2.0},
                difficulty="Intermediate",
            )
        )

        assert created.name == "Retail SQL Practice"
        assert service.get_template(created.id).name == "Retail SQL Practice"

        updated = service.update_template(
            created.id,
            TemplateUpdate(
                name="Retail SQL Practice Updated",
                description="Updated interview-ready SQL practice",
                difficulty="Advanced",
            ),
        )
        assert updated.name == "Retail SQL Practice Updated"
        assert updated.version == 2

        generated = service.generate_from_template(updated.id)
        assert generated.challenge_title
        assert generated.download_url.endswith(".zip")

        service.delete_template(updated.id)
        try:
            service.get_template(updated.id)
        except ValueError:
            pass
        else:
            raise AssertionError("template should be deleted")


def test_template_routes_validate_input(api_client) -> None:
    client = api_client
    response = client.post(
        "/templates",
        headers={"Authorization": "Bearer invalid"},
        json={
            "name": "Retail Beginner",
            "description": "Starter template",
            "industry": "retail",
            "scenario": "none",
            "customers": 10,
            "products": 5,
            "stores": 2,
            "orders": 20,
            "export_type": "zip",
            "quality": {"missing_values": 101},
            "difficulty": "Beginner",
        },
    )
    assert response.status_code == 401

    response = client.get("/templates")
    assert response.status_code == 401
