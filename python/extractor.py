import re
import json
import sys
import zipfile


class ExtraerTexto:
    @staticmethod
    def de_xml(contenido_xml):
        """Extrae texto simple del contenido XML de docx/odt"""
        # Primero intentamos extraer texto de etiquetas w:t (propio de .docx)
        try:
            textos = re.findall(r'<w:t>(.*?)</w:t>', contenido_xml, re.DOTALL)
        except Exception:
            textos = []
        
        if textos and len(textos) > 2:
            # Si hay muchos textos w:t, es probable que sea un .docx
            # Unimos todos los textos encontrados, eliminando etiquetas internas
            partes_texto = []
            for t in textos:
                t_limpio = re.sub(r'<[^>]+>', '', t)
                partes_texto.append(t_limpio.strip())
            texto = ' '.join(partes_texto)
        else:
            # Fallback: formato .odt u otros - remover etiquetas XML básicas
            texto = re.sub(r'<[^>]+>', ' ', contenido_xml)
            # Remover nombrespaces tipo w:, o: etc. antes de quitar etiquetas
            texto = re.sub(r'xmlns:[^=]+="[^"]*"', '', texto)
            # Remover etiquetas w: específicas
            texto = re.sub(r'<w:[^>]+>', ' ', texto)
            texto = re.sub(r'</w:[^>]+>', ' ', texto)
            # Normalizar espacios múltiples
            texto = re.sub(r'\s+', ' ', texto)
        
        return texto.strip()


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
                if 'content.xml' in nombre.lower():
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
    patron_email = re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', re.IGNORECASE)
    match_email = patron_email.search(texto)
    if match_email:
        datos['personal']['email'] = match_email.group(0)
    
    # 2. Nombre: buscar patrón "Nombre Apellido" -para CVs no deterministas
    # Patrones en orden de prioridad:
    # 1. Nombre al inicio del texto
    # 2. Después de "PERFIL:" o "RESUMEN:" (para CVs modelo/plantilla)
    # 3. Cualquier secuencia que empiece con mayúscula en el texto
    patrones_nombre = [
        # Nombre al inicio: "Juan Pérez ..."  
        r'(?:^|\s)([A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóú]+)*)',
        # Después de "PERFIL:" o "RESUMEN:" - para CVs modelo
        r'(?:PERFIL|RESUMEN)[:\s]+([A-ZÁÉÍÓÚ][a-zA-ZÁÉÍÓÚ\s]{3,50})',
        # Cualquier palabra que empiece con mayúscula (último recurso)
        r'^[A-ZÁÉÍÓÚ][a-zA-ZÁÉÍÓÚ\s]{2,50}$',
    ]
    
    nombre_asignado = False
    for patron in patrones_nombre:
        match_nombre = re.search(patron, texto, re.MULTILINE)
        if match_nombre:
            if len(match_nombre.groups()) >= 1 and match_nombre.group(1):
                nombre_completo = match_nombre.group(1).strip()
            elif match_nombre.groups():
                nombre_completo = match_nombre.group(0).strip()
            else:
                continue
            
            # Validar: mínimo 3 chars, máximo 80, letras y espacios/acentos
            if not nombre_asignado and len(nombre_completo) >= 3 and len(nombre_completo) < 80:
                if all(c.isalpha() or c.isspace() or c in 'ÁÉÍÓÚáéíóÚ' for c in nombre_completo.replace(' ', '')):
                    # Tener al menos 1 "palabra" (grupo de letras separadas por espacios)
                    if len(nombre_completo.split()) >= 1:
                        datos['personal']['nombre'] = nombre_completo.strip()
                        nombre_asignado = True
                        break  # Detenerse al encontrar el primer nombre válido
    
    # 3. Teléfono: formato +34 600 123 456 o 600 123 456
    patron_telefono = re.compile(r'(?:\+\d{1,3}[\s-]?)?\d{3}[\s-]?\d{3}[\s-]?\d{3}')
    match_telefono = patron_telefono.search(texto)
    if match_telefono:
        telefono = match_telefono.group(0)
        # Filtrar: el teléfono debe tener entre 7 y 15 dígitos (sin contar +, -, (, ))
        digitos = re.sub(r'\D', '', telefono)
        if 7 <= len(digitos) <= 15:
            datos['personal']['telefono'] = telefono
    
    # 4. GitHub
    patron_github = re.compile(r'github[/\.\s]([A-Za-z0-9-]+)', re.IGNORECASE)
    match_github = patron_github.search(texto)
    if match_github:
        datos['contacto']['github'] = match_github.group(1)
    
    # 5. LinkedIn
    patron_linkedin = re.compile(r'linkedin\.com/in/([A-Za-z0-9-]+)', re.IGNORECASE)
    match_linkedin = patron_linkedin.search(texto)
    if match_linkedin:
        datos['contacto']['linkedin'] = match_linkedin.group(1)
    
    # 6. Detectar secciones por palabras clave
    # Buscar texto después de encabezados de sección comunes
    seccion_patterns = [
        r'EXPERIENCIA[^\n]{0,200}',
        r'HABILIDADES[^\n]{0,200}',
        r'FORMACIÓN[^\n]{0,200}',
    ]
    
    for pattern in seccion_patterns:
        matches = re.findall(pattern, texto, re.IGNORECASE)
        if matches:
            limpio = matches[0].strip()
            # Categorizar basado en qué patrón hizo match
            if 'EXPERIENCIA' in pattern.upper():
                if not datos['experiencia']:
                    datos['experiencia'] = [limpio[:200]]
            elif 'HABILIDADES' in pattern.upper():
                if not datos['habilidades']:
                    datos['habilidades'] = [limpio[:200]]
            elif 'FORMACIÓN' in pattern.upper():
                if not datos['educacion']:
                    datos['educacion'] = [limpio[:200]]
    
    return datos


if __name__ == '__main__':
    datos = extraer_datos_cv()
    print(json.dumps(datos, ensure_ascii=False))