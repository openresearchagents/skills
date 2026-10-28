# Health and surveillance data

Read this alongside `SKILL.md` when the data concern health, mortality, disease, overdose, EMS,
hospitals or vital records, or come from a health department. Most of what follows is about three
things that tend to occur together in public-health projects: public aggregate reports with
suppression rules, restricted record-level data in the same repository, and counts that keep
changing after the fact.

This is practical guidance, not legal advice. Data use agreements, IRB protocols and institutional
policy decide what is allowed.

## Contents
1. Regulation and identifiers
2. Small-cell suppression and complementary disclosure
3. Reporting delays and provisional data
4. Case definitions and cohorts
5. Independent signals for validation
6. Reporting standards
7. Tables for anomaly detection and source inventories

## 1. Regulation and identifiers

- **HIPAA** applies to covered entities (most providers, health plans, clearinghouses) and their
  business associates. Sending protected health information to a vendor without a Business
  Associate Agreement is generally an impermissible disclosure, and an agent's model provider is a
  vendor. Whether HIPAA applies depends on who holds the data: a medical examiner's office or a
  police department is often not a covered entity, while a hospital is. The DUA often matters more
  than the statute.
- **Decedents** are protected under HIPAA for 50 years after death, so death records are not exempt
  because the person has died.
- **State law** can add more (California's Confidentiality of Medical Information Act, for
  example), as can 42 CFR Part 2 for substance use disorder treatment records, which is stricter
  than HIPAA.
- **Safe Harbor identifiers** include geographic units smaller than a state (a three-digit ZIP
  prefix is allowed only if its area has more than 20,000 people), all elements of dates except the
  year (including dates of death and admission), and ages over 89. A file of overdose deaths with
  five-digit ZIP and date of death is identifiable even with names removed.
- Free-text fields (narratives, cause-of-death text, chief complaints, addresses) can contain names
  and other identifiers anywhere. Treat them as identifying unless processed by a validated
  de-identification step.

## 2. Small-cell suppression and complementary disclosure

Publishers suppress small counts because they can identify people, especially when crossed with
age, sex, race and place. Common thresholds: counts from 1 to 9 or 1 to 10, or fewer than 11
(CMS). Use the threshold in the DUA or the publisher's notes.

**Primary suppression** blanks the small cells. **Complementary disclosure** happens when other
published numbers let someone recover them: a row total minus the other cells in the row, two
tables that share a margin, or a year total next to a quarterly breakdown. Rules for the agent:

- When extracting a suppressed public table, you may compute the remainder (total minus visible
  cells) to check the extraction. It should fall inside the suppressed range. Report that the check
  passed, not the recovered values.
- Do not write recovered values into any output, and do not use them as data.
- When producing aggregates from restricted data, apply primary suppression, then check whether
  any published or co-released margin (row, column or period totals, other tables from the same
  data) lets a suppressed cell be recovered. If so, suppress additional cells or drop the margin,
  and say which you did.
- Zeros are usually publishable, but they reveal that a cell is not zero elsewhere. Follow the DUA.
- If small cells make a table useless at the requested grain (every non-zero cell suppressed),
  say so and offer coarser grains (longer periods, larger areas) with the share of cells each
  would publish.

## 3. Reporting delays and provisional data

- **Completeness lag.** Death records, especially those waiting on toxicology, keep arriving for
  months. The most recent periods are undercounted in any pull. Measure the lag by comparing
  successive pulls if you have them; otherwise state an assumption and flag recent periods. Never
  read the shortfall as a decline.
- **Provisional versus final.** Reports mark recent years as provisional. Keep a flag column and
  record which edition each value came from. Later editions restate earlier years; do not mix
  editions silently.
- **Nowcasting and backtests.** Labels as well as features must respect the as-of date: at a
  forecast origin, only periods whose counts were known (and complete enough) by then may be used
  for training. See `temporal_availability.md`.

