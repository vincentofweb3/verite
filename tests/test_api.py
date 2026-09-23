import asyncio
import sys
import threading
import types

from httpx import ASGITransport, AsyncClient

from app.main import app


async def wait_for_status(client, project_id, expected, timeout=3.0):
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        response = await client.get(f"/api/projects/{project_id}")
        body = response.json()
        if body["status"] == expected:
            return body
        await asyncio.sleep(0.01)
    raise AssertionError(f"Project did not reach {expected!r} before timeout")


def test_upload_and_parse_flow(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    import app.main as main
    from app.storage import Repository

    main.repo = Repository(str(tmp_path))
    async def exercise_flow():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            created = await client.post("/api/projects", json={"title": "Test Reel"})
            assert created.status_code == 201
            project_id = created.json()["id"]
            screenplay = b"INT. OFFICE - DAY\n\nALEX\nWe should go.\n"
            uploaded = await client.post(f"/api/projects/{project_id}/scripts", files={"file": ("test.fountain", screenplay, "text/plain")})
            assert uploaded.status_code == 201
            assert uploaded.json()["status"] in {"processing", "ready"}
            body = await wait_for_status(client, project_id, "ready")
            assert body["scenes"][0]["slugline"] == "INT. OFFICE - DAY"
            assert body["script"]["scenes_count"] == 1

    asyncio.run(exercise_flow())


def test_firebase_mode_requires_a_bearer_token(monkeypatch):
    monkeypatch.setenv("AUTH_MODE", "firebase")
    async def exercise_auth():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/projects")
            assert response.status_code == 401

    asyncio.run(exercise_auth())
    monkeypatch.setenv("AUTH_MODE", "local")


def test_firebase_mode_accepts_a_valid_token(tmp_path, monkeypatch):
    import app.main as main
    from app.storage import Repository

    fake_auth = types.SimpleNamespace(verify_id_token=lambda token: {"uid": "firebase-user", "email": "user@example.test"})
    fake_admin = types.SimpleNamespace(_apps=[object()], auth=fake_auth, initialize_app=lambda: None)
    monkeypatch.setitem(sys.modules, "firebase_admin", fake_admin)
    monkeypatch.setitem(sys.modules, "firebase_admin.auth", fake_auth)
    monkeypatch.setenv("AUTH_MODE", "firebase")
    main.repo = Repository(str(tmp_path))

    async def exercise_valid_auth():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            created = await client.post(
                "/api/projects",
                json={"title": "Authenticated"},
                headers={"Authorization": "Bearer valid-test-token"},
            )
            assert created.status_code == 201
            assert created.json()["owner_id"] == "firebase-user"

    asyncio.run(exercise_valid_auth())


def test_upload_rejects_unsupported_file(tmp_path):
    import app.main as main
    from app.storage import Repository

    main.repo = Repository(str(tmp_path))

    async def exercise_invalid_upload():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            project = await client.post("/api/projects", json={"title": "Bad format"})
            response = await client.post(
                f"/api/projects/{project.json()['id']}/scripts",
                files={"file": ("script.docx", b"not a screenplay", "application/octet-stream")},
            )
            assert response.status_code == 415

    asyncio.run(exercise_invalid_upload())


def test_processing_is_observable_before_parser_finishes(tmp_path, monkeypatch):
    import app.main as main
    from app.storage import Repository

    main.repo = Repository(str(tmp_path))
    started = threading.Event()
    release = threading.Event()
    original_parser = main.parse_screenplay

    def blocked_parser(text):
        started.set()
        assert release.wait(timeout=2)
        return original_parser(text)

    monkeypatch.setattr(main, "parse_screenplay", blocked_parser)

    async def exercise_processing():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            project = await client.post("/api/projects", json={"title": "Processing state"})
            project_id = project.json()["id"]
            uploaded = await client.post(
                f"/api/projects/{project_id}/scripts",
                files={"file": ("script.fountain", b"INT. ROOM - DAY\n\nALEX\nWait.\n", "text/plain")},
            )
            assert uploaded.json()["status"] == "processing"
            assert started.wait(timeout=2)
            processing = await client.get(f"/api/projects/{project_id}")
            assert processing.json()["status"] == "processing"
            release.set()
            ready = await wait_for_status(client, project_id, "ready")
            assert ready["script"]["scenes_count"] == 1

    asyncio.run(exercise_processing())


def test_empty_upload_is_rejected(tmp_path):
    import app.main as main
    from app.storage import Repository

    main.repo = Repository(str(tmp_path))

    async def exercise_empty_upload():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            project = await client.post("/api/projects", json={"title": "Empty"})
            response = await client.post(f"/api/projects/{project.json()['id']}/scripts", files={"file": ("empty.fountain", b"", "text/plain")})
            assert response.status_code == 400
            assert response.json()["detail"] == "The screenplay file is empty."

    asyncio.run(exercise_empty_upload())


def test_malformed_script_reaches_error_state(tmp_path):
    import app.main as main
    from app.storage import Repository

    main.repo = Repository(str(tmp_path))

    async def exercise_malformed_script():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            project = await client.post("/api/projects", json={"title": "Malformed"})
            project_id = project.json()["id"]
            uploaded = await client.post(f"/api/projects/{project_id}/scripts", files={"file": ("bad.fountain", b"not a scene", "text/plain")})
            assert uploaded.json()["status"] == "processing"
            failed = await wait_for_status(client, project_id, "error")
            assert "No screenplay scenes found" in failed["script"]["error"]
            assert any("ERROR" in line for line in failed["processing_log"])

    asyncio.run(exercise_malformed_script())


def test_upload_size_limit(tmp_path, monkeypatch):
    import app.main as main
    from app.storage import Repository

    monkeypatch.setenv("MAX_UPLOAD_BYTES", "10")
    main.repo = Repository(str(tmp_path))

    async def exercise_size_limit():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            project = await client.post("/api/projects", json={"title": "Size limit"})
            response = await client.post(f"/api/projects/{project.json()['id']}/scripts", files={"file": ("big.fountain", b"12345678901", "text/plain")})
            assert response.status_code == 413
            assert "upload limit" in response.json()["detail"]

    asyncio.run(exercise_size_limit())


def test_reupload_replaces_shorter_result(tmp_path):
    import app.main as main
    from app.storage import Repository

    main.repo = Repository(str(tmp_path))

    async def exercise_reupload():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            project = await client.post("/api/projects", json={"title": "Re-upload"})
            project_id = project.json()["id"]
            script_a = b"INT. ONE - DAY\n\nALEX\nOne.\n\nINT. TWO - DAY\n\nALEX\nTwo.\n\nINT. THREE - DAY\n\nALEX\nThree.\n"
            await client.post(f"/api/projects/{project_id}/scripts", files={"file": ("a.fountain", script_a, "text/plain")})
            first = await wait_for_status(client, project_id, "ready")
            assert len(first["scenes"]) == 3
            script_b = b"INT. ONE - DAY\n\nALEX\nOne revised.\n\nINT. TWO - DAY\n\nALEX\nTwo revised.\n"
            await client.post(f"/api/projects/{project_id}/scripts", files={"file": ("b.fountain", script_b, "text/plain")})
            second = await wait_for_status(client, project_id, "ready")
            assert [scene["slugline"] for scene in second["scenes"]] == ["INT. ONE - DAY", "INT. TWO - DAY"]
            assert second["script"]["scenes_count"] == 2

    asyncio.run(exercise_reupload())
