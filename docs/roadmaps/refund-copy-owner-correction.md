# Refund-copy constraint and regression guard

The correction was integrated through [PR #58](https://github.com/viktorermolov/ermolov.dev/pull/58) and included in the merged [site release #59](https://github.com/viktorermolov/ermolov.dev/pull/59).

## Required public copy

Omit assurances that a refund leaves already activated Pro running. Do not add an equivalent hint, technical qualification or immediate-deactivation claim. This copy decision does not change product behavior or refund terms.

Preserve the accepted 1.1.4 retention paragraph, privacy inventory, approved images, prices, 30-day request window, original-payment-method refunds, bundle/upgrade rules and legitimate activation through another valid payment. The original base purchase being unaffected by refunding only an upgrade remains distinct from the prohibited assurance.

## Why the guard exists

[PR #31](https://github.com/viktorermolov/ermolov.dev/pull/31) removed the assurance from both refund pages and also removed separate retroactive-target-purchase assurances. Commit [db476714](https://github.com/viktorermolov/ermolov.dev/commit/db476714c089ba44d21857a2adec872fd90bb839) reintroduced it during PR #46's retention reconciliation; neither parent contained it. It was corrected before that preparation release reached production.

Implementation facts and retention decisions do not authorize restoring copy the owner removed. The full trace and exact source diff remain in PR #58 rather than being repeated here.

## Regression protection and limits

The existing `scripts/check_site.py` guard scans every generated HTML file, including 404, page text, structured data and metadata/alt/title/ARIA text. It normalizes entities, case, whitespace and typographic apostrophes, rejecting the original negative-deactivation assurance and common continued-activation forms in sentences about Pro and a refund. It is a focused wording guard, not complete semantic equivalence detection; audit the public source and rendered output as well.

The original baseline passed the older site checker despite the prohibited sentence. The strengthened full checker rejected that unchanged artifact specifically at `clipstay/refunds/index.html`; the corrected build passed. Temporary mutation checks rejected six exact/paraphrased/HTML/metadata/alt variants and accepted four existing activation/free-plan statements. Those temporary fixtures are not public copy.

No existing check was weakened, skipped or renamed. The correction changed only the sentence and blank line in public copy; other pre-commit rendered pages were byte-identical. Keep the full pinned-Hugo build, site checker and JavaScript syntax checks for subsequent work. These checks do not establish native OS, payment, Store or fresh production acceptance.
