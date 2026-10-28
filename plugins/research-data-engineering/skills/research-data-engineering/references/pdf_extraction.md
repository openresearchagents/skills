# Extracting data from PDFs, tables and figures

Much public data still lives in PDF annual reports, slide decks, and dashboards that only show
charts. The goal is a table that can be regenerated and checked, not a one-time transcription.

## Choosing a method

| Source | First method | Independent second method |
|---|---|---|
| Born-digital PDF table | pdfplumber or Camelot (lattice mode for ruled tables, stream mode otherwise) | PyMuPDF text with coordinates, or a vision model reading the page image |
| Complex layouts, multi-page tables | Docling or similar layout-aware converters | Vision model, or manual extraction of a sample |
| Scanned PDF | OCR (Tesseract via OCRmyPDF), then table parsing | Vision model on the page image |
| Chart or figure | Vision model asked for values with uncertainty, or WebPlotDigitizer | The other of the two; check against labelled points |
| Web dashboard | Look for the underlying API or download link first (browser network tab, "export" buttons, open-data portal) | Screenshot plus vision model, for spot checks only |

A dashboard's own data endpoint is almost always better than reading its charts. Look for it first.

## Workflow

1. Save the original file unchanged and write its provenance record (URL, retrieval time, hash).
2. Locate the table: page number, table title, and the notes beneath it. Save the notes. They
   define suppression symbols, provisional data and case definitions.
3. Extract with the first method into a tidy table (one row per unit and period, one column per
   measure). Keep a column linking each value to its page and table.
4. Normalize: suppression symbols to missing, thousands separators and footnote markers removed,
   units recorded.
5. Extract again with an independent method. Diff cell by cell and resolve every disagreement by
   looking at the page.
6. Run the arithmetic checks: totals, subgroup sums, ranges.
7. Reconcile at least one total against a different published source if one exists.
8. Hand-check a random sample of cells and report the error rate.

## Common failure modes

- Column shifts when a cell is empty or merged, which move every value one column over. Total
  checks catch most of these.
- Interleaved columns. Plain text extraction of tables with several value columns can alternate
  fragments of neighbouring cells, so a value survives but its column is ambiguous. When a value
  matters and the document does not restate it elsewhere, render that page as an image and read
  it directly before trusting the assignment.
- Row labels misassigned while column totals still add up. Totals cannot detect a swapped or
  shifted row. Only a second method, a hand check, or an outside source for the row values can.
- Footnote markers glued to numbers ("123a" read as 1231).
- Rows split across pages with the header repeated mid-table.
- Rates read as counts, or per-100,000 read as per-1,000.
- Suppressed cells ("*", "--", "<11") silently turned into zero.
- Revised figures: a later report may restate earlier years. Record which edition each value came
  from and do not mix editions without saying so.

## Figures

Values read from a chart are estimates. Ask for them with uncertainty, check against any labelled
data points and axis ticks, record the tolerance, and keep them in a separate column or flag from
values read from tables. Never sum digitized values and present the total as exact.
