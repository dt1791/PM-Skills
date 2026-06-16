# Contributing

PM Skills Marketplace is maintained by [Paweł Huryn](https://www.productcompass.pm) (pawel@productcompass.pm). Contributions are welcome — whether it's a bug fix, a typo, or a new skill idea.

## How to Contribute

- **Bugs and small fixes** — open a PR directly.
- **New skills, commands, or larger changes** — open an issue first so we can discuss the approach.

## Guidelines

- Keep PRs focused — one change per PR.
- Follow existing patterns: skills are nouns (domain knowledge), commands are verbs (workflows), agents mirror skills for Cursor sub-agent delegation.
- Every skill needs frontmatter with `name` and `description`. Every command needs `description` and `argument-hint`. Every agent needs `name` and `description` matching its skill.
- Skill `name` must match its directory name. Agent `name` must match its filename (without `.md`).
- No cross-plugin references in commands. Suggest follow-ups in natural language only.
- Every contributor will be listed publicly.
- Run the validator before submitting: `python3 validate_plugins.py`
- Regenerate Cursor sub-agents after skill changes: `python3 generate_agents.py`
- Regenerate pm-product-discovery sub-agents (full embedded workflows): `python3 generate_discovery_agents.py`

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
