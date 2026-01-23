# Troubleshooting and FAQ

## Common setup issues

### "OPENAI_API_KEY not set"
- Ensure the environment variable is exported or `.env` exists.
- Verify with: `echo $OPENAI_API_KEY`

### "Module not found"
- Install dependencies with `pip install -r requirements.txt`.
- Some subprojects include their own `requirements.txt`.

### "File not found" errors
- Confirm that the `Files/` directory exists.
- Ensure KB files are in the expected locations.
- Run `python kb_update_optimizer.py --stats` for a quick check.

## Panelin GPT behavior issues

### Panelin invents prices
- Verify `BMC_Base_Conocimiento_GPT-2.json` is uploaded first.
- Re-check instructions in `PANELIN_INSTRUCTIONS_FINAL.txt`.
- Wait for KB reindexing after uploads (2-3 minutes).

### Personalization does not trigger
- Confirm instructions include the personalization section.
- Start a new conversation in GPT Builder.

### Model not found
- Use a model available for your account (e.g., gpt-4o or gpt-4-turbo).
- Check API access and billing status.

### PDF generation does not work
- Enable Code Interpreter in GPT Builder.
- Provide a direct request like "Genera un PDF de esta cotizacion".

## Agents SDK issues

### "Tool execution failed"
- Ensure tool implementations are wired to Python backends.
- Validate input schemas passed to tools.

### "Agent result is undefined"
- Verify the agent returns `finalOutput`.
- Increase `maxTokens` or adjust model settings.

## Scheduler issues

### Scheduler not running
- Check logs (scheduler.log or logs/kb_scheduler_*.log).
- Run `python kb_auto_scheduler.py --once` to test.

## References
- KB_UPDATE_QUICKSTART.md
- PANELIN_FULL_CONFIGURATION.md
- PANELIN_AGENTS_SDK_README.md
