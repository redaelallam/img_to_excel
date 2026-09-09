from __future__ import annotations


def test_health_endpoint(client) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "Agro Juice Scanner"
    assert "version" in data
    assert isinstance(data["version"], str)


def test_templates_endpoint_returns_list(client) -> None:
    response = client.get("/api/templates")

    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert "templates" in data
    assert isinstance(data["templates"], list)
    assert len(data["templates"]) >= 1

    first_template = data["templates"][0]
    assert "id" in first_template
    assert "name" in first_template
    assert "document_type" in first_template
    assert "column_names" in first_template
    assert "notes" in first_template
    assert "created_at" in first_template