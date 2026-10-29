# Computational reader entry

Read README.md, claims.json and VERIFICATION-RECORD.md before running commands. The theorem is for each fixed known integer n>=1 and known N0, generic real true points against every real competitor, observed through the analytic incidence germ. Positivity or genericity is not imposed on competitors.

The proof is in paper.tex/paper.pdf and is not mechanically certified. Do not extend it to all true points, unknown stage number or population, finite/noisy data, stable estimation, or disease-model adequacy. Do not describe the two-stage audit as an independently completed all-n proof in its first stage, human peer review, or formal proof certification.

Run `python3 -B check_packet.py` and `python3 -B reproduce.py`. Python 3.10+ standard library is sufficient for finite controls; Poppler is required for PDF/privacy checks. Generated results stay under ignored results/. No network, source-author code, parent repository or Git history is needed. Finite controls n=1..6 do not prove the theorem for all n.

The code is the producer-side finite-control implementation. The historical audit reader’s result snapshot is evidence of a separate run, not a second implementation invoked by reproduce.py. Keep review stages, public summaries, source hashes and scientific file contents distinct.
