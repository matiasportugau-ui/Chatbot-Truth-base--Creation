# Contributing

Thanks for helping improve this repository. The system is used for production
quotations and KB-driven responses, so changes should be careful and traceable.

## What to update
- Knowledge base files in `Files/`
- Documentation in root `.md` files and this wiki
- Agent logic and tooling in Python or TypeScript

## Suggested workflow
1. Create a focused change with a clear purpose.
2. Update or add documentation where behavior changes.
3. Run relevant scripts or checks.
4. Include examples for new features.

## Documentation guidelines
- Keep instructions consistent with `PANELIN_FULL_CONFIGURATION.md`.
- Do not add sensitive cost data to public docs.
- Prefer small, modular pages for the wiki.

## Testing
- Run KB update checks:
  - `python kb_update_optimizer.py --stats`
  - `python training_data_optimizer.py --stats`
- Run Agents SDK sample:
  - `ts-node panelin_agents_sdk_example.ts`

## References
- KB_UPDATE_QUICKSTART.md
- PANELIN_AGENTS_SDK_README.md
