# Owner-directed refund-copy correction

Prepared 2026-11-04 UTC from site release `071bd55c880268ee93d4e503dcb15bc838713307`, tree `06c129c7063143bc10f0903626993e32e23c2195`. This is a separate draft PR targeting `release/site-bugfix-preparation-2026-11`, not master or production.

## Binding decision and scope

The owner explicitly requires the site to omit assurances that a refund leaves already activated Pro running. Remove the reintroduced sentence without a replacement, equivalent hint or technical qualification about retaining Pro. Do not assert immediate deactivation instead. PR31 already implemented this decision; product source or later retention decisions do not authorize reversing it. No runtime behavior, refund terms or policy decision is changed here.

Only the two-line sentence/blank-line deletion changes public copy. Keep the accepted 1.1.4 retention paragraph verbatim, every privacy correction, all approved images, prices, the 30-day request window, original-payment-method refunds, bundle/upgrade rules and legitimate activation through another valid payment. The source/rendered audit found no other equivalent assurance. The existing statements about another valid payment and the original base purchase being unaffected by refunding only an upgrade were preserved in PR31 and remain unchanged.

## Exact introduction trace

- PR31 head `5cea6b23507894ed2ab72c7b995d850087ff9f6f`, integrated as `13542a6e03903919eb30bd94bb6e4861f380f859`, removed the specified assurance from both refund pages and removed separate retroactive-target-purchase assurances. Its PR body explicitly requires no instant-deactivation claim and no Worker behavior change.
- The regression was introduced in PR46 preparation commit `db476714c089ba44d21857a2adec872fd90bb839` (`docs: reconcile accepted retention and local metadata with current legal pages`). `git blame` attributes release `content/clipstay-refunds.md:20` to that commit. Its combined diff adds the forbidden sentence; **both parents**, `be0726f129f95d0cada48f07ed32d3418c6f5bc5` and `efdbdf76aa3d1aafa8ebdfb9248de3dac765cd31`, lack it. It was new text during reconciliation, not a conflict inherited from either parent.
- Legal PR46 integration `2a14e40816abcfa2f409e257b3f20fd00650b733` carried that text into the preparation release. Current master `fba7e7b3b8f1468a52b972ce09211715ea6fd926` does not contain it. No production deployment introduced this regression.
- The error was treating an implementation/retention fact as permission to restore public copy despite the owner's prior explicit removal. The earlier roadmap instructions about publishing that fact are corrected here to preserve the binding copy decision.

## Validation and regression guard

- Before adding any guard, the unchanged release passed pinned Hugo 0.166.0 production build, the existing full site checker (8 pages/2 products/nested 404), JS syntax and whitespace. The baseline still contained the prohibited sentence, exposing the missing check.
- Strengthen the existing checker with an assertion over every generated HTML file, including 404, page text, structured-data text and metadata/alt/title/ARIA text. Normalize HTML entities, case, whitespace and typographic apostrophes; reject the original negative-deactivation assurance and common continued-activation forms in sentences referring to Pro and a refund. This is a focused wording guard, not complete natural-language equivalence detection; the whole public-source/rendered audit remains necessary. No check or workflow is weakened, skipped or renamed.
- Run the strengthened full checker against the **original untouched baseline artifact**: it fails specifically at `clipstay/refunds/index.html` with the prohibited-assurance diagnostic. Run it against the corrected build: all existing checks plus the new guard pass.
- Additional temporary mutation checks reject six examples covering the exact sentence, capitalization/entities/inline markup, metadata, continued-activation phrasing and alt text; four existing activation/free-plan statements pass. These fixtures are not published or committed as site copy.
- Before the correction commit, generated artifacts differ from baseline only at `clipstay/refunds/index.html`; all other rendered pages, privacy, structured data and images are byte-identical. Final commit rebuild and exact-head Actions remain required. No native OS, Store or production acceptance is claimed.

## Remaining steps and gates

Record exact head and current Actions in the draft PR, obtain independent review of the public deletion, unchanged accepted facts, trace and strengthened guard, then integrate only after current checks under standing release authority. Do not merge before that review. No master merge, deployment or publication is authorized; the owner intends an additional audit before finishing. Leave Issues open until actual delivery. No runtime, payment/security/settings or macOS Actions change is included.
