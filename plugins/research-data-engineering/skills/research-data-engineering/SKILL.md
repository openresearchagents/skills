---
name: research-data-engineering
description: Best practices for an agent building analysis-ready research datasets from scattered sources (open-data portals, PDF reports, spreadsheets, archived web pages, records requests) and from sensitive data held under a data use agreement. Covers a source catalog, rerunnable ingestion with provenance and publication dates, extracting tables and figures from PDFs with independent validation, and keeping protected records (PII, PHI, HIPAA, FERPA, confidential data) out of the agent's context. Includes a module for public-health and surveillance data (mortality, overdose, EMS, hospital and death records, suppressed small counts, reporting delays). Use this skill whenever the user asks to download, scrape, clean, merge, geocode, extract or validate data for research, pull numbers out of a PDF report or dashboard, build a panel or feature table for a model or backtest, or work in a repository that holds record-level data about people, even if they do not mention privacy or validation.
compatibility: Python 3.10+ with pandas (pyarrow for Parquet) for the bundled scripts. No network calls and no API keys; nothing in this skill sends data to an outside service.
metadata:
  version: "0.4"
  last-reviewed: "2026-10-28"
---

# Research data engineering with an agent

The aim is a dataset that someone else can audit: they can see where every value came from, when
it became public, what was checked, and what was not. Three rules underlie everything:

1. **The agent writes code; the code touches the data.** Every output comes from a rerunnable
   script, never from values read and retyped.
2. **Nothing is trusted until checked against something independent.**
3. **Record when each value became public**, not only the period it describes.

For health, mortality, overdose, EMS, hospital or vital-records data, also read
`references/health_and_surveillance_data.md` (HIPAA identifiers, suppression and how totals undo
it, reporting delays, case definitions, tables for anomaly detection).

## Before opening any file: privacy tier

Decide each file's tier from READMEs, agreements and directory names, not by opening it. Ask if
unsure.

- **Public**: read freely.
- **Restricted aggregate** (small-cell tables under an agreement): only through scripts that apply
  the agreement's suppression rule.
- **Record-level protected** (anything about identifiable people): never read rows. Whatever the
  agent sees goes to the model provider and the session transcript. Work through code whose
  output is already aggregate, or against a synthetic stand-in. Read
  `references/privacy_boundary.md`. If the user asks to see rows, decline, explain why, and give
  them a command to run in their own terminal (for example `head -20 <file>`) so they can look
  without it passing through the agent.

**Profiling protected files.** Decide what each column *is* before printing anything about it.
Identifiers (names, IDs, addresses, dates of birth or death, exact locations) and free text
(narratives, notes, comments) never have values printed, whatever their cardinality. A
"print the levels when there are only a few" rule leaks a free-text column that happens to hold
one repeated sentence. For those columns print only counts, null rates, lengths, format-validity
rates and keyword-flag counts. Print levels only for columns you have confirmed are coded
categories (manner, ZIP, school), and only levels with at least the suppression threshold.

## What to produce

**1. A source catalog entry for each source** (`assets/source_catalog.csv`, one row per source).
It records what the source is and how it may be used: owner, access level and agreement, sharing
limits, whether it holds personal data, update frequency, publication lag, revision behaviour,
years covered, finest geography and demographic detail, case definition, suppression rule, and
quality considerations (completeness, timeliness, validity, consistency). Fill what you can from
the source's own documentation and mark the rest unknown. A reader deciding whether a source
can answer their question needs to know who controls it, what it may be used for, and how it
describes people and places; a backtest additionally needs to know when each value became public
and whether it is later revised.

**2. A rerunnable script per source**, with download, convert and validate steps. Keep raw files
unchanged. Keep suppressed or missing cells as missing, never zero. Read the footnotes: they hold
definition changes, provisional flags and suppression rules.

**3. A provenance record next to every output** (`scripts/provenance.py`): source URL, exact
query or filters, retrieval time, publication date if known, file hash, page and table for
documents, and the producing command.

**4. Flags in the data, not just in the reply**: a `provisional` column where the source says so;
an `incomplete` flag for recent periods still filling in; the edition or pull each value came
from; and, for anything used in a forecast or backtest, the date each value (features *and*
labels) became available, so an as-of join can enforce it.

**5. A validation report** (`assets/validation_report.md`, or the same content in the reply for
small tasks), described below.

## Validation

Write the acceptance rule before running checks: which checks, and what counts as a pass. Then
run as many of these as the stakes need, and report every one as pass, fail or not run:

| Check | Establishes | Does not establish |
|---|---|---|
| Internal arithmetic (rows sum to totals, ranges, no duplicates) | Internal consistency | That values match the source, or sit under the right labels |
| Two independent extraction methods, diffed cell by cell | Reproducible extraction | That the source is right; two text parsers reading the same text layer are not independent, a rendered-page read is |
| Match to a published figure in another document | Totals and population agree with the publisher | Subgroup or small-area values |
| Correlation with an independent signal | The series moves like another measure of the same thing | Level accuracy, finer grains |
| Random hand check of n cells | An error rate | That no errors remain |

Things that go wrong often enough to check every time:

- **Multiple pulls or editions** can differ in definition, not just completeness. Reconcile each
  against an official total before combining, and never splice editions with different
  definitions into one unmarked series.
- **PDF text layers** can hold values the page does not show (corrections pasted over old
  numbers), and multi-column tables can interleave. When values matter, compare against the
  rendered page. See `references/pdf_extraction.md`.
- **Revised or smoothed series** (economic data, search indices) leak the future into backtests.
  Use the vintage available at each date. See `references/temporal_availability.md`.
- **Withheld values.** If suppressed cells can be recovered from published totals, use the
  remainder only to check the extraction. Never write recovered values or publish margins that
  allow recovery.
- **A failed request is not a dead source.** Check the publisher before dropping anything.
- **Implausible patterns** (a unit swinging wildly while its total is stable, a level shift at a
  file boundary) are pipeline or source problems until shown otherwise.

## Hand back

Say what was produced, where, and the command that rebuilds it; the acceptance rule and the check
table; what was not validated; assumptions; and any file you chose not to open because of its
tier. A clearly reported mismatch is worth more than a table that silently "looks fine".

## Bundled resources

- `references/privacy_boundary.md`: enforcing the boundary in agent settings, leak paths,
  synthetic stand-ins, local models, campus model services.
- `references/health_and_surveillance_data.md`: HIPAA, suppression, reporting delays, case
  definitions, ICD-10-CM exclusions, tables for anomaly detection.
- `references/pdf_extraction.md`, `references/temporal_availability.md`.
- `assets/source_catalog.csv` (columns and one example row), `assets/validation_report.md`.
- `scripts/provenance.py OUTPUT --source-url URL [--query Q] [--published DATE] [--page N] [--table T]`
- `scripts/synth_standin.py REAL OUT [--rows N] [--vocab COL ...]`: run by a person, not the agent,
  to make a schema-only fake of a protected file.

- `references/related_guidance.md`: the laws, standards and published guidance these practices are
  consistent with, for citing in a methods section.

The scripts record provenance and build stand-ins. They do not validate data, detect identifiers or
make anything compliant with a law or agreement.
