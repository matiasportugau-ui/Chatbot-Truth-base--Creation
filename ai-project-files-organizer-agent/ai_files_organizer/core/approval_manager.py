"""
Approval Manager for handling user approvals of file organization proposals
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ApprovalManager:
    """
    Manages approval workflow for file organization proposals
    """

    def __init__(
        self,
        require_approval: bool = True,
        batch_mode: bool = True,
        history_file: Optional[Path] = None,
    ):
        """
        Initialize approval manager.

        Args:
            require_approval: If True, require approval for all actions
            batch_mode: If True, allow batch approvals
            history_file: Path to store approval history
        """
        self.require_approval = require_approval
        self.batch_mode = batch_mode
        self.history_file = history_file
        self.history: List[Dict] = []

    def request_approval(
        self, proposal: Dict, interactive: bool = True
    ) -> Dict:
        """
        Request approval for a single proposal.

        Args:
            proposal: Proposal dictionary
            interactive: If True, prompt user interactively

        Returns:
            Approval result dictionary
        """
        if not self.require_approval:
            return {"approved": True, "action": "auto_approved"}

        if interactive:
            return self._interactive_approval(proposal)
        else:
            # Non-interactive mode - return pending
            return {"approved": False, "action": "pending", "proposal": proposal}

    def request_batch_approval(
        self, proposals: List[Dict], interactive: bool = True
    ) -> Dict:
        """
        Request batch approval for multiple proposals.

        Args:
            proposals: List of proposal dictionaries
            interactive: If True, prompt user interactively

        Returns:
            Batch approval result dictionary
        """
        if not self.require_approval:
            return {
                "approved": True,
                "action": "auto_approved",
                "approved_proposals": proposals,
            }

        if not self.batch_mode:
            # Process individually
            results = []
            for proposal in proposals:
                result = self.request_approval(proposal, interactive)
                results.append(result)
            return {"results": results}

        if interactive:
            return self._interactive_batch_approval(proposals)
        else:
            return {
                "approved": False,
                "action": "pending",
                "proposals": proposals,
            }

    def _interactive_approval(self, proposal: Dict) -> Dict:
        """Interactive approval for single proposal"""
        print("\n" + "=" * 60)
        print("📋 FILE ORGANIZATION PROPOSAL")
        print("=" * 60)
        print(f"\nFile: {proposal['file']}")
        print(f"Current: {proposal['current_location']}")
        print(f"Proposed: {proposal['proposed_location']}")
        print(f"\nJustification: {proposal['justification']}")
        print(f"Confidence: {proposal['confidence']:.2%}")
        print(f"Actions: {', '.join(proposal['actions'])}")
        print("\n" + "-" * 60)

        while True:
            response = input(
                "\nApprove this proposal? (yes/no/modify/skip): "
            ).strip().lower()

            if response in ["yes", "y"]:
                self._record_approval(proposal, "approved")
                return {"approved": True, "action": "approved", "proposal": proposal}
            elif response in ["no", "n"]:
                self._record_approval(proposal, "rejected")
                return {"approved": False, "action": "rejected", "proposal": proposal}
            elif response in ["modify", "m"]:
                modified = self._modify_proposal(proposal)
                if modified:
                    return self._interactive_approval(modified)
            elif response in ["skip", "s"]:
                return {"approved": False, "action": "skipped", "proposal": proposal}
            else:
                print("Invalid response. Please enter yes/no/modify/skip")

    def _interactive_batch_approval(self, proposals: List[Dict]) -> Dict:
        """Interactive batch approval"""
        print("\n" + "=" * 60)
        print(f"📋 BATCH ORGANIZATION PROPOSALS ({len(proposals)} files)")
        print("=" * 60)

        # Group by category
        by_category: Dict[str, List[Dict]] = {}
        for proposal in proposals:
            # Extract category from proposed location
            category = Path(proposal["proposed_location"]).parts[-1]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(proposal)

        print("\nProposals grouped by category:")
        for category, props in by_category.items():
            print(f"  {category}: {len(props)} files")

        print("\n" + "-" * 60)
        print("\nOptions:")
        print("  1. Approve all")
        print("  2. Approve by category")
        print("  3. Review individually")
        print("  4. Reject all")

        while True:
            choice = input("\nYour choice (1-4): ").strip()

            if choice == "1":
                self._record_batch_approval(proposals, "approved_all")
                return {
                    "approved": True,
                    "action": "approved_all",
                    "approved_proposals": proposals,
                }
            elif choice == "2":
                return self._approve_by_category(by_category)
            elif choice == "3":
                return self._review_individually(proposals)
            elif choice == "4":
                self._record_batch_approval(proposals, "rejected_all")
                return {
                    "approved": False,
                    "action": "rejected_all",
                    "proposals": proposals,
                }
            else:
                print("Invalid choice. Please enter 1-4")

    def _approve_by_category(self, by_category: Dict[str, List[Dict]]) -> Dict:
        """Approve proposals by category"""
        approved = []
        rejected = []

        for category, proposals in by_category.items():
            print(f"\nCategory: {category} ({len(proposals)} files)")
            response = input("Approve this category? (yes/no): ").strip().lower()

            if response in ["yes", "y"]:
                approved.extend(proposals)
                self._record_batch_approval(proposals, f"approved_category_{category}")
            else:
                rejected.extend(proposals)

        return {
            "approved": len(approved) > 0,
            "action": "approved_by_category",
            "approved_proposals": approved,
            "rejected_proposals": rejected,
        }

    def _review_individually(self, proposals: List[Dict]) -> Dict:
        """Review proposals individually"""
        approved = []
        rejected = []
        skipped = []

        for proposal in proposals:
            result = self._interactive_approval(proposal)
            if result["approved"]:
                approved.append(proposal)
            elif result["action"] == "rejected":
                rejected.append(proposal)
            else:
                skipped.append(proposal)

        return {
            "approved": len(approved) > 0,
            "action": "reviewed_individually",
            "approved_proposals": approved,
            "rejected_proposals": rejected,
            "skipped_proposals": skipped,
        }

    def _modify_proposal(self, proposal: Dict) -> Optional[Dict]:
        """Allow user to modify proposal"""
        print("\nModify proposal:")
        print(f"Current proposed location: {proposal['proposed_location']}")
        new_location = input("Enter new location (or press Enter to keep): ").strip()

        if new_location:
            proposal["proposed_location"] = new_location
            proposal["justification"] = "User-modified location"
            return proposal

        return None

    def _record_approval(self, proposal: Dict, action: str):
        """Record approval decision to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "file": str(proposal["file"]),
            "action": action,
            "proposal": proposal,
        }
        self.history.append(entry)

        if self.history_file:
            self._save_history()

    def _record_batch_approval(self, proposals: List[Dict], action: str):
        """Record batch approval decision"""
        for proposal in proposals:
            self._record_approval(proposal, action)

    def _save_history(self):
        """Save approval history to file"""
        if self.history_file:
            try:
                self.history_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.history_file, "w", encoding="utf-8") as f:
                    json.dump(self.history, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

    def load_history(self) -> List[Dict]:
        """Load approval history from file"""
        if self.history_file and self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []

        return self.history
