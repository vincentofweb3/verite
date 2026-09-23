from app.models import ProjectCreate
from app.parser import extract_text, parse_screenplay
from app.storage import Repository


def test_pdf_extraction_reaches_parser():
    content = b"BT /F1 12 Tf 72 720 Td (INT. PDF ROOM - DAY) Tj 0 -18 Td (ALEX) Tj 0 -18 Td (The PDF made it.) Tj ET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    text = extract_text("script.pdf", "application/pdf", bytes(pdf))
    scenes = parse_screenplay(text)
    assert scenes[0].slugline == "INT. PDF ROOM - DAY"
    assert scenes[0].dialogue[0]["text"] == "The PDF made it."


def test_save_and_retrieve_parsed_project(tmp_path):
    repository = Repository(str(tmp_path))
    project = repository.create_project(ProjectCreate(title="Persisted"), "local-demo")
    repository.save_upload(project.id, "persisted.fountain", "text/plain", b"INT. ROOM - DAY\n", "local-demo")
    scenes = parse_screenplay("INT. ROOM - DAY\n\nALEX\nSaved.\n")
    repository.save_parsed(project.id, "local-demo", scenes, ["parsed"])
    retrieved = repository.get_project(project.id, "local-demo")
    assert retrieved is not None
    assert retrieved.status == "ready"
    assert retrieved.script is not None
    assert retrieved.script.scenes_count == 1
    assert retrieved.scenes[0].dialogue[0]["text"] == "Saved."
