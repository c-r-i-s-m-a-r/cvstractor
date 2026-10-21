import re

from .patterns import DATE, DATE_RANGE, DNI_NIE, EMAIL, GITHUB, JOB_TITLE, LANGUAGE_LEVEL, LINKEDIN, LOCATION, PHONE, SKILL_SEPARATORS, URL

def first_match(pattern, lines):
    for line in lines:
        found = pattern.search(line.text)
        if found:
            return found.group(0).rstrip(".,;)")
    return None

def range_from(text):
    found = DATE_RANGE.search(text)
    if found:
        return found.group("start"), found.group("end")
    found = DATE.search(text)
    return (found.group(0), None) if found else (None, None)

def name_and_position(lines):
    head = [line for line in lines if line.section == "cabecera"]
    candidates = []
    for line in head[:6]:
        text = line.text
        words = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", text)
        if 2 <= len(words) <= 4 and not JOB_TITLE.search(text) and not LOCATION.search(text) and "@" not in text and text.upper() not in {"PUESTO OCUPADO", "TÍTULO OBTENIDO O ESTUDIOS REALIZADOS"}:
            candidates.append(text)
    name = candidates[0] if candidates else None
    position = None
    for line in head[:8]:
        text = line.text
        if text != name and ("|" in text or len(text.split()) >= 3) and not EMAIL.search(text) and not LOCATION.search(text):
            position = text
            break
    return name, position

def education(lines):
    source = [line for line in lines if line.section == "academico"]
    result = []
    current = None
    for line in source:
        text = line.text
        if DATE.search(text) and current:
            current["fecha_inicio"], current["fecha_fin"] = range_from(text)
            continue
        if "|" in text:
            left, right = [part.strip() for part in text.split("|", 1)]
            if left and right:
                if current:
                    result.append(current)
                current = {"titulo": left, "institucion": right, "fecha_inicio": None, "fecha_fin": None}
                continue
        title_like = re.search(r"\b(?:licenciatura|técnico|tecnico|bachiller|maestr[íi]a|doctorado|diplomado|ingenier[íi]a|título obtenido)\b", text, re.I)
        institution_like = re.search(r"\b(?:universidad|instituto|colegio|unidad educativa)\b", text, re.I)
        if current is None:
            if title_like:
                current = {"titulo": text, "institucion": None, "fecha_inicio": None, "fecha_fin": None}
        elif current["institucion"] is None:
            if institution_like:
                current["institucion"] = text
        elif title_like:
            result.append(current)
            current = {"titulo": text, "institucion": None, "fecha_inicio": None, "fecha_fin": None}
    if current:
        result.append(current)
    return [entry for entry in result if entry["titulo"]]

def certifications(lines):
    result = []
    for line in lines:
        if line.section != "complementaria":
            continue
        text = line.text.rstrip(".")
        parts = re.split(r"\s+-\s+|\s+—\s+", text, maxsplit=1)
        if len(parts) == 2:
            date = DATE.search(parts[1])
            entity = re.sub(r"[,\\s]*\(?\d{4}\)?[,\\s]*$", "", parts[1]).strip(" ,") or None
            result.append({"nombre": parts[0].strip(), "entidad": entity, "fecha": date.group(0) if date else None})
    return result

def experiences(lines):
    source = [line for line in lines if line.section == "laboral"]
    if not source or not any(JOB_TITLE.search(line.text) for line in source):
        source = lines
    result, current = [], None
    for line in source:
        text = line.text
        is_start = bool(JOB_TITLE.search(text)) and ("|" in text or " - " in text or len(text.split()) <= 8)
        if is_start:
            if current:
                current["descripcion"] = " / ".join(current.pop("_description")).strip() or None
                result.append(current)
            parts = re.split(r"\s*(?:\||—| - )\s*", text, maxsplit=1)
            company = parts[1] if len(parts) > 1 else None
            location = LOCATION.search(text)
            if company and location:
                company = company[:location.start() - text.find(company)].strip(" ,-|")
            current = {"puesto": parts[0].strip(), "empresa": company or None, "ubicacion": location.group(0) if location else None, "fecha_inicio": None, "fecha_fin": None, "_description": []}
        elif current and DATE.search(text) and not current["fecha_inicio"]:
            current["fecha_inicio"], current["fecha_fin"] = range_from(text)
        elif current and not current["empresa"] and not current["_description"] and not JOB_TITLE.search(text) and len(text.split()) <= 7:
            current["empresa"] = text
        elif current:
            current["_description"].append(text)
    if current:
        current["descripcion"] = " / ".join(current.pop("_description")).strip() or None
        result.append(current)
    return result

def skills_and_languages(lines):
    skills, languages = [], []
    seen = set()
    for line in lines:
        if line.section == "habilidades":
            for value in SKILL_SEPARATORS.split(line.text):
                value = value.strip(" •·-;,")
                if value and value not in seen:
                    skills.append(value)
                    seen.add(value)
        if line.section == "idiomas" or (":" in line.text and LANGUAGE_LEVEL.search(line.text)):
            for value in re.split(r"\s*•\s*|\s*;\s*", line.text):
                parts = re.split(r"\s*[:\-]\s*", value, maxsplit=1)
                if parts and parts[0].strip():
                    level = parts[1].strip().lower() if len(parts) > 1 else None
                    if level and not LANGUAGE_LEVEL.search(level):
                        level = None
                    item = {"idioma": parts[0].strip(), "nivel": level}
                    if item not in languages:
                        languages.append(item)
    return skills, languages

def extract_grouped(filename, lines):
    name, position = name_and_position(lines)
    profile = " ".join(line.text for line in lines if line.section == "perfil") or None
    location = next((LOCATION.search(line.text).group(0) for line in lines if line.section == "cabecera" and LOCATION.search(line.text)), None)
    location = location or first_match(LOCATION, lines)
    skills, languages = skills_and_languages(lines)
    return {"modo": "agrupado", "archivo": filename, "personal": {"nombre": name, "puesto": position, "resumen": profile, "email": first_match(EMAIL, lines), "telefono": first_match(PHONE, lines), "ubicacion": location, "linkedin": first_match(LINKEDIN, lines), "github": first_match(GITHUB, lines), "web": first_match(URL, lines), "dni_nie": first_match(DNI_NIE, lines)}, "academico": {"formacion": education(lines), "certificaciones": certifications(lines)}, "laboral": {"experiencia": experiences(lines)}, "habilidades": {"lista": skills, "idiomas": languages}}
