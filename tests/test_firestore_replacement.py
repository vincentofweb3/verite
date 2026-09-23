from pathlib import Path

from app.models import Project, ProjectDetail, Scene, ScriptSummary, utc_now
from app.storage import Repository


class FakeDocument:
    def __init__(self, collection, document_id):
        self.parent_collection = collection
        self.id = document_id

    def to_dict(self):
        return self.parent_collection.documents[self.id]

    @property
    def reference(self):
        return self

    def set(self, payload):
        self.parent_collection.documents[self.id] = payload

    def collection(self, name):
        return FakeCollection(self.parent_collection.firestore, f"{self.parent_collection.path}/{self.id}/{name}")


class FakeCollection:
    def __init__(self, firestore, path):
        self.firestore = firestore
        self.path = path
        self.documents = firestore.collections.setdefault(path, {})

    def document(self, document_id):
        return FakeDocument(self, document_id)

    def stream(self):
        return [FakeDocument(self, document_id) for document_id in list(self.documents)]


class FakeFirestore:
    def __init__(self):
        self.collections = {}

    def collection(self, name):
        return FakeCollection(self, name)

    def batch(self):
        return FakeBatch()


class FakeBatch:
    def __init__(self):
        self.operations = []

    def delete(self, reference):
        self.operations.append(("delete", reference, None))

    def set(self, reference, payload):
        self.operations.append(("set", reference, payload))

    def commit(self):
        for operation, reference, payload in self.operations:
            if operation == "delete":
                reference.parent_collection.documents.pop(reference.id, None)
            else:
                reference.parent_collection.documents[reference.id] = payload


def test_firestore_latest_scenes_delete_stale_documents(tmp_path):
    repository = Repository.__new__(Repository)
    repository.data_dir = Path(tmp_path)
    repository._lock = __import__("threading").RLock()
    repository._firestore = FakeFirestore()
    scenes_collection = repository._firestore.collections.setdefault("projects/p/scripts/latest/scenes", {})
    scenes_collection.update({
        "scene-001": {"scene_number": 1},
        "scene-002": {"scene_number": 2},
        "scene-003": {"scene_number": 3},
    })
    project = Project(id="p", title="Replacement", owner_id="local-demo", status="ready", created_at=utc_now(), updated_at=utc_now(), script=ScriptSummary(id="s", filename="b.fountain", content_type="text/plain", size_bytes=1, status="ready", uploaded_at=utc_now(), scenes_count=2))
    detail = ProjectDetail(**project.model_dump(), scenes=[], processing_log=[])
    replacement = [
        Scene(id="scene-001", scene_number=1, slugline="INT. ONE - DAY", synopsis="One."),
        Scene(id="scene-002", scene_number=2, slugline="INT. TWO - DAY", synopsis="Two."),
    ]
    repository._write_project(detail, replacement)
    assert set(scenes_collection) == {"scene-001", "scene-002"}
