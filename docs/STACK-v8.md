# Professional Stack — VTB Supreme v8

## 1. Preservation
- SHA-256 manifests (`vtb/preservation.py`)
- Internet Archive / Wayback for historical corroboration
- `wayback-machine-downloader` as a candidate tool after TOOLCHECK
- `yt-dlp` / `gallery-dl` only for public, lawfully accessible media
- original/derived artifacts remain distinct

## 2. Brazilian public records
Preferred source classes include PNCP/Compras.gov.br, transparency portals, TCU/TCE/TCM, CGU, TSE/TRE, SICONFI, CEIS/CNEP/CEPIM, CNJ/DataJud for discovery, competent courts, official gazettes, legislative portals and public corporate registries when lawfully accessible.

## 3. Documents and reconciliation
- PyMuPDF / Docling for extraction
- OCRmyPDF only as OCR fallback
- Trafilatura for web text extraction
- OpenRefine for normalization and reconciliation
- Aleph/FollowTheMoney-compatible workflows as optional investigative document/entity tooling

## 4. Graphs
- NetworkX is the default reproducible analytics layer
- Neo4j is an optional persistent graph backend
- Gephi is optional visualization/analysis
- Maltego/Linkurious/yEd can be used as optional interfaces, never as evidentiary authorities

## 5. Financial/procurement analytics
- Money-flow: estimated → awarded → contracted/amended → committed → liquidated → paid → executed
- Price intelligence must normalize specification, unit, quantity, geography, date, freight and commercial conditions
- HHI, Benford, clustering, centrality and outliers produce **signals for verification**, not findings of fraud

## 6. Structured analytic techniques
VTB uses public, general-purpose analytic techniques rather than claiming access to secret or agency-internal doctrine:
- Analysis of Competing Hypotheses (ACH)
- Devil's Advocate / Red Team
- timeline reconstruction
- link/network analysis
- source evaluation
- falsification and contradiction search
- missing-evidence analysis
- next-best-query prioritization

## 7. Digital footprint boundary
Public posts/pages may be preserved when materially relevant to a legitimate public-interest question. The default stack does **not** automate private-person surveillance, residential tracking, breach-data aggregation, credentialed scraping or access-control bypass.

## 8. What makes the stack professional
Power is measured by reproducibility and error control, not tool count. Every major conclusion must survive entity resolution, provenance, independent source lineage, alternative hypotheses, contradiction search, legal validation when relevant, Red Team and QA.
