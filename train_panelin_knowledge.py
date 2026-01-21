#!/usr/bin/env python3
"""
Panelin Knowledge Evolution System - 4-Level Training Orchestrator
===================================================================

This script orchestrates the evolutionary training protocol for Panelin's
knowledge base, enforcing a single source of truth and systematically
improving the bot's accuracy through 4 progressive levels.

Execution Strategy:
1. Level 1: Integrity Sanitization - Archive conflicts, validate truth
2. Level 2: Forensic Analysis - Learn from historical quotes/chats
3. Level 3: Social Adaptation - Ingest slang and map to SKUs
4. Level 4: Adversarial Hardening - Stress test against hostile queries

Author: Panelin Training System
Version: 1.0
Date: 2026-01-21
"""

import os
import sys
import shutil
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# --- CONFIGURATION: SINGLE SOURCE OF TRUTH (SSOT) ---
# We designate the V2 Web Scrape as the ONLY valid source of pricing/stock.
MASTER_TRUTH = "panelin_truth_bmcuruguay_web_only_v2.json"

# Files identified as "Leaks" (Legacy/Conflicting data)
CONFLICTING_FILES = [
    "BMC_Base_Conocimiento_GPT-2.json",  # ❌ LEAK: Old GPT-2 text base
    "BMC_Catalogo_Completo_Shopify (1).json",  # ❌ LEAK: Unprocessed export
    "Files /BMC_Base_Unificada_v4.json",  # ❌ LEAK: Version conflict (note: "Files " has space)
]

# Paths
ARCHIVE_DIR = "z_Archived_Truths"
LOG_DIR = "logs"
ROOT_DIR = Path(__file__).parent.absolute()

# --- LOGGING SETUP ---
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = f"{LOG_DIR}/training_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [PANELIN-TRAINER] - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(log_filename)],
)

logger = logging.getLogger(__name__)


