#!/usr/bin/env python3
"""Build a schema-only synthetic stand-in for a protected CSV or Parquet file.

A PERSON runs this on the real file, not the agent. It writes:
  OUT_FILE                  fake rows with the same columns, types and missingness
  OUT_FILE.schema.json      what was kept, for review before the agent sees anything

What is kept from the real data:
  - column names and types
  - missingness rate per column (rounded to 0.01)
  - numeric columns: the 5th-95th percentile range, rounded (extremes are not kept)
  - date columns: the range of years only
  - string columns: nothing, values are replaced by placeholders like "name_17",
    unless the column is listed with --vocab (for standard code sets such as ICD-10 or
    manner of death), in which case levels seen at least --min-count times are kept
    and rarer ones are dropped.

Review OUT_FILE.schema.json before sharing. Column names themselves can be sensitive.
Requires pandas (and pyarrow for Parquet).

Example:
    python synth_standin.py data/raw/me_deaths.csv data/synthetic/me_deaths.csv \
        --rows 2000 --vocab manner_of_death icd10_underlying
"""
import argparse
import json
import pathlib
import sys

import numpy as np
import pandas as pd


def read(path: pathlib.Path) -> pd.DataFrame:
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    return pd.read_csv(path, low_memory=False)


def write(df: pd.DataFrame, path: pathlib.Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in {".parquet", ".pq"}:
        df.to_parquet(path, index=False)
    else:
        df.to_csv(path, index=False)


def looks_like_dates(s: pd.Series) -> bool:
    sample = s.dropna().astype(str).head(200)
    if sample.empty:
        return False
    parsed = pd.to_datetime(sample, errors="coerce", format="mixed")
    return parsed.notna().mean() > 0.9


def synth_column(name, s, n, rng, vocab, min_count):
    null_rate = round(float(s.isna().mean()), 2)
    info = {"column": name, "dtype": str(s.dtype), "null_rate": null_rate}
    nonnull = s.dropna()

    if pd.api.types.is_bool_dtype(s):
        p = round(float(nonnull.mean()), 2) if len(nonnull) else 0.5
        values = pd.Series(rng.random(n) < p, dtype="boolean")
        info.update(kind="bool", p_true=p)
    elif pd.api.types.is_numeric_dtype(s):
        if len(nonnull):
            lo, hi = np.nanpercentile(nonnull.astype(float), [5, 95])
        else:
            lo, hi = 0.0, 1.0
        is_int = pd.api.types.is_integer_dtype(s) or bool((nonnull % 1 == 0).all())
        if is_int:
            lo, hi = int(np.floor(lo)), int(np.ceil(hi))
            values = pd.Series(rng.integers(lo, hi + 1, n), dtype="Int64")
        else:
            lo, hi = float(f"{lo:.2g}"), float(f"{hi:.2g}")
            values = pd.Series(rng.uniform(lo, hi, n))
        info.update(kind="int" if is_int else "float", p5_p95=[lo, hi])
    elif pd.api.types.is_datetime64_any_dtype(s) or (name not in vocab and looks_like_dates(s)):
        dates = pd.to_datetime(nonnull, errors="coerce", format="mixed").dropna()
        y0, y1 = (int(dates.dt.year.min()), int(dates.dt.year.max())) if len(dates) else (2000, 2000)
        start = pd.Timestamp(f"{y0}-01-01").value // 10**9
        end = pd.Timestamp(f"{y1}-12-31").value // 10**9
        values = pd.Series(pd.to_datetime(rng.integers(start, end + 1, n), unit="s").strftime("%Y-%m-%d"))
        info.update(kind="date", years=[y0, y1])
    elif name in vocab:
        counts = nonnull.astype(str).value_counts()
        kept = counts[counts >= min_count]
        if kept.empty:
            values = pd.Series([f"{name}_{i}" for i in rng.integers(1, 50, n)])
            info.update(kind="vocab", kept_levels=0, note=f"no level reached min_count={min_count}")
        else:
            probs = (kept / kept.sum()).to_numpy()
            values = pd.Series(rng.choice(kept.index.to_numpy(), n, p=probs))
            info.update(kind="vocab", kept_levels=len(kept), dropped_levels=int(len(counts) - len(kept)))
    else:
        n_levels = int(nonnull.nunique())
        pool = max(1, min(n_levels, 1000))
        values = pd.Series([f"{name}_{i}" for i in rng.integers(1, pool + 1, n)])
        info.update(kind="placeholder_text", approx_levels=pool if n_levels <= 1000 else ">1000")

    mask = rng.random(n) < null_rate
    values = values.astype(object)
    values[mask] = None
    return values, info


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("real_file", type=pathlib.Path)
    p.add_argument("out_file", type=pathlib.Path)
    p.add_argument("--rows", type=int, default=1000)
    p.add_argument("--vocab", nargs="*", default=[], help="Columns holding standard code sets to keep")
    p.add_argument("--min-count", type=int, default=11, help="Minimum count for a vocab level to be kept")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    real = read(args.real_file)
    missing = [c for c in args.vocab if c not in real.columns]
    if missing:
        print(f"--vocab columns not found: {missing}", file=sys.stderr)
        return 1

    rng = np.random.default_rng(args.seed)
    cols, report = {}, []
    for name in real.columns:
        cols[name], info = synth_column(name, real[name], args.rows, rng, set(args.vocab), args.min_count)
        report.append(info)

    write(pd.DataFrame(cols), args.out_file)
    schema_path = args.out_file.with_name(args.out_file.name + ".schema.json")
    schema_path.write_text(json.dumps(
        {"source_rows": int(len(real)), "synthetic_rows": args.rows, "seed": args.seed,
         "min_count": args.min_count, "columns": report}, indent=2) + "\n")

    # Only counts go to the screen, never values.
    print(f"wrote {args.out_file} ({args.rows} rows, {len(real.columns)} columns)")
    print(f"wrote {schema_path}; review it before giving either file to an agent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