## 4. Case definitions and cohorts

- Overdose deaths can be defined by underlying cause (ICD-10 X40-X44, X60-X64, X85, Y10-Y14),
  by drugs mentioned anywhere on the record (T-codes as multiple causes), or by a medical examiner's
  own coding. Counts differ substantially between these. Record which one each source uses.
- Records requests worded differently, or fulfilled at different times, can return different
  cohorts (for example, deaths with a drug listed as a contributing condition). Reconcile every
  pull against the publisher's annual totals before combining.
- Check manner of death (accident, suicide, homicide, undetermined, natural) and whether the
  definition includes or excludes each.
- Geography: residence versus place of death versus place of injury give different maps. ZIP
  codes are postal routes, not areas; non-areal ZIPs (PO boxes, single buildings) need a crosswalk
  to ZCTAs or another areal unit. Record which is used.

**Nonfatal overdose definitions.** A count is only comparable across places and years if the
definition is fixed and written down. Prefer a published, versioned definition used by the health
department or a national surveillance program over one written for the project, record its name
and version in the catalog, and note any local changes. Whatever the source:

- **Diagnosis codes (ICD-10-CM).** Drug poisoning codes (T36-T50) encode intent in the 5th or 6th
  character: 1 accidental, 2 intentional self-harm, 3 assault, 4 undetermined, 5 adverse effect of
  a correctly taken drug, 6 underdosing. Adverse effects and underdosing are not overdoses, so a
  pattern match such as `T40*` over-counts unless they are excluded explicitly (for example
  T40.4X5A). The 7th character (A, D, S) separates initial encounters from follow-ups and
  sequelae; counting D and S codes counts the same overdose more than once.
- **Free-text (syndromic) definitions** built from chief complaints and discharge text catch
  visits that are never coded, so they will not match code-based counts. Report which kind a
  series uses.
- **EMS.** Naloxone administration alone over-counts (it is also given to unresponsive patients
  who did not overdose); naloxone with documented improvement, overdose keywords in the narrative,
  or an overdose primary impression are more specific. State which elements the definition uses.
- Most emergency department overdose visits are not confirmed by toxicology. Label such series
  "suspected".

## 5. Independent signals for validation

Useful cross-checks for overdose and mortality series, each measuring the same phenomenon a
different way: EMS overdose calls or naloxone administrations, police calls coded as overdose,
emergency department visits (syndromic surveillance), poison center calls, and the state or
national vital statistics release for the same area. Agreement in trend at the same grain is
evidence; disagreement in level is expected and is not by itself an error.

## 6. Reporting standards

When a dataset will be used in a paper, the RECORD statement (REporting of studies Conducted using
Observational Routinely-collected health Data) lists what readers will expect to be documented:
data sources, linkage, code lists, validation of definitions and data cleaning. The provenance
records and validation report from this skill cover most of it.

## 7. Tables for anomaly detection and source inventories

- **Anomaly-ready counts.** Spike and anomaly detection compares each observed count with an
  expected one, so the input must be a complete grid: one row per period and stratum (place, and
  optionally age group, sex, race and ethnicity) with its count, and explicit zero rows. A missing
  row is read as "no data" by some methods and as zero by others, and either reading can be wrong.
  Keep the definition (overdose flag and cause code) and both geographies (residence and
  facility or event) as columns, since the choice changes the map. Apply suppression only to
  tables that leave the secure environment; suppressed analysis inputs make expected counts
  impossible to estimate.
- **Baselines.** If a table will be used to estimate "expected" counts, record known surge
  periods (a new substance's arrival, a fentanyl wave) in the catalog notes. Including them in a
  baseline makes similar future surges look normal.
- **Source inventory.** Keep one row per source in `assets/source_catalog.csv`. Its first 21
  columns match the fields health-department data inventories commonly use (see
  `related_guidance.md`), so an existing inventory can be pasted in and extended with the timing
  columns.
