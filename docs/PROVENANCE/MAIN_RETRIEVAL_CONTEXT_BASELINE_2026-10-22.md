# Main-corpus retrieval context — targeted baseline (2026-10-22)

Status: non-canonical technical test result. No canon interpretation or Keeper ruling.

## Method

Fetched three documents from `main` using the GitHub connector and reproduced the logic of `tools/main_retrieval_context_audit.py` in an isolated JavaScript runner. Character windows of 512, 1000 and 2000 with 20% overlap; topic regexes matched concealment or authority terms; status regex searched for a local status/dissent cue. Source text was not modified. This is **not** a full-clone run of the Python script, and does not measure model behaviour.

| File | 512 chars missing/total | 1000 chars missing/total | 2000 chars missing/total |
|---|---:|---:|---:|
| `docs/Future_AI/The_Keepers_Testament.md` | 9/11 | 6/8 | 2/4 |
| `docs/Future_AI/CUSTODIANSHIP_SCROLL.md` | 10/11 | 6/7 | 3/4 |
| `docs/DOCTRINE/GARDEN_CONSTITUTION.md` | 5/8 | 2/4 | 1/2 |
| **Combined** | **24/30** | **14/19** | **6/10** |

At 512 chars, 80% of topic-bearing windows lacked a nearby status cue. At 1000 chars, 73.7%; at 2000 chars, 60%. These counts measure the chosen heuristic, **not** the probability of a reader being misled.

## Interpretation

The Testament labels itself non-law at the start and places its Witness dissent at the end. Middle chunks about concealment often omit both. The Scroll and Constitution also have context-bearing headers or notes that can be detached by naive chunking.

The absence of a local cue does not imply an instruction, a canon violation, or endorsement. This is evidence for **retrieval-side metadata envelopes**, not for editing the authored testimony or inserting repeated warnings into it.

## Follow-up validation

1. Execute the checked-in Python probe on a clean clone; compare JSON results to this baseline.
2. Test whether retrieval preserves `source_path`, `source_sha`, `document_status`, `voice_class`, `authority_scope`, and `unresolved_conflicts` in every returned chunk.
3. Do not infer classifications for unknown documents. Record `unknown_pending_provenance` and flag for review.
4. Review metadata provenance and versioning before treating any envelope as authoritative.
5. Keep existing Marginalia gate and branch isolation unchanged.

## Signature investigation

A GitHub code search found widespread `<!--SIG-->` blocks but did not identify a caller of `scripts/inject_signature.js`. This search is **not** a complete call-graph audit. No signature script change is proposed without knowing its invocation paths.
