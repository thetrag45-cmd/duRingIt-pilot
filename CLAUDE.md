# gstack

Use the `/browse` skill from gstack for all web browsing. Never use `mcp__claude-in-chrome__*` tools.

To install gstack: `git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup`

Available gstack skills:
- `/office-hours` — structured office hours facilitation
- `/plan-ceo-review` — CEO review planning
- `/plan-eng-review` — engineering review planning
- `/plan-design-review` — design review planning
- `/design-consultation` — design consultation
- `/design-shotgun` — rapid design exploration
- `/design-html` — HTML design generation
- `/review` — code/PR review
- `/ship` — ship a feature end-to-end
- `/land-and-deploy` — land and deploy changes
- `/canary` — canary deployment
- `/benchmark` — performance benchmarking
- `/browse` — headless browser for QA, testing, and web browsing
- `/connect-chrome` — connect to Chrome browser
- `/qa` — full QA run
- `/qa-only` — QA without setup
- `/design-review` — design review
- `/setup-browser-cookies` — set up browser cookies
- `/setup-deploy` — configure deployment
- `/setup-gbrain` — configure gbrain
- `/retro` — retrospective facilitation
- `/investigate` — investigate an issue
- `/document-release` — document a release
- `/codex` — Codex agent integration
- `/cso` — CSO workflow
- `/autoplan` — automatic planning
- `/plan-devex-review` — devex review planning
- `/devex-review` — developer experience review
- `/careful` — careful/guarded mode
- `/freeze` — freeze deployments
- `/guard` — guard mode
- `/unfreeze` — unfreeze deployments
- `/gstack-upgrade` — upgrade gstack
- `/learn` — learning workflow

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
