# Audit: 21 September 2026

Reviewed all active templates, CSS, JavaScript, metadata and deployment instructions; inspected the published site at desktop, 720 px and 375 px. Hugo 0.166.0 built successfully. Git was clean before implementation. Cloudflare DNS points to DigitalOcean; no Worker route existed for this domain. SSH confirmed Notification Bot healthy and restricted to localhost/private Docker networking.

| Priority | Baseline finding | Resolution |
| --- | --- | --- |
| High | Contact asked for email without address/link/form | Visible email and accessible form |
| High | Non-hero sections hidden when JavaScript fails | Visible baseline content, optional motion |
| High | No durable lead intake or delivery state | Worker + D1 + authenticated relay |
| Medium | About 800 words of notes before engagement/contact | Outcome-led services first, concise disclosures |
| Medium | Mobile removed all nav; 720 px header crowded | Responsive header and persistent contact action |
| Medium | Small text contrast around 3.39:1 light/3.78:1 dark | Readable tokens and both-theme review |
| Medium | Normal and italic fonts totalled about 724 KB | Lighter font strategy |
| Medium | Overlapping timelines; no client proof source | Scope-dependent copy, no fabricated results |
| Medium | No CI, version pin or recovery documentation | Pinned Hugo, build checks, tests and runbooks |

Preserve Hugo's small static output, hosting, semantic markup, skip link, keyboard focus, dark theme, reduced motion, local assets, fingerprinted CSS/JS, canonical/social metadata, robots and sitemap. Decision notes describe engineering reasoning, not invented client case studies.

## Boundaries

Cloudflare quotas are account-wide and include Bytlot. Separate resources do not create separate allowances. No subscription changes or paid features are authorized. A public endpoint may exhaust a free request quota under abuse; failures must retain form text and offer email.

Billing-list APIs returned authorization errors. The domain Free plan was verified; the user's stated Workers Free plan remains the operating assumption pending billing access. The implementation does not change subscriptions.

This release improves conversion and measures accepted enquiries; it does not supply acquisition traffic or guarantee customers. No blanket accessibility certification or unmeasured field-performance score is claimed. See release evidence for concrete verification.
