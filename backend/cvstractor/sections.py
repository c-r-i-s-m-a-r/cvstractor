import re
import unicodedata
from dataclasses import dataclass

HEADERS = {
    "contacto": {"contacto", "datos personales", "informacion de contacto"},
    "perfil": {"perfil", "perfil profesional", "resumen", "sobre mi", "presentacion"},
    "laboral": {"experiencia", "experiencia laboral", "experiencia profesional", "trabajo", "empleo"},
    "academico": {"formacion", "formacion academica", "educacion", "academica", "estudios", "titulacion"},
    "habilidades": {"habilidades", "competencias", "destrezas"},
    "idiomas": {"idiomas"},
    "complementaria": {"cursos", "certificaciones", "formacion complementaria", "capacitaciones", "cursos complementarios"},
    "intereses": {"intereses", "pasatiempos", "hobbies"},
}

@dataclass
class SectionLine:
    text: str
    position: int
    section: str

def comparable(value):
    value = unicodedata.normalize("NFD", value.lower())
    return " ".join("".join(char for char in value if unicodedata.category(char) != "Mn").split())

def header_for(value):
    normalized = comparable(re.sub(r"[:\-]+$", "", value.strip()))
    for name, aliases in HEADERS.items():
        if normalized in aliases:
            return name
    return None

def assign_sections(lines):
    current = "cabecera"
    items = []
    names = ["cabecera"]
    for line in lines:
        found = header_for(line.text)
        if found:
            current = found
            if found not in names:
                names.append(found)
            continue
        items.append(SectionLine(line.text, line.position, current))
    return items, names
