import re
import json
import sys
import zipfile
import html


SECCIONES = (
    'EXPERIENCIA', 'HABILIDADES', 'FORMACIÓN', 'EDUCACIÓN', 'CURSOS',
    'IDIOMAS', 'REFERENCIAS', 'PROYECTOS', 'CERTIFICACIONES',
)
ENCABEZADOS_NO_NOMBRE = SECCIONES + (
    'PERFIL', 'RESUMEN', 'CONTACTO', 'DATOS PERSONALES', 'OBJETIVOS',
    'CURRICULUM', 'CURRÍCULUM', 'HOJA DE VIDA', 'PROFILE',
)
PATRON_CALLE = re.compile(r'^(?:CALLE|AVENIDA|AV\.?|BULEVAR|BLVD\.?|CAMINO|PLAZA|PASEO)\b', re.IGNORECASE)
NOMBRE_MAYUSCULAS = re.compile(r"^[A-ZÁÉÍÓÚÜÑ]+(?:[ '-][A-ZÁÉÍÓÚÜÑ]+)*(?:\s+[A-ZÁÉÍÓÚÜÑ]+(?:[ '-][A-ZÁÉÍÓÚÜÑ]+)*){0,4}$")
NOMBRE_TITLECASE = re.compile(r"^[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+(?:[ '-][A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)*(?:\s+[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+(?:[ '-][A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]+)*){0,4}$")


class ExtraerTexto:
    @staticmethod
    def de_xml(contenido_xml):
        """Devuelve el texto del XML con un párrafo por línea."""
        if not contenido_xml:
            return ''
        if '<' not in contenido_xml:
            return contenido_xml.strip()

        lineas = []

        # .docx: párrafos <w:p>...</w:p> con runs <w:t>
        if re.search(r'</?w:p(?:\s[^>]*)?>', contenido_xml):
            for trozo in re.split(r'</?w:p(?:\s[^>]*)?>', contenido_xml):
                trozo = re.sub(r'<w:(?:tab|br)[^>]*/>', ' ', trozo)
                runs = re.findall(r'<w:t[^>]*>(.*?)</w:t>', trozo, re.DOTALL)
                if runs:
                    texto = re.sub(r'<[^>]+>', '', ''.join(runs))
                    lineas.append(html.unescape(texto).strip())

        # .odt: párrafos <text:p>/<text:h> (partir solo por aperturas)
        elif re.search(r'<text:(?:p|h)(?:\s[^>]*)?/?>', contenido_xml):
            xml_norm = re.sub(
                r'<text:(p|h)((?:\s[^>]*)?)/>',
                r'<text:\1\2></text:\1>',
                contenido_xml,
            )
            for i, trozo in enumerate(re.split(r'<text:(?:p|h)(?:\s[^>]*)?>', xml_norm)):
                trozo = re.sub(r'<text:(?:line-break|tab|s)[^>]*/>', ' ', trozo)
                cuerpo = html.unescape(re.sub(r'<[^>]+>', '', trozo))
                linea = re.sub(r'[ \t]+', ' ', cuerpo).strip()
                if i == 0 and not linea:
                    continue  # prologo XML, sin párrafo
                lineas.append(linea)

        if lineas:
            return '\n'.join(lineas)

        # Fallback: XML sin párrafos conocidos
        texto = re.sub(r'<[^>]+>', ' ', contenido_xml)
        texto = html.unescape(texto)
        return re.sub(r'\s+', ' ', texto).strip()


def _nombre_valido(candidato):
    candidato = candidato.strip()
    if not 3 <= len(candidato) <= 60:
        return False
    if not NOMBRE_MAYUSCULAS.fullmatch(candidato) and not NOMBRE_TITLECASE.fullmatch(candidato):
        return False
    if len(candidato.split()) > 5:
        return False
    mayusculas = candidato.upper()
    for prohibido in ENCABEZADOS_NO_NOMBRE:
        if re.search(rf'\b{re.escape(prohibido)}\b', mayusculas):
            return False
    if PATRON_CALLE.match(candidato):
        return False
    return True


def _extraer_nombre(lineas):
    for linea in lineas:
        if _nombre_valido(linea):
            return linea
    return ''


def _extraer_telefono(texto):
    for match in re.finditer(r'\+?[\d][\d\s.\-]{5,20}\d', texto):
        bruto = match.group(0)
        digitos = re.sub(r'\D', '', bruto)
        if not 7 <= len(digitos) <= 15:
            continue
        grupos = re.findall(r'\d+', bruto)
        if len(grupos) > 1 and all(len(g) == 4 and g[:2] in ('19', '20') for g in grupos):
            continue  # rango de años, no un teléfono
        return bruto.strip(' .,-')
    return ''


def _cortar_bloque(resto):
    corte = len(resto)
    fin_linea_vacia = re.search(r'\n\s*\n', resto)
    if fin_linea_vacia:
        corte = min(corte, fin_linea_vacia.start())
    encabezados = '|'.join(SECCIONES + ('PERFIL', 'CONTACTO'))
    fin_encabezado = re.search(rf'\n\s*(?:{encabezados})\b', resto, re.IGNORECASE)
    if fin_encabezado:
        corte = min(corte, fin_encabezado.start())
    return resto[:min(corte, 400)].strip()


def _extraer_bloque(texto, encabezado):
    match = re.search(encabezado, texto)
    if not match:
        match = re.search(encabezado, texto, re.IGNORECASE)
    if not match:
        return None
    bloque = _cortar_bloque(texto[match.start():])
    return bloque or None


