# Related law, standards and guidance

The practices in this skill follow from the reasoning given where each appears. They are also
consistent with the law, standards and published guidance below, which are useful to cite in a
methods section or a data management plan. None of them is required reading for the agent. This is
not legal advice; agreements and institutional policy govern.

## Law

| Practice in the skill | Consistent with |
|---|---|
| Treat ZIP codes, dates and free text about people as identifying | HIPAA Privacy Rule de-identification standard, 45 CFR 164.514(b) (Safe Harbor identifiers); HHS, *Guidance Regarding Methods for De-identification of PHI* (2012) |
| Death records are still protected | HIPAA protects a decedent's health information for 50 years after death (definition of PHI, 45 CFR 160.103; 45 CFR 164.502(f)) |
| Model providers are third parties | HIPAA business associate requirements, 45 CFR 164.502(e); FERPA disclosure limits, 20 U.S.C. 1232g and 34 CFR Part 99 |
| Substance use treatment records need extra care | 42 CFR Part 2 |
| Census and tax microdata are restricted | 13 U.S.C. 9; 26 U.S.C. 6103 |
| State law may add to federal rules | For example, California's Confidentiality of Medical Information Act (Civil Code 56) |

## Standards and methods literature

| Practice | Consistent with |
|---|---|
| Suppress small cells and check for complementary disclosure | Hundepool et al., *Statistical Disclosure Control* (Wiley, 2012); NIST SP 800-188, *De-Identifying Government Datasets* (2023); CMS cell-size suppression policy (counts 1 to 10) |
| Exclude adverse-effect and underdosing codes; count initial encounters | ICD-10-CM Official Guidelines for Coding and Reporting, chapter 19 (poisoning, adverse effect, underdosing) |
| Record publication dates and use the vintage available at each date | Croushore and Stark, "A real-time data set for macroeconomists", *Journal of Econometrics* (2001), and the real-time data literature that followed |
| Document sources, code lists, linkage and validation | RECORD statement, Benchimol et al., *PLoS Medicine* (2015) |
| Provenance, persistent identifiers, reusable metadata | FAIR principles, Wilkinson et al., *Scientific Data* (2016) |
| Synthetic stand-ins; risks of fitted generators | Nowok, Raab and Dibben, "synthpop", *Journal of Statistical Software* (2016); the differential privacy literature |

## Public-health practice

| Practice | Consistent with |
|---|---|
| A source inventory with owner, access, sharing limits, granularity and quality notes | Data-source inventories recommended to health departments for overdose surveillance, for example the Council of State and Territorial Epidemiologists (CSTE) Overdose Anomaly Toolkit's data catalog |
| Never put real records into an AI tool; share code only | The same toolkit's technical guidance for its anomaly-detection code, which allows AI-assisted code translation only "without entering any real data into the artificial intelligence interface" |
| Use published, versioned overdose definitions | National nonfatal overdose definitions for discharge, syndromic and EMS data (CDC's DOSE program; CSTE's standardized nonfatal opioid overdose case definition, built on NEMSIS EMS data elements) |
| Keep known surges out of baselines for expected counts | Standard practice in aberration detection, and stated explicitly in the toolkit's anomaly-detection guidance |
