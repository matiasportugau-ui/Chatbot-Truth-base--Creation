# Panelin Wiki

This folder contains the complete GitHub Wiki documentation for the Panelin AI System.

## How to Use

### Option 1: View in Repository

All wiki pages are Markdown files that can be viewed directly in the repository.

### Option 2: GitHub Wiki

To use these as a proper GitHub Wiki:

1. **Clone the wiki repository:**
   ```bash
   git clone https://github.com/your-org/panelin.wiki.git
   ```

2. **Copy wiki files:**
   ```bash
   cp wiki/*.md panelin.wiki/
   ```

3. **Push to wiki:**
   ```bash
   cd panelin.wiki
   git add .
   git commit -m "Update wiki documentation"
   git push
   ```

### Option 3: GitHub Actions (Automated)

Add a workflow to automatically sync wiki:

```yaml
# .github/workflows/sync-wiki.yml
name: Sync Wiki
on:
  push:
    paths:
      - 'wiki/**'
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Sync to wiki
        uses: SwiftDocOrg/github-wiki-publish-action@v1
        with:
          path: wiki
        env:
          GH_PERSONAL_ACCESS_TOKEN: ${{ secrets.GH_PAT }}
```

## Wiki Structure

```
wiki/
├── Home.md                    # Main landing page
├── Getting-Started.md         # Installation & setup
├── Architecture.md            # System architecture
├── Configuration.md           # Configuration guide
├── Troubleshooting.md         # Common issues
├── API-Reference.md           # API documentation
│
├── Agents-Overview.md         # All agents summary
├── Quotation-Agent.md         # Quotation agent
├── Analysis-Agent.md          # Analysis agent
├── GPT-Simulation-Agent.md    # GPT simulation
├── KB-Config-Agent.md         # KB configuration
├── Files-Organizer-Agent.md   # File organization
│
├── Knowledge-Base.md          # KB documentation
├── Quotation-Engine.md        # Core engine
├── Training-System.md         # Training system
├── Multi-Model-Orchestration.md # Model routing
├── Evaluation-Metrics.md      # Evaluation metrics
│
├── Contributing.md            # Contribution guide
├── Changelog.md               # Version history
│
├── _Sidebar.md                # Wiki navigation
└── _Footer.md                 # Wiki footer
```

## Page Count

- **Core Documentation:** 6 pages
- **Agent Documentation:** 6 pages  
- **System Components:** 4 pages
- **Project Pages:** 2 pages
- **Navigation:** 2 pages

**Total: 20+ comprehensive wiki pages**

## Contributing

To add or update wiki pages:

1. Edit the Markdown files in this folder
2. Follow the existing format and style
3. Update `_Sidebar.md` if adding new pages
4. Submit a pull request

## License

This documentation is part of the Panelin AI System and is licensed under the MIT License.