def _extraer_resumen(texto):
    encabezado = r'^(?:PERFIL|RESUMEN|PROFILE)(?:\s+[A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ ]{0,30})?$'
    match = re.search(encabezado, texto, re.IGNORECASE | re.MULTILINE)
    if not match:
        return ''
    resto = texto[match.end():].lstrip('\n')
    return _cortar_bloque(resto)


def _extraer_direccion(lineas):
    # 1. Línea con formato de calle/avenida
    for linea in lineas:
        if PATRON_CALLE.match(linea) and len(linea) <= 70:
            if re.fullmatch(r"[\wÁÉÍÓÚáéíóúñüÑ ,.\-ºª°]+", linea):
                return linea
    # 2. En la línea de contacto (con email), el tramo anterior al primer bullet
    for linea in lineas:
        if '@' in linea:
            tramo = re.split(r'[•·|]', linea)[0].strip()
            if (
                2 <= len(tramo.split()) <= 6
                and ',' in tramo
                and len(tramo) <= 60
                and re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúñüÑ][\wÁÉÍÓÚáéíóúñüÑ,.' ]*", tramo)
            ):
                return tramo
    return ''


def extraer_datos_cv():
    ruta_arg = sys.argv[1]

    if not ruta_arg or not ruta_arg.strip():
        return {'personal': {'nombre': '', 'email': '', 'telefono': '', 'direccion': ''},
                'contacto': {'github': '', 'linkedin': '', 'web': ''},
                'educacion': [], 'experiencia': [], 'habilidades': [], 'resumen': ''}

    # Intentar abrir como archivo ZIP (formato .odt/.docx)
    try:
        with zipfile.ZipFile(ruta_arg, 'r') as z:
            nombres = z.namelist()
            contenido_xml = None
            for nombre in nombres:
                bajo = nombre.lower()
                # .odt guarda el texto en content.xml; .docx en word/document.xml
                if bajo.endswith('content.xml') or bajo == 'word/document.xml':
                    contenido_xml = z.read(nombre).decode('utf-8', errors='replace')
                    break
            if contenido_xml is None:
                if nombres:
                    contenido_xml = z.read(nombres[0]).decode('utf-8', errors='replace')
                else:
                    contenido_xml = ''
    except (zipfile.BadZipFile, FileNotFoundError):
        # No es un ZIP, leer como archivo de texto directo
        try:
            with open(ruta_arg, 'r', encoding='utf-8', errors='replace') as f:
                contenido_xml = f.read()
        except Exception:
            contenido_xml = ''

    texto = ExtraerTexto.de_xml(contenido_xml)
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]

    datos = {
        'personal': {
            'nombre': '',
            'email': '',
            'telefono': '',
            'direccion': ''
        },
        'contacto': {
            'github': '',
            'linkedin': '',
            'web': ''
        },
        'educacion': [],
        'experiencia': [],
        'habilidades': [],
        'resumen': ''
    }

    if not texto:
        return datos

    # 1. Email: patrón estándar
    match_email = re.search(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', texto, re.IGNORECASE)
    if match_email:
        datos['personal']['email'] = match_email.group(0)

    # 2. Nombre: una línea completa con aspecto de nombre (sin puntuación)
    datos['personal']['nombre'] = _extraer_nombre(lineas)

    # 3. Teléfono: 7-15 dígitos, descartando rangos de años
    datos['personal']['telefono'] = _extraer_telefono(texto)

    # 4. Dirección: línea tipo calle o tramo de ciudad en la línea de contacto
    datos['personal']['direccion'] = _extraer_direccion(lineas)

    # 5. GitHub
    match_github = re.search(
        r'github(?:\.(?:com|io|dev))?/([A-Za-z0-9-]+(?:/[A-Za-z0-9-]+)*)', texto, re.IGNORECASE
    )
    if match_github:
        datos['contacto']['github'] = match_github.group(1).strip('/')

    # 6. LinkedIn
    match_linkedin = re.search(r'linkedin\.com/in/([A-Za-z0-9-]+)', texto, re.IGNORECASE)
    if match_linkedin:
        datos['contacto']['linkedin'] = match_linkedin.group(1)

    # 7. Web personal (excluyendo github/linkedin)
    for match_web in re.finditer(r'https?://[^\s•|]+|www\.[^\s•|]+', texto, re.IGNORECASE):
        url = match_web.group(0).rstrip('.,;')
        if 'github.' in url.lower() or 'linkedin.' in url.lower():
            continue
        datos['contacto']['web'] = url
        break

    # 8. Secciones por palabras clave (mayúsculas primero, bloque hasta el siguiente encabezado)
    bloque = _extraer_bloque(texto, r'EXPERIENCIA')
    if bloque:
        datos['experiencia'] = [bloque]
    bloque = _extraer_bloque(texto, r'HABILIDADES')
    if bloque:
        datos['habilidades'] = [bloque]
    bloque = _extraer_bloque(texto, r'FORMACIÓN|EDUCACIÓN')
    if bloque:
        datos['educacion'] = [bloque]

    # 9. Resumen: texto tras el encabezado PERFIL/RESUMEN
    datos['resumen'] = _extraer_resumen(texto)

    return datos


if __name__ == '__main__':
    datos = extraer_datos_cv()
    print(json.dumps(datos, ensure_ascii=False))
