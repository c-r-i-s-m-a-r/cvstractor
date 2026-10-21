import re

FLAGS = re.UNICODE | re.IGNORECASE
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[A-Za-z]{2,}", FLAGS)
PHONE = re.compile(r"\+?\d[\d\s().-]{7,}\d", FLAGS)
URL = re.compile(r"(?:https?://[^\s<>\"']+|www\.[\w-]+\.[\w.-]+)", FLAGS)
LINKEDIN = re.compile(r"(?:https?://)?(?:www\.)?linkedin\.com/in/[\w%.-]+", FLAGS)
GITHUB = re.compile(r"(?:https?://)?(?:www\.)?github\.com/[\w.-]+", FLAGS)
DNI_NIE = re.compile(r"\b(?:\d{8}[A-Za-z]|[XYZxyz]\d{7}[A-Za-z])\b", FLAGS)
MONTH = r"(?:ene(?:ro)?|feb(?:rero)?|mar(?:zo)?|abr(?:il)?|may(?:o)?|jun(?:io)?|jul(?:io)?|ago(?:sto)?|sep(?:t(?:iembre)?)?|oct(?:ubre)?|nov(?:iembre)?|dic(?:iembre)?)"
DATE = re.compile(rf"(?:{MONTH}\.?\s+(?:19|20)\d{{2}}|(?:0?[1-9]|1[0-2])[/.\\-](?:19|20)\d{{2}}|(?:19|20)\d{{2}}|{MONTH}\.?\s+20XX)", FLAGS)
DATE_RANGE = re.compile(rf"(?P<start>{MONTH}\.?\s+(?:(?:19|20)\d{{2}}|20XX)|(?:0?[1-9]|1[0-2])[/.\\-](?:(?:19|20)\d{{2}}|20XX)|(?:19|20)\d{{2}})\s*(?:-|–|—|hasta|a|\s+)\s*(?P<end>{MONTH}\.?\s+(?:(?:19|20)\d{{2}}|20XX)|(?:0?[1-9]|1[0-2])[/.\\-](?:(?:19|20)\d{{2}}|20XX)|(?:19|20)\d{{2}}|actual(?:idad)?|presente)", FLAGS)
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
LOCATION = re.compile(r"\b([A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúñ.-]*(?:\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúñ.-]*)*),\s*([A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúñ.-]*(?:\s+[A-ZÁÉÍÓÚÑ][\wÁÉÍÓÚáéíóúñ.-]*)*)")
JOB_TITLE = re.compile(r"\b(?:asistente|recepcionista|ingenier\w*|administrativ\w*|técnic\w*|tecnic\w*|analista|desarrollador\w*|coordinador\w*|director\w*|gerent\w*|becari\w*|práctic\w*|practic\w*|vendedor\w*|contador\w*|auxiliar|consultor\w*|supervisor\w*|jefe|profesor\w*|docente)\b", FLAGS)
LANGUAGE_LEVEL = re.compile(r"\b(?:nativo|lengua materna|bilingüe|avanzado|intermedio|básico|principiante|a[12]|b[12]|c[12])\b", FLAGS)
SKILL_SEPARATORS = re.compile(r"\s*(?:•|·|;|\||(?<!\w)\-(?!\w))\s*")
NOISE = re.compile(r"^(?:\d{6,}|[-•·\s]+)$")
