#!/usr/bin/env python3
"""Read-only, advisory provenance envelopes. Not canon or Keeper authorization."""
import argparse
import hashlib
import json
from pathlib import Path

UNKNOWN = "unknown_pending_provenance_resolution"
FIELDS = ("document_status", "voice_class", "authority_scope", "authorship_status")

def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def windows(text, size=1000, overlap=0.2):
    if size <= 0 or not 0 <= overlap < 1:
        raise ValueError("Invalid size or overlap")
    step = max(1, round(size * (1 - overlap)))
    for start in range(0, len(text), step):
        end = min(len(text), start + size)
        if text[start:end].strip():
            yield start, end
        if end == len(text):
            break

def voice_for_window(content, doc, start, end):
    """Use source-text anchors; a window spanning speakers is always mixed."""
    segments = doc.get("voice_segments")
    if not segments:
        return doc.get("voice_class", UNKNOWN), "document_level"
    boundaries = [(0, UNKNOWN)]
    for segment in segments:
        marker = segment.get("start_marker")
        voice = segment.get("voice_class")
        if not isinstance(marker, str) or not marker or not isinstance(voice, str) or not voice:
            raise ValueError("Invalid voice segment")
        if content.count(marker) != 1:
            raise ValueError("Voice marker must occur exactly once: " + marker)
        boundaries.append((content.index(marker), voice))
    # A first marker at offset zero replaces the default unknown region.
    if len(boundaries) > 1 and boundaries[1][0] == 0:
        boundaries.pop(0)
    offsets = [p for p, _ in boundaries]
    if offsets != sorted(set(offsets)):
        raise ValueError("Voice markers must be in ascending source order")
    # Include all regions touched by the actual text window.
    voices = set()
    for i, (begin, voice) in enumerate(boundaries):
        finish = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(content)
        if start < finish and end > begin:
            voices.add(voice)
    if len(voices) == 1:
        return voices.pop(), "source_marker_segment"
    return "mixed_voice_boundary", "source_marker_overlap"

def emit(root, manifest, size=1000, overlap=0.2):
    root = Path(root).resolve()
    if manifest.get("status") != "advisory_not_canon":
        raise ValueError("Manifest must be explicitly advisory")
    seen = set()
    for doc in manifest["documents"]:
        rel = doc["path"]
        if rel in seen:
            raise ValueError("Duplicate manifest path: " + rel)
        seen.add(rel)
        source = (root / rel).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            raise ValueError("Missing or unsafe source: " + rel)
        content = source.read_text(encoding="utf-8")
        actual_hash = digest(content)
        expected_hash = doc.get("expected_source_sha256")
        if expected_hash is not None and actual_hash != expected_hash:
            raise ValueError("Pinned source hash mismatch: " + rel)
        # Validate all marker boundaries even when the source is empty.
        voice_for_window(content, doc, 0, len(content))
        for start, end in windows(content, size, overlap):
            part = content[start:end]
            voice, voice_basis = voice_for_window(content, doc, start, end)
            yield {
                "schema": "acacia.retrieval-envelope/0.2-advisory",
                "source_path": rel,
                "source_sha256": actual_hash,
                "source_commit": doc.get("source_commit", "unverified"),
                "start_offset": start,
                "end_offset": end,
                "chunk_sha256": digest(part),
                **{field: (voice if field == "voice_class" else doc.get(field, UNKNOWN)) for field in FIELDS},
                "classification_basis": doc.get("classification_basis", "not_classified"),
                "metadata_trust": "advisory_manifest_unverified",
                "authorization_status": "not_authenticated",
                "keeper_approval": "not_established",
                "canonical_effect": "none",
                "classification_provenance": {
                    "manifest_status": "advisory_not_canon",
                    "method": "human_review_pending",
                    "cryptographic_attestation": "absent"
                },
                "voice_boundary_basis": voice_basis,
                "unresolved_conflicts": doc.get("unresolved_conflicts", []),
                "text": part,
            }

def verify_record(record, original_source_text, trusted_source_sha256):
    """Integrity only. Trusted hash must arrive independently of the record.

    Successful integrity checks never establish Keeper identity, approval, or canon.
    """
    if not isinstance(trusted_source_sha256, str) or len(trusted_source_sha256) != 64:
        return False
    if digest(original_source_text) != trusted_source_sha256:
        return False
    if record.get("source_sha256") != trusted_source_sha256:
        return False
    start, end = record.get("start_offset"), record.get("end_offset")
    if type(start) is not int or type(end) is not int:
        return False
    if not (0 <= start < end <= len(original_source_text)):
        return False
    part = original_source_text[start:end]
    return record.get("text") == part and record.get("chunk_sha256") == digest(part)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--size", type=int, default=1000)
    parser.add_argument("--overlap", type=float, default=0.2)
    args = parser.parse_args()
    with open(args.manifest, encoding="utf-8") as handle:
        manifest = json.load(handle)
    for item in emit(args.root, manifest, args.size, args.overlap):
        print(json.dumps(item, ensure_ascii=False))

if __name__ == "__main__":
    main()
