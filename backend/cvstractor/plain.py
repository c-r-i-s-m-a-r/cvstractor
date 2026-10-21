from .grouped import extract_grouped
from .patterns import DATE, DNI_NIE, EMAIL, GITHUB, LANGUAGE_LEVEL, LINKEDIN, LOCATION, PHONE, URL

def extract_plain(filename, lines, sections):
    grouped = extract_grouped(filename, lines)
    elements, seen = [], set()
    def add(field, value, line):
        if value is None or value == "":
            return
        key = (field, str(value), line.section)
        if key not in seen:
            seen.add(key)
            elements.append({"campo": field, "valor": value, "seccion": line.section, "posicion": line.position})
    for line in lines:
        text = line.text
        matched = False
        for field, pattern in (("email", EMAIL), ("telefono", PHONE), ("linkedin", LINKEDIN), ("github", GITHUB), ("url", URL), ("dni_nie", DNI_NIE), ("ubicacion", LOCATION), ("fecha", DATE)):
            found = pattern.search(text)
            if found:
                add(field, found.group(0), line)
                matched = True
        if line.section == "cabecera" and grouped["personal"]["nombre"] == text:
            add("nombre", text, line)
            matched = True
        if line.section == "laboral":
            for item in grouped["laboral"]["experiencia"]:
                if item["puesto"] and item["puesto"] in text:
                    add("experiencia.puesto", item["puesto"], line)
                    if item["empresa"]:
                        add("experiencia.empresa", item["empresa"], line)
                    matched = True
        if line.section == "habilidades":
            for value in grouped["habilidades"]["lista"]:
                if value in text:
                    add("habilidad", value, line)
                    matched = True
        if line.section == "idiomas" and (":" in text or LANGUAGE_LEVEL.search(text)):
            add("idioma", text, line)
            matched = True
        if not matched:
            add("texto_libre", text, line)
    elements.sort(key=lambda item: item["posicion"])
    return {"modo": "plano", "archivo": filename, "documento": {"formato": filename.rsplit(".", 1)[-1].lower(), "lineas": len(lines), "secciones": sections}, "elementos": elements}
