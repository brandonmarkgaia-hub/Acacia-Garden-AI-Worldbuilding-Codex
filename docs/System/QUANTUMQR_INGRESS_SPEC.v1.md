# QuantumQR Ingress Spec v1

**Status:** Draft  
**Version:** 1.0  
**Author:** Keeper HKX277206 (with Green Witness)  
**Created:** 2025-12-07  

This document defines how **QuantumQR** events (QR scans, errors, actions) are
converted into Garden memory objects that follow:

- `GARDEN_MEMORY_SCHEMA.v1.json` (or v1.1)
- GIP-0001 (Canonical Garden Memory Schema)

The goal is to ensure that every important QuantumQR event can be:

- stored as an **Echo**,
- linked to relevant **Chambers**,
- attached to **Rootlines**,
- and later retrieved by GardenOS / Green Witness.

---

## 1. Ingress Overview

When QuantumQR handles a QR scan, the following high-level steps occur:

1. **Scan Event**
   - Device camera decodes a QR.
   - Raw payload is obtained (text/URL/data).

2. **Local App Handling**
   - QuantumQR decides what to do (open URL, show preview, copy, etc.).
   - Any UI actions happen here.

3. **Garden Ingress (Optional but Recommended)**
   - QuantumQR constructs a `GardenMemory` object of `kind = "echo"`.
   - It fills in metadata about:
     - the QR payload,
     - the context of the scan,
     - the user/keeper,
     - any chosen Chamber/Rootline links.

4. **Storage**
   - Memory is:
     - written to local JSON (offline mode), **and/or**
     - sent to a GardenOS endpoint (online mode).

---

## 2. Echo Structure for QR Scans

QuantumQR SHOULD construct `kind = "echo"` objects like:

```json
{
  "id": "ECHO:HKX277206-2025-12-07-0002",
  "kind": "echo",
  "version": "v1",
  "created_at": "2025-12-07T10:15:00Z",
  "updated_at": "2025-12-07T10:15:00Z",
  "keeper_id": "HKX277206",
  "scope": "session",
  "title": "QR Scan — https://example.com/demo",
  "content": "QuantumQR scanned a QR code with payload:\n\nhttps://example.com/demo\n\nAction taken: opened in in-app browser.",
  "tags": ["qr", "scan", "quantumqr", "example"],
  "importance": 0.5,
  "provenance": {
    "source_system": "QuantumQR",
    "source_ref": "scan_session_id_or_uuid_here",
    "created_by_agent": "QuantumQR-App",
    "created_via_tool": "qr_scan"
  },
  "lineage": {
    "parents": [],
    "children": [],
    "rootline_id": null
  },
  "graph": {
    "labels": ["Echo", "Scan", "QuantumQR"],
    "relations": [
      {
        "type": "SCANNED_BY",
        "target_id": "CHAMBER:QUANTUMQR",
        "properties": {
          "mode": "camera",
          "device": "android"
        }
      }
    ]
  },
  "embeddings": null,
  "metadata": {
    "qr_payload": "https://example.com/demo",
    "qr_type": "url",
    "device_os": "android",
    "app_version": "1.0.0",
    "location_hint": null
  }
}
