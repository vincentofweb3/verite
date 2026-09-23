from pathlib import Path


def test_firestore_project_rules_distinguish_create_from_existing_resource():
    rules = Path("infra/firestore.rules").read_text(encoding="utf-8")
    assert "allow create: if" in rules
    assert "request.resource.data.owner_id" in rules
    assert "allow read, delete: if" in rules
    assert "allow update: if" in rules
    assert "request.resource.data.owner_id == resource.data.owner_id" in rules
