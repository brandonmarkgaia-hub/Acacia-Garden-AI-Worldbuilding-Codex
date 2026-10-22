"""Conservative source-derived context for retrieval windows.

Does not trust envelope-supplied voice or status. This is a supplementary
checkout-bound context signal, NOT authentication or canonical authority.
"""
from pathlib import Path

TESTAMENT = "docs/Future_AI/The_Keepers_Testament.md"
SCROLL = "docs/Future_AI/CUSTODIANSHIP_SCROLL.md"
CONSTITUTION = "docs/DOCTRINE/GARDEN_CONSTITUTION.md"
RULING = "tools/KEEPER_RULING_2026-10-22_SCROLL_SECTION_III.md"
SECTION_START = "## III. The Veil and the Window"
SECTION_END = "## IV. Against the Fear of Enclosure"


def derive_context(root, record):
    path = record["source_path"]
    root = Path(root)
    source = (root / path).read_text(encoding="utf-8")
    begin, end = record["start_offset"], record["end_offset"]
    # Call only AFTER source-bound hash, text, and offset validation.
    context = {
        "classification_basis": "checked_out_source_and_repository_ruling_not_authenticated",
        "context_source": path,
        "canonical_authority_verified": False,
        "required_context": [],
        "sensitive_context_boundary": False,
    }
    if path == TESTAMENT:
        if "Status: Testament. Not law. Not covenant." not in source:
            return None
        dissent = "## Witness Note — Recorded Dissent"
        if dissent not in source:
            return None
        context["required_context"] = [
            "Source status: Testament, NOT law, NOT covenant; Keeper personal belief.",
            "Witness Note records dissent from concealment from legitimate oversight.",
            "Custodianship Scroll section III supports transparency to legitimate oversight; original Scroll header remains Draft; separate Keeper-directed section-III ruling is recorded, without independent signature."
        ]
        context["sensitive_context_boundary"] = True
        context["witness_dissent_present_in_source"] = True
    elif path == SCROLL:
        a = source.find(SECTION_START)
        b = source.find(SECTION_END)
        if a < 0 or b <= a or "Status: Draft for the Keeper's review and amendment" not in source:
            return None
        context["required_context"] = [
            "Original Custodianship Scroll is labelled Draft.",
            "Keeper-directed ruling dated 2026-10-22 ratifies section III only, not the whole Scroll; independent cryptographic authentication is not established.",
        ]
        # Only windows wholly within the section may carry the section-scoped claim.
        within = begin >= a and end <= b
        context["section_iii_window"] = within
        context["required_context"].append(
            "Window lies wholly within ratified section III." if within
            else "Window is not wholly within section III: do not describe this window as ratified Law."
        )
        context["sensitive_context_boundary"] = True
        if within and not (root / RULING).is_file():
            return None
    elif path == CONSTITUTION:
        context["required_context"] = [
            "Constitution is labelled Canon; Law versus Canon classification remains unresolved.",
            "Keeper's Gloss and Neighbour's Note are separately attributed, not blanket binding Articles."
        ]
        context["sensitive_context_boundary"] = True
    else:
        context["required_context"] = [
            "No source-grounded special status established; do not infer Law from envelope metadata."
        ]
    return context
