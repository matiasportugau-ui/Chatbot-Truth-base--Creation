"""
CLI interface for AI Files Organizer Agent
"""

import sys
from pathlib import Path
from typing import Optional

import click

from .agent import FileOrganizerAgent
from .utils.logger import setup_logger


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AI Project Files Organizer Agent - Organize your project files automatically"""
    pass


@cli.command()
@click.argument("workspace_path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--no-approval", is_flag=True, help="Skip approval prompts (use with caution)")
@click.option("--interactive/--no-interactive", default=True, help="Interactive mode")
def organize(workspace_path: str, config: Optional[str], no_approval: bool, interactive: bool):
    """Organize existing files in workspace"""
    try:
        config_path = Path(config) if config else None
        agent = FileOrganizerAgent(
            workspace_path=workspace_path,
            config_path=config_path,
            require_approval=not no_approval,
        )
        
        result = agent.organize_existing_files(interactive=interactive)
        
        if result.get("success"):
            click.echo(f"✅ Successfully organized {len(result.get('results', {}).get('successful', []))} files")
        else:
            click.echo("❌ Organization was not completed")
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("workspace_path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--no-approval", is_flag=True, help="Skip approval prompts")
def watch(workspace_path: str, config: Optional[str], no_approval: bool):
    """Start watching for file changes and organize automatically"""
    try:
        config_path = Path(config) if config else None
        agent = FileOrganizerAgent(
            workspace_path=workspace_path,
            config_path=config_path,
            require_approval=not no_approval,
        )
        
        click.echo(f"👀 Watching {workspace_path} for changes...")
        click.echo("Press Ctrl+C to stop")
        
        agent.start_monitoring(interactive=not no_approval)
        
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo("\n🛑 Stopping file watcher...")
            agent.stop_monitoring()
            click.echo("✅ Stopped")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("workspace_path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--outdated", is_flag=True, help="Also detect outdated files")
def scan(workspace_path: str, outdated: bool):
    """Scan workspace and show organization suggestions without making changes"""
    try:
        agent = FileOrganizerAgent(workspace_path=workspace_path, require_approval=False)
        
        # Scan files
        files = agent.scanner.scan()
        click.echo(f"📊 Scanned {len(files)} files")
        
        # Generate proposals
        proposals = agent.folder_engine.generate_batch_proposals(files, agent.workspace_path)
        click.echo(f"💡 Generated {len(proposals)} organization proposals")
        
        # Show summary
        by_category = {}
        for proposal in proposals:
            category = Path(proposal["proposed_location"]).parts[-1]
            by_category[category] = by_category.get(category, 0) + 1
        
        click.echo("\n📁 Proposed organization:")
        for category, count in sorted(by_category.items()):
            click.echo(f"  {category}: {count} files")
        
        # Check for outdated files
        if outdated:
            outdated_files = agent.detect_outdated_files()
            if outdated_files:
                click.echo(f"\n⚠️  Found {len(outdated_files)} outdated files")
            else:
                click.echo("\n✅ No outdated files detected")
                
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def version():
    """Show version information"""
    click.echo("AI Project Files Organizer Agent v0.1.0")


if __name__ == "__main__":
    cli()
