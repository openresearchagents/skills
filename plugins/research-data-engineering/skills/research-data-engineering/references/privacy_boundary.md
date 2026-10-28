# Keeping protected data out of the agent's context

## Contents
1. Why this matters
2. The boundary: code-only access
3. Leak paths
4. Enforcing it in configuration
5. Synthetic stand-ins
6. Local open-weight models for record-level text
7. Campus-hosted model services

This is practical guidance, not legal advice. Data use agreements, IRB protocols and institutional
policy decide what is allowed. When they are stricter than anything here, they win. For health
data, also read `health_and_surveillance_data.md` (HIPAA identifiers, suppression thresholds).

## 1. Why this matters

Anything the agent reads (a file, a command's output, an error message that echoes a row) goes to
the model provider and is stored in the local transcript. Most data use agreements forbid sharing
record-level data with third parties, and a model provider is a third party unless an agreement
with it says otherwise. Sector laws add their own rules: HIPAA for health data, FERPA for
education records, Title 13 and Title 26 for census and tax microdata, and state privacy laws.

Published public-health guidance on using AI tools with surveillance code takes the same line:
share code, never real data (see `related_guidance.md`).

This includes de-identification itself. Asking a cloud-hosted agent to read records and strip
identifiers sends the identifiers to the provider in the process. De-identification of free text
belongs on a local model or a rule-based tool (section 6), not in the agent's own context.

## 2. The boundary: code-only access

The agent never reads protected rows. It writes code, the code runs on the data, and only checked
aggregates come back. In practice:

- Develop and debug against a synthetic stand-in with the same schema (section 5).
- Scripts that touch protected data print only counts, shapes, column names and suppressed
  aggregates. Avoid `head()`, `sample()`, `describe()` or `value_counts()` on identifying or
  free-text columns.
- Classify every column by role before profiling: identifier, free text, date, coded category or
  measure. Never print values of identifier or free-text columns, whatever their cardinality (a
  narrative column holding one repeated sentence has one distinct value, and a "print levels when
  few" rule will print it). For those, print derived facts only: distinct count, null rate,
  length range, format-validity rate, keyword-flag counts. Print levels only for confirmed coded
  categories, and only levels at or above the suppression threshold.
- When code must run on the real file, prefer that a person runs it and pastes back only the
  aggregate output. If the agent runs it, the output must already be aggregate and suppressed.
- Outputs written to disk from protected inputs carry the same restrictions as the inputs unless
  they are aggregate and suppressed.
- If the agent does see protected content by accident, stop and tell the user. They may have a
  reporting duty, and the transcript may need to be deleted.

## 3. Leak paths

Values escape through more routes than `print`. Check each one in any script that reads protected
data:

- **Error messages and tracebacks.** Parsing errors, assertion messages and pandas warnings often
  include the offending value or row. Catch exceptions and report the type and row index or a
  hashed key, not the content.
- **Logs.** Logging a record "for debugging" writes it to disk and, if the agent reads the log, to
  the provider.
- **Notebook outputs.** Cell outputs are saved in the `.ipynb` file. An agent that reads the
  notebook reads the outputs.
- **Caches and temporary files.** Intermediate Parquet files, joblib caches and temp directories
  hold copies of the data outside the protected folder. Keep them inside it, or avoid them.
- **File names and paths** built from record values (one file per person or per case number).
- **Version control.** Outputs committed to git before suppression stay in its history.

## 4. Enforcing it in configuration

Instructions in a prompt are not enough, because the agent decides what to read on the fly. Use
the harness's own controls.

- **Deny rules.** In Claude Code, add deny rules for protected paths to the project's
  `.claude/settings.json`, for example:

  ```json
  {
    "permissions": {
      "deny": [
        "Read(./data/raw/protected/**)",
        "Read(./data/requests/**)"
      ]
    }
  }
  ```

  File-read rules cover the built-in file tools, not every shell command. A broad shell
  permission such as allowing any `python` command can still read the file. Narrow broad shell
  allow rules, and use the harness's OS-level sandbox with filesystem restrictions where available
  (check the current documentation for your tool: Claude Code, Codex and others each have their own
  sandbox settings).
- **Keep protected data out of the working tree** where possible, for example on a separate mount
  the agent's process cannot read.
- **Treat transcripts as sensitive.** Agent session logs (for Claude Code, under
  `~/.claude/projects/`) keep whatever the agent saw. Store and delete them under the same rules as
  the data.
- `.gitignore` keeps files out of version control. It does nothing to stop an agent reading them.

## 5. Synthetic stand-ins

A stand-in is a fake file with the real file's schema, so code written against it runs unchanged on
the real data.

- **Schema-only stand-in (default).** Same columns, types, missingness rates and plausible value
  ranges, filled with generated values. Categorical code sets that are standard vocabularies
  (diagnosis codes, manner of death, school grade levels) can be kept, because they are not data.
  `scripts/synth_standin.py` builds this. A person runs it on the real file, checks the schema
  report, and gives the agent only the outputs.
- **Fitted generators** (synthpop in R, SDV in Python) reproduce joint distributions, which helps
  when code depends on realistic relationships. They can also memorize and reproduce rare real
  records. If a fitted file will be shown to an agent or shared, use a differentially private
  generator and have someone review it.
- Stand-ins are for building and testing code. Never report estimates from them.

## 6. Local open-weight models for record-level text

Some steps need a model to read individual records: coding free-text causes or narratives into
categories, normalizing addresses before geocoding, finding identifiers that regular expressions
miss. Run these on a model that sends nothing off premises.

Memory rule of thumb: parameters times bytes per weight, plus the context cache. At 4-bit an 8B
model is about 5 GB and a 70B model about 40 GB.

| Hardware | Practical models | Good for |
|---|---|---|
| CPU only | 1B to 8B, 4-bit, via llama.cpp or Ollama | Overnight batch classification and extraction, one record per call |
| Consumer GPU up to about 6 GB | 7B to 8B at 4-bit, short context | Single-record extraction and classification; not long agent loops |
| Lab GPU, 40 GB or more | 30B at 8-bit, 70B at 4-bit, served with vLLM or SGLang | High-throughput batch jobs; a shared OpenAI-compatible endpoint for the lab |

Practices:

- Run rule-based tools first (Presidio, spaCy, regular expressions) and send only the unresolved
  cases to the model.
- Use constrained output (JSON schema or grammar) so small models cannot return malformed records.
- Treat the model as a measurement instrument. Validate on a few hundred hand-labelled records and
  report precision and recall per category before using the output. For de-identification, test
  on synthetic records with planted identifiers and report how many survive.
- Pin model, quantization, runtime version, prompt, temperature (0) and seed, and record them with
  the output. Validate again after any change; a new quantization can shift rates enough to look
  like a trend.
- Bind the server to localhost or the lab network, disable telemetry, and protect its logs like
  the data.

## 7. Campus-hosted model services

Several universities and research platforms run shared OpenAI-compatible endpoints for open-weight
models. They avoid third-party disclosure only if they are approved for the data. Some are
explicitly not approved for regulated data. Before sending protected data, confirm:

1. Which data classification level the service is approved for (institutions name these differently), and whether that covers HIPAA or FERPA data.
2. Whether prompts and outputs are logged, for how long, and who can read the logs.
3. Whether model versions are pinned and changes announced.
4. Whether the service's terms satisfy your DUA.

If no approved service exists, say so to research computing and the privacy office, with a list of
projects that need one. One governed campus service is safer and cheaper than many lab-run servers.
