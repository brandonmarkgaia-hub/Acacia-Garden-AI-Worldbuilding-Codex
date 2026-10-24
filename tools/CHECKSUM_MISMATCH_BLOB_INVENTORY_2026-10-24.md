# Ten legacy checksum entries — current Git blob inventory (2026-10-24)

**Advisory evidence only. Not Canon, Keeper authentication, or proof of tampering.** The original ten mismatches were reported at historical CI run 39846567770; this inventory independently confirms that each named path still exists on the current default branch and records its current Git blob SHA-1. A Git blob SHA-1 is **not** the current file SHA-256 and must never be compared directly to CHECKSUMS.sha256.

| Path | Recorded SHA-256 in CHECKSUMS.sha256 | Current Git blob SHA-1 |
| --- | --- | --- |
| `STATUS.json` | `be368b7c34d6e4497ee439e240af7867d96da8821afaf2b211b7240316a84236` | `d784f3f41d8dc256b3dae3d7757f211924e22ff4` |
| `docs/Chambers/chambers_index.json` | `2267e8dae38e6d7f0a53bc569241d88ac8616edb7d197db485fb550fb55606b1` | `c1505bef87621c21be7ddb33b764797b71594dbb` |
| `docs/Chambers/index.html` | `083ab6e64d23da6083950ccd9d811a09e2f92bfe0ce3b68cb0feffc910ce7e53` | `4cff6423ab95a015651dec9d162a817758658df0` |
| `docs/Echoes/echoes_index.json` | `6ea28f0b72507d236d33fd0ba1675c33b27b0177e6b7e3bc176ee749fa018636` | `3eb754e67279662928c61c3a35b1f532b31734f5` |
| `docs/Echoes/index.html` | `22b0d1f6e385c87b1c00d116deafd6ee1deff610372aae53088c43d25563e0f5` | `cdc3e7c4d8ae00cdade358f4b783664d3d306c85` |
| `docs/GardenOS/index.html` | `ebbc246f64091c382440bd36794ee70de3f215ffe157db42afdc58a33b20b225` | `ba8015d564d823beda5012bc3a16853abea3c3d3` |
| `docs/Novellas/garden_index.json` | `e1b46ffdeace37bb08bdf354a9be6f6869d8d4b41ea9414d92b65d75106153ea` | `3bb4bca10be3333d58ccba60a7c98ea5d4090269` |
| `docs/Vaults/index.html` | `9fc276a476acc3c6c1485c884e09a6ec8e73776ef6cc16c1069ae55f11bc1a87` | `eae7095020edbe3801851b131133140829c381ce` |
| `docs/docs_urls.json` | `e5101baf3a67f3d59a563de1f4a07dba41b5d83a7e639922f3862ad56c3c5ceb` | `725b01b2b6334c67038c20fcdc52043a42ff6c2d` |
| `machine-index.json` | `7a6ebff65f73237ba6d6e9083c4074e256a5dc85572443c742683adaa435f70e` | `3a3b02b4fb44b21528eb8ca8175288335807606c` |

## Findings and boundaries

- All ten listed paths were retrievable on current main when inspected. No current SHA-256 remeasurement or historical last-modifying-commit attribution is claimed here.
- `.github/scripts/build_docs_folder_indexes.py` explicitly names Chambers, Vaults, Echoes, and GardenOS as output folders, supporting a **generator candidate** for their HTML indexes. This is not proof of why a checksum differs.
- `.github/scripts/build_docs_url_dump.py` declares `docs/docs_urls.json` as an output; `.github/scripts/build_machine_index.py` declares `machine-index.json` as an output. Both need deterministic-build and commit-history review.
- `STATUS.json`, Chambers/Echoes JSON indexes and Novellas JSON index require independent origin and commit-history review; their generation is not established by the three scripts inspected.
- No checksum has been refreshed, no source file modified, and no mismatch marked resolved.

## Next evidence gate

For each path: extract exact current bytes and SHA-256 at a frozen commit; compare to recorded digest; inspect git log for last modification and generator workflows; decide whether the expected hash describes a historical snapshot, current intended artifact, or unexplained drift. Record the exact commit SHA and reviewer decision. Do not restamp CHECKSUMS.sha256 en masse.
