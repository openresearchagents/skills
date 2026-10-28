# Publication dates, vintages and as-of joins

Any analysis that asks "what could we have known at time T" (forecasting, nowcasting, early
warning, backtesting) needs each value's publication date, not just its reference period. Without
it, results look better than they would have in real time, and nobody notices because the
leak is in the data, not the model.

## Record for every source

- Reference period: the period the value describes.
- Publication or availability date: when the value first became public. Use the release calendar,
  the report date, archive snapshots, or the API's own revision history.
- Vintage: which release the stored value comes from, when a series is revised.
- Completeness lag: how long until records for a period are substantially complete (deaths with
  pending toxicology, for example). Measure it by comparing successive pulls if you can.

## Rule for joins

A feature value may be joined to analysis time T only if its publication date is on or before T.
Implement this as an explicit as-of join on publication date, not as a fixed lag guessed once.
Write the rule down before running the analysis, and apply the same rule to the outcome labels used
for training (labels for periods after T, or not yet complete at T, must not be used).

## Traps seen in practice

- **Annual counts released late.** A January count published in May cannot inform February.
- **Smoothed or adjusted series.** Smoothing and seasonal adjustment use later months, and are
  revised. Use the raw series or archived vintages.
- **Rescaled indices.** Search-interest data scaled to the maximum of the requested window change
  every time a new peak arrives. Pull real-time vintages ending at each analysis date, or use a
  scale that does not depend on the window.
- **Static snapshots.** Today's map, facility list or boundary file attached to past periods. Use
  archived snapshots (the Internet Archive's Wayback Machine, dated releases) or flag the feature
  as a forward leak and measure how much it matters.
- **Cohort drift between pulls.** Data pulled at different times, or under different request
  wording, may use different case definitions. Mixing them can create false trends. Reconcile each
  pull's annual totals against an official published count before combining.
- **Late-arriving records.** The most recent periods are undercounted until records are complete.
  Either wait out the completeness lag or model it, and never read the shortfall as a decline.

## How to tell if it matters

Run the analysis twice: once with the stored (possibly leaky) values and once with real-time
vintages or the as-of rule enforced. If results barely change, report that and keep the simpler
pipeline. If they change, the as-of version is the honest one.
