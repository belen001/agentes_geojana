from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from .models import DocumentRecord, Evidence


SUPPORTED_TEXT = {".md", ".txt", ".csv", ".json", ".yaml", ".yml"}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def discover_documents(docs_dir: Path) -> list[Path]:
    if not docs_dir.exists():
        raise FileNotFoundError(f"No existe la carpeta de documentos: {docs_dir}")
    return sorted(path for path in docs_dir.rglob("*") if path.is_file())


def extract_document(path: Path) -> DocumentRecord:
    suffix = path.suffix.lower()
    sha = sha256_file(path)
    if suffix in SUPPORTED_TEXT:
        return _extract_text(path, sha)
    if suffix == ".docx":
        return _extract_docx(path, sha)
    if suffix == ".pdf":
        return _extract_pdf(path, sha)
    return DocumentRecord(path, sha, suffix.lstrip(".") or "unknown", "unsupported")


def _extract_text(path: Path, sha: str) -> DocumentRecord:
    try:
        return DocumentRecord(path, sha, path.suffix.lower().lstrip("."), "ok", path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        return DocumentRecord(path, sha, "text", "failed", notes=["El archivo no esta en UTF-8."])


def _extract_docx(path: Path, sha: str) -> DocumentRecord:
    try:
        with zipfile.ZipFile(path) as docx:
            xml = docx.read("word/document.xml")
    except Exception as exc:  # noqa: BLE001
        return DocumentRecord(path, sha, "docx", "failed", notes=[str(exc)])

    root = ElementTree.fromstring(xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", namespace):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return DocumentRecord(path, sha, "docx", "ok", "\n".join(paragraphs))


def _extract_pdf(path: Path, sha: str) -> DocumentRecord:
    pypdf_text = _extract_pdf_with_pypdf(path)
    if pypdf_text:
        return DocumentRecord(path, sha, "pdf", "ok", pypdf_text)

    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        try:
            proc = subprocess.run(
                [pdftotext, "-layout", str(path), "-"],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            return DocumentRecord(path, sha, "pdf", "ok", proc.stdout)
        except Exception as exc:  # noqa: BLE001
            return DocumentRecord(path, sha, "pdf", "failed", notes=[str(exc)])

    return DocumentRecord(
        path,
        sha,
        "pdf",
        "not_extracted",
        notes=["Instala pypdf o pdftotext para extraer texto de PDF. No se genero contenido inferido."],
    )


def _extract_pdf_with_pypdf(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:  # noqa: BLE001
        return ""

    try:
        reader = PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        return "\n\n".join(page for page in pages if page.strip())
    except Exception:  # noqa: BLE001
        return ""


def chunk_document(record: DocumentRecord, chunk_size: int = 2400, overlap: int = 240) -> list[Evidence]:
    if record.extraction_status != "ok" or not record.text.strip():
        return []

    normalized = re.sub(r"\n{3,}", "\n\n", record.text).strip()
    chunks: list[Evidence] = []
    start = 0
    index = 0
    while start < len(normalized):
        end = min(len(normalized), start + chunk_size)
        text = normalized[start:end].strip()
        if text:
            evidence_id = f"ev-{record.sha256[:12]}-{index:04d}"
            chunks.append(
                Evidence(
                    evidence_id=evidence_id,
                    source_path=str(record.path),
                    source_sha256=record.sha256,
                    chunk_index=index,
                    text=text,
                )
            )
            index += 1
        if end == len(normalized):
            break
        start = max(end - overlap, start + 1)
    return chunks
