# Global identifiability for the staged-infection SIR model

For every **known integer number of infection stages n ≥ 1**, exact incidence near one time determines both rates and all initial states of the staged-infection SIR model, for a generic true real point compared with **every real competitor**, when total population is known.

This article proves the statement posed as Conjecture 1 of Pant, Saucedo, and Pogudin, [medRxiv version 2](https://doi.org/10.64898/2026.01.16.26344284). It keeps the original model and observation: all infectious stages contribute to transmission, the stage-progression rate is common, and incidence is y = βS(I₁ + … + Iₙ). No extra observation of S or an infectious compartment is supplied.

Read [the article](paper.pdf), [its TeX source](paper.tex), and [the structured claims](claims.json). This is version 1.0.0 of the article and supporting finite-check code.

## Scope and evidence

The all-n result rests on a prose proof. A two-stage AI mathematical audit supported it, and a separate editorial reader requested two minor clarifications, which were addressed. The first audit stage did **not** independently complete all bridges in the general proof; the second stage examined the producer's proof and code. The audit did not execute or import the producer's programs. See [the verification record](VERIFICATION-RECORD.md) and [the correction table](changes.md).

There is no human peer review or proof-assistant certification. A generic true point may exclude exceptional cases; the competitor is not required to be positive or generic. The claim does not cover unknown n, unknown total population, finitely sampled observations, measurement noise, stable estimation, or the adequacy of the model for a disease. A bounded literature review found no prior all-n resolution in the checked sources; it does not establish worldwide priority.

The bundled executable controls cover **n = 1 through 6**. They check polynomial coefficients, finite Wronskian witnesses, inverse formulas, state recovery, and finite algebraic identities. They are not an all-n proof checker.

## Reproduce the finite controls

Python 3.10 or later on macOS or Linux is sufficient; only its standard library is needed. Poppler (`pdftotext` and `pdfinfo`) is additionally required for the publication-file and privacy checks.

```sh
python3 -B check_packet.py
python3 -B reproduce.py
```

Run without `-O`, since the mathematical checks use assertions. The runner verifies `MANIFEST.sha256`, copies the three programs and nine JSON baselines into an isolated temporary directory, and compares every baseline. It ignores only elapsed time and peak-memory measurements. The result is written to ignored `results/reproduction.json`. Checks need no network, parent repository, Git history, source-author software, or third-party Python package.

- `checks/diagnose.py` constructs the polynomial relation and coefficient inverse with exact integer/rational arithmetic.
- `checks/check_jets.py` separately computes ODE Taylor coefficients over a finite field, Wronskian witnesses, relation residuals, and state recovery. It reuses the first program's monomial list, so it is not independent of that list.
- `checks/check_algebra.py` checks finite characteristic-polynomial, formal-center, Puiseux-coefficient, and translation identities.

The programs and baselines are unchanged from the manuscript packet. Their legacy `UNPROVED` labels describe the limits of those finite programs. The all-n theorem is the prose argument in the article. The legacy `PROOF.md` reference in algebra output refers to that argument, now in `paper.tex`.

These producer-side programs differ from the audit reader's separate implementation. [Its finite-result snapshot](review/finite-results.json) documents that historical independent run; the commands above do not rerun that implementation. [Provenance](PROVENANCE.json) distinguishes unchanged scientific files from public summaries of review records.

### Optional network-denial control on macOS

```sh
/usr/bin/sandbox-exec -f network-deny.sb python3 -B check_offline.py
```

This requires a loopback socket operation to fail with EPERM or EACCES before running the controls. It isolates the checker and descendants, not other applications. Ordinary reproduction works without this macOS facility but does not itself prove enforced network denial.

### Optional PDF rebuild

The included PDF and TeX are unchanged from the reviewed manuscript. A rebuild requires Tectonic and its existing resource cache:

```sh
mkdir -p build
tectonic --only-cached --untrusted --keep-logs --outdir build paper.tex
```

The finite controls do not require TeX. The checked-in CI performs the same file/privacy and finite-control commands; it does not constitute human review or an all-n formal proof.

## Attribution and thanks

Pant, Saucedo, and Pogudin formulated the model and the conjecture addressed here. Bostan and Dumas provide the cited background on Wronskians and linear independence. I am grateful for these published contributions, and I hope this work adds something to the field they developed. This acknowledgment implies no review, endorsement, or personal assistance by those authors.

## Citation and licensing

[CITATION.cff](CITATION.cff) records the author and version. Text and data are CC BY 4.0; code is Apache 2.0. See [LICENSE](LICENSE). No cited third-party paper or original author code is redistributed.
