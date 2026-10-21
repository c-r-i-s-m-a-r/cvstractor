import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from cvstractor.grouped import extract_grouped
from cvstractor.normalize import normalize_lines
from cvstractor.plain import extract_plain
from cvstractor.readers import read_document
from cvstractor.sections import assign_sections

MAX_SIZE = 5 * 1024 * 1024
app = FastAPI(title="CVstractor")
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")], allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])
DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
app.mount("/assets", StaticFiles(directory=DIST / "assets", check_dir=False), name="assets")

async def process(file):
    if file is None or not file.filename:
        raise HTTPException(400, "Debe enviar un archivo")
    filename = Path(file.filename).name
    if Path(filename).suffix.lower() not in {".docx", ".odt"}:
        raise HTTPException(400, "Formato no admitido. Use .docx u .odt")
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(413, "Archivo demasiado grande (máx. 5 MB)")
    if not content.startswith(b"PK\x03\x04"):
        raise HTTPException(400, "El archivo no contiene un documento válido")
    try:
        raw_lines = read_document(filename, content)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(422, "No se pudo extraer texto del documento") from error
    lines = normalize_lines(raw_lines)
    if not lines:
        raise HTTPException(422, "Documento sin texto extraíble")
    assigned, sections = assign_sections(lines)
    if not assigned:
        raise HTTPException(422, "Documento sin datos detectables")
    return filename, assigned, sections

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/extract/grouped")
async def grouped(file: UploadFile = File(...)):
    filename, lines, _ = await process(file)
    return extract_grouped(filename, lines)

@app.post("/api/extract/full")
async def full(file: UploadFile = File(...)):
    filename, lines, sections = await process(file)
    return extract_plain(filename, lines, sections)

@app.get("/")
def frontend():
    dist = DIST / "index.html"
    if not dist.exists():
        raise HTTPException(404, "El frontend no está compilado")
    return FileResponse(dist)