class PanelinKnowledgeOrchestrator:
    """
    Orchestrates the 4-Level Evolutionary Training Protocol for Panelin KB.
    """

    def __init__(self):
        self.levels_passed = 0
        self.levels_total = 4
        self.start_time = datetime.now()
        logger.info("=" * 70)
        logger.info("PANELIN KNOWLEDGE EVOLUTION SYSTEM - INITIALIZED")
        logger.info("=" * 70)

    def level_1_integrity_sanitization(self):
        """
        LEVEL 1: INTEGRITY (Faithfulness)
        Goal: Enforce ONE Truth. Archive conflicts. Validate Math vs JSON.

        Returns:
            bool: True if integrity check passed, False otherwise
        """
        logger.info("\n" + "=" * 70)
        logger.info("🔹 LEVEL 1: TRUTH SANITIZATION & INTEGRITY")
        logger.info("=" * 70)

        # 1. Archive "Ghost" Truths
        archive_path = Path(ARCHIVE_DIR)
        if not archive_path.exists():
            archive_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"   📁 Created archive directory: {ARCHIVE_DIR}/")

        conflicts_found = False
        archived_files = []

        for file_path in CONFLICTING_FILES:
            # Handle both relative and absolute paths
            full_path = Path(file_path)
            if not full_path.is_absolute():
                full_path = ROOT_DIR / file_path

            if full_path.exists():
                try:
                    archive_dest = archive_path / full_path.name
                    # If file already exists in archive, add timestamp
                    if archive_dest.exists():
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        name_parts = full_path.stem, timestamp, full_path.suffix
                        archive_dest = (
                            archive_path
                            / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                        )

                    shutil.move(str(full_path), str(archive_dest))
                    logger.warning(
                        f"   ⚠️  LEAK SEALED: Archived '{full_path.name}' → {ARCHIVE_DIR}/"
                    )
                    conflicts_found = True
                    archived_files.append(full_path.name)
                except Exception as e:
                    logger.error(f"   ❌ Failed to archive {full_path}: {e}")
                    return False

        if not conflicts_found:
            logger.info("   ✅ File System Clean: No conflicting JSONs found.")
        else:
            logger.info(f"   📦 Archived {len(archived_files)} conflicting file(s)")

        # 2. Verify Master Truth Existence
        master_path = Path(MASTER_TRUTH)
        if not master_path.is_absolute():
            master_path = ROOT_DIR / MASTER_TRUTH

        if not master_path.exists():
            logger.critical(
                f"   🛑 CRITICAL FAILURE: Master Truth '{MASTER_TRUTH}' is missing!"
            )
            logger.critical(f"   Expected location: {master_path}")
            return False

        logger.info(f"   ✅ Master Truth verified: {MASTER_TRUTH}")

        # 3. Validate Logic (Python) vs Truth (JSON)
        validator_script = (
            ROOT_DIR / "panelin_improvements" / "source_of_truth_validator.py"
        )
        if validator_script.exists():
            logger.info("   🔎 Running Logic Validator (Math vs Text)...")
            try:
                result = subprocess.run(
                    [sys.executable, str(validator_script)],
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    cwd=str(ROOT_DIR),
                )

                if result.returncode != 0:
                    logger.error(
                        f"   ❌ INTEGRITY FAIL: Python Motor calculates different prices than JSON Catalog."
                    )
                    if result.stderr:
                        logger.error(f"   Error details: {result.stderr[:500]}")
                    return False

                logger.info("   ✅ Mathematical Integrity Verified.")
                if result.stdout:
                    logger.debug(f"   Validator output: {result.stdout[:200]}")
            except subprocess.TimeoutExpired:
                logger.error("   ❌ Validator timed out after 5 minutes")
                return False
            except Exception as e:
                logger.error(f"   ❌ Error running validator: {e}")
                return False
        else:
            logger.warning(
                f"   ⚠️  Skipping Logic Check: '{validator_script}' not found."
            )
            logger.warning(
                f"   This is non-critical, but recommended for full validation."
            )

        self.levels_passed += 1
        logger.info(f"   ✅ LEVEL 1 COMPLETE: Integrity Sanitization passed")
        return True

    def level_2_forensic_analysis(self):
        """
        LEVEL 2: FORENSIC LEARNING (Correctness)
        Goal: Learn from previous quotes/chats.

        Returns:
            bool: True if analysis completed (or skipped), False on critical error
        """
        logger.info("\n" + "=" * 70)
        logger.info("🔹 LEVEL 2: FORENSIC ANALYSIS LOOP")
        logger.info("=" * 70)

        analyzer = ROOT_DIR / "analizar_cotizaciones_2025.py"
        if analyzer.exists():
            logger.info(f"   📊 Mining chat logs via {analyzer.name}...")
            try:
                result = subprocess.run(
                    [sys.executable, str(analyzer)],
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                    cwd=str(ROOT_DIR),
                )

                if result.returncode == 0:
                    logger.info("   ✅ Forensic Analysis Completed Successfully")
                    if result.stdout:
                        logger.debug(f"   Output: {result.stdout[:300]}")
                else:
                    logger.warning(
                        f"   ⚠️  Analyzer returned non-zero exit code: {result.returncode}"
                    )
                    if result.stderr:
                        logger.warning(f"   Error: {result.stderr[:300]}")

                # Check for output files
                output_files = [
                    "analisis_completo_resultados.json",
                    "analisis_cotizaciones_resultados.json",
                    "ingestion_analysis_completo_*.json",
                ]

                found_output = False
                for pattern in output_files:
                    if "*" in pattern:
                        # Check for files matching pattern
                        import glob

                        matches = glob.glob(str(ROOT_DIR / pattern))
                        if matches:
                            found_output = True
                            logger.info(f"   📄 Found output: {matches[0]}")
                    else:
                        if (ROOT_DIR / pattern).exists():
                            found_output = True
                            logger.info(f"   📄 Found output: {pattern}")

                if found_output:
                    logger.info("   ✅ Optimization Report Generated.")
                else:
                    logger.info("   ℹ️  No output files detected (may be normal)")

            except subprocess.TimeoutExpired:
                logger.error("   ❌ Analyzer timed out after 10 minutes")
                return False
            except Exception as e:
                logger.error(f"   ❌ Error running analyzer: {e}")
                return False

            self.levels_passed += 1
            logger.info(f"   ✅ LEVEL 2 COMPLETE: Forensic Analysis passed")
        else:
            logger.warning(f"   ⚠️  Skipping: {analyzer.name} not found.")
            logger.warning(f"   Expected location: {analyzer}")
            logger.info("   ℹ️  This level is optional - continuing to next level")
            # Don't increment levels_passed if skipped

        return True

    def level_3_social_adaptation(self):
        """
        LEVEL 3: SOCIAL SEMANTICS (Context Relevance)
        Goal: Ingest slang (e.g. 'Techo Sandwich') and map to SKUs.

        Returns:
            bool: True if adaptation completed (or skipped), False on critical error
        """
        logger.info("\n" + "=" * 70)
        logger.info("🔹 LEVEL 3: SOCIAL ADAPTATION")
        logger.info("=" * 70)

        social_ingest = (
            ROOT_DIR
            / "gpt_simulation_agent"
            / "agent_system"
            / "agent_social_ingestion.py"
        )
        gem_gen = ROOT_DIR / "codex_to_gem_generator.py"

        level_complete = False

        # Step 1: Ingest Social Signals
        if social_ingest.exists():
            logger.info("   🎧 Listening to Social Signals...")
            try:
                result = subprocess.run(
                    [sys.executable, str(social_ingest)],
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                    cwd=str(ROOT_DIR),
                )

                if result.returncode == 0:
                    logger.info("   ✅ Social Ingestion Completed")
                else:
                    logger.warning(
                        f"   ⚠️  Social ingestion returned exit code: {result.returncode}"
                    )
            except subprocess.TimeoutExpired:
                logger.error("   ❌ Social ingestion timed out")
            except Exception as e:
                logger.error(f"   ❌ Error in social ingestion: {e}")
        else:
            logger.warning(f"   ⚠️  Social ingestion script not found: {social_ingest}")

        # Step 2: Generate Knowledge Gems
        if gem_gen.exists():
            logger.info("   💎 Synthesizing new Knowledge Gems...")
            try:
                result = subprocess.run(
                    [sys.executable, str(gem_gen)],
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                    cwd=str(ROOT_DIR),
                )

                if result.returncode == 0:
                    logger.info("   ✅ Knowledge Gems Generated")
                    level_complete = True
                else:
                    logger.warning(
                        f"   ⚠️  Gem generator returned exit code: {result.returncode}"
                    )
            except subprocess.TimeoutExpired:
                logger.error("   ❌ Gem generator timed out")
            except Exception as e:
                logger.error(f"   ❌ Error generating gems: {e}")
        else:
            logger.warning(f"   ⚠️  Gem Generator not found: {gem_gen}")
            logger.info("   ℹ️  This level is optional - continuing to next level")

        if level_complete:
            logger.info("   ✅ Vocabulary Updated.")
            self.levels_passed += 1
            logger.info(f"   ✅ LEVEL 3 COMPLETE: Social Adaptation passed")
        else:
            logger.info("   ℹ️  Level 3 partially completed or skipped")

        return True

    def level_4_adversarial_hardening(self):
        """
        LEVEL 4: ROBUSTNESS (Safety)
        Goal: Stress test the bot against a hostile AI agent.

        Returns:
            bool: True if stress test completed (or skipped), False on critical error
        """
        logger.info("\n" + "=" * 70)
        logger.info("🔹 LEVEL 4: ADVERSARIAL STRESS TEST")
        logger.info("=" * 70)

        sim_agent = (
            ROOT_DIR
            / "gpt_simulation_agent"
            / "agent_system"
            / "gpt_simulation_agent.py"
        )
        if sim_agent.exists():
            logger.info("   🥊 Spawning 'Skeptical Customer' Agent...")
            try:
                # Running in stress mode
                result = subprocess.run(
                    [sys.executable, str(sim_agent), "--mode=stress"],
                    capture_output=True,
                    text=True,
                    timeout=900,  # 15 minute timeout
                    cwd=str(ROOT_DIR),
                )

                if result.returncode == 0:
                    logger.info("   ✅ Robustness Test Complete.")
                    self.levels_passed += 1
                    logger.info(f"   ✅ LEVEL 4 COMPLETE: Adversarial Hardening passed")
                else:
                    logger.warning(
                        f"   ⚠️  Stress test returned exit code: {result.returncode}"
                    )
                    if result.stderr:
                        logger.warning(f"   Error: {result.stderr[:300]}")
            except subprocess.TimeoutExpired:
                logger.error("   ❌ Stress test timed out after 15 minutes")
            except Exception as e:
                logger.error(f"   ❌ Error in stress test: {e}")
        else:
            logger.warning(f"   ⚠️  Simulation Agent not found: {sim_agent}")
            logger.info("   ℹ️  This level is optional - training will complete")

        return True

    def generate_summary_report(self):
        """Generate a summary report of the training session."""
        end_time = datetime.now()
        duration = end_time - self.start_time

        logger.info("\n" + "=" * 70)
        logger.info("📊 TRAINING SESSION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"   Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"   Duration: {duration}")
        logger.info(f"   Levels Passed: {self.levels_passed}/{self.levels_total}")
        logger.info(f"   Log File: {log_filename}")
        logger.info(f"   Archive Directory: {ARCHIVE_DIR}/")
        logger.info("=" * 70)

        # Write summary to file
        summary_file = (
            ROOT_DIR
            / LOG_DIR
            / f"training_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(summary_file, "w") as f:
            f.write("PANELIN KNOWLEDGE EVOLUTION SYSTEM - TRAINING SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Duration: {duration}\n")
            f.write(f"Levels Passed: {self.levels_passed}/{self.levels_total}\n\n")
            f.write(f"Log File: {log_filename}\n")
            f.write(f"Archive Directory: {ARCHIVE_DIR}/\n")
            f.write(f"Master Truth: {MASTER_TRUTH}\n")

        logger.info(f"   📄 Summary saved to: {summary_file}")


def main():
    """Main execution function."""
    print("\n" + "🤖" * 35)
    print("🤖 INITIALIZING PANELIN KNOWLEDGE EVOLUTION SYSTEM...")
    print("🤖" * 35 + "\n")

    trainer = PanelinKnowledgeOrchestrator()

    # Execute the Evolutionary Chain
    success = True

    if trainer.level_1_integrity_sanitization():
        trainer.level_2_forensic_analysis()
        trainer.level_3_social_adaptation()
        trainer.level_4_adversarial_hardening()
    else:
        success = False
        logger.critical("\n🛑 TRAINING HALTED: Critical Integrity Failure.")
        logger.critical("   Fix the Truth Base first before continuing.")

    # Generate summary report
    trainer.generate_summary_report()

    # Final status
    print("\n" + "=" * 70)
    if success:
        print(
            f"🏆 TRAINING COMPLETE. Levels Passed: {trainer.levels_passed}/{trainer.levels_total}"
        )
        print(f"📂 Conflicting files moved to: ./{ARCHIVE_DIR}/")
        print(f"📄 Detailed logs: {log_filename}")
    else:
        print("🛑 TRAINING HALTED: Critical Integrity Failure.")
        print("   Review logs and fix issues before retrying.")
    print("=" * 70 + "\n")

    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Training interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.critical(f"\n💥 Fatal error: {e}", exc_info=True)
        sys.exit(1)
