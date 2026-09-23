import subprocess
from pathlib import Path


def test_compliance_gate_rejects_disallowed_vendor_reference(tmp_path):
    shipped_source = tmp_path / "app"
    shipped_source.mkdir()
    (shipped_source / "bad_runtime.py").write_text("import openai\n", encoding="utf-8")
    result = subprocess.run(["bash", "scripts/check_compliance.sh", str(shipped_source)], capture_output=True, text=True, check=False)
    assert result.returncode == 1
    assert "Disallowed AI vendor reference" in result.stderr


def test_default_compliance_gate_scans_app_without_optional_roots(tmp_path):
    project_root = Path(__file__).resolve().parents[1]
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "check_compliance.sh").write_bytes(
        (project_root / "scripts" / "check_compliance.sh").read_bytes()
    )
    (tmp_path / "app").mkdir()
    (tmp_path / "frontend").mkdir()
    (tmp_path / "app" / "bad.py").write_text("import openai\n", encoding="utf-8")

    result = subprocess.run(
        ["bash", "scripts/check_compliance.sh"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Disallowed AI vendor reference" in result.stderr


def test_compliance_gate_fails_closed_for_missing_root(tmp_path):
    project_root = Path(__file__).resolve().parents[1]
    script = project_root / "scripts" / "check_compliance.sh"
    result = subprocess.run(
        ["bash", str(script), str(tmp_path / "missing")],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "scan root does not exist" in result.stderr
