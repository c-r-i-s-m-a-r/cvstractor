from pathlib import Path

from cvstractor.grouped import extract_grouped
from cvstractor.normalize import normalize_lines
from cvstractor.readers import read_document
from cvstractor.sections import assign_sections

ROOT = Path(__file__).resolve().parents[2]

def grouped_document(name):
    path = ROOT / ".cvs" / name
    lines = normalize_lines(read_document(name, path.read_bytes()))
    assigned, _ = assign_sections(lines)
    return extract_grouped(name, assigned)

def test_grouped_cv_f1_has_core_information():
    result = grouped_document("cv_f1.docx")
    assert result["personal"]["nombre"] == "ALEXANDRA MORALES VEGA"
    assert result["personal"]["email"] == "alexandra.morales@example.com"
    assert result["academico"]["formacion"]
    assert result["laboral"]["experiencia"]
    assert result["habilidades"]["idiomas"]

def test_grouped_has_fixed_top_level_shape():
    result = grouped_document("288-curriculum-vitae-bolivia.docx")
    assert set(result) == {"modo", "archivo", "personal", "academico", "laboral", "habilidades"}
    assert result["personal"]["telefono"] == "+591 00 000 0000"
