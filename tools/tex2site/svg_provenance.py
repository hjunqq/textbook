"""Bind each distributed SVG to its current drawing and shared definitions."""
import hashlib
import json
from pathlib import Path


def source_hash(snippet, preamble, definitions):
    values = [snippet, preamble, definitions]
    canonical = json.dumps([s.replace('\r\n', '\n') for s in values], ensure_ascii=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verified_svg(build, filename, expected_hash, require_pdf=False):
    """Return only a matching unmodified build result; old filenames prove nothing."""
    manifest = Path(build) / 'svg-manifest.json'
    if not manifest.is_file():
        return None
    records = json.loads(manifest.read_text(encoding='utf-8')).get('figures', {})
    record = records.get(filename, {})
    svg = Path(build) / filename
    if record.get('source_sha256') != expected_hash or not svg.is_file():
        return None
    if record.get('svg_sha256') != file_hash(svg):
        return None
    if require_pdf:
        pdf = svg.with_suffix('.pdf')
        if not pdf.is_file() or record.get('pdf_sha256') != file_hash(pdf):
            return None
    return svg
