from io import BytesIO
from pathlib import Path

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from odf import teletype
from odf.opendocument import load
from odf.table import Table as OdtTable, TableCell, TableRow
from odf.text import P

def _docx_table(table):
    lines = []
    seen = set()
    for row in table.rows:
        for cell in row.cells:
            key = id(cell._tc)
            if key in seen:
                continue
            seen.add(key)
            for paragraph in cell.paragraphs:
                if paragraph.text.strip():
                    lines.append(paragraph.text)
            for nested in cell.tables:
                lines.extend(_docx_table(nested))
    return lines

def read_docx(content):
    document = Document(BytesIO(content))
    lines = []
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            paragraph = Paragraph(child, document)
            if paragraph.text.strip():
                lines.append(paragraph.text)
        elif child.tag.endswith("}tbl"):
            lines.extend(_docx_table(Table(child, document)))
    if len(lines) <= 1:
        lines = []
        for paragraph in document.element.body.xpath(".//w:p"):
            value = "".join(node.text or "" for node in paragraph.xpath("./w:r/w:t"))
            if value.strip():
                lines.append(value)
    return lines

def _odt_nodes(node):
    for child in node.childNodes:
        if isinstance(child, P):
            value = teletype.extractText(child).strip()
            if value:
                yield value
        elif isinstance(child, OdtTable):
            for row in child.childNodes:
                if isinstance(row, TableRow):
                    for cell in row.childNodes:
                        if isinstance(cell, TableCell):
                            yield from _odt_nodes(cell)
        else:
            yield from _odt_nodes(child)

def read_odt(content):
    document = load(BytesIO(content))
    return list(_odt_nodes(document.text))

def read_document(filename, content):
    suffix = Path(filename).suffix.lower()
    if suffix == ".docx":
        return read_docx(content)
    if suffix == ".odt":
        return read_odt(content)
    raise ValueError("Formato no admitido")
