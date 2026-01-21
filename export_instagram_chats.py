#!/usr/bin/env python3
"""
Export Instagram Chats

This script exports all Instagram direct messages (chats) in multiple formats.
Supports:
1. Instagram Graph API (requires business account with permissions)
2. Processing Instagram data download files (from Instagram's "Download Your Information")
"""

import json
import os
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
# Optional imports
try:
    from loguru import logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Try to import Instagram API client if available
try:
    from gpt_simulation_agent.agent_system.utils.instagram_api import InstagramAPIClient
    HAS_INSTAGRAM_API = True
except ImportError:
    HAS_INSTAGRAM_API = False
    logger.warning("Instagram API client not available. Only file processing will work.")


class InstagramChatExporter:
    """Export Instagram chats from API or downloaded data files"""

    def __init__(self, output_dir: str = "instagram_chats_export"):
        """
        Initialize exporter
        
        Args:
            output_dir: Directory to save exported chats
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def export_from_api(
        self,
        access_token: Optional[str] = None,
        business_account_id: Optional[str] = None,
        limit: int = 1000
    ) -> Dict:
        """
        Export chats using Instagram Graph API
        
        Args:
            access_token: Instagram access token
            business_account_id: Business account ID
            limit: Maximum number of messages to export
            
        Returns:
            Dictionary with export results
        """
        if not HAS_INSTAGRAM_API:
            raise ValueError("Instagram API client not available. Install required dependencies.")
            
        logger.info("Exporting Instagram chats from API...")
        
        # Initialize client
        client = InstagramAPIClient(
            access_token=access_token,
            business_account_id=business_account_id
        )
        
        # Note: Instagram DMs require Instagram Messaging API permissions
        # This is a placeholder - actual implementation requires special setup
        logger.warning("Instagram DMs via Graph API require Instagram Messaging API setup")
        logger.info("For personal accounts, use Instagram's 'Download Your Information' feature")
        
        # Try to get DMs (may return empty if not configured)
        dms = client.get_direct_messages(limit=limit)
        
        if dms:
            normalized_dms = [
                client.normalize_interaction(dm, "dm")
                for dm in dms
            ]
            return self._save_chats(normalized_dms, "api_export")
        else:
            logger.info("No DMs retrieved. Check API permissions or use file-based export.")
            return {"count": 0, "files": []}
    
    def export_from_files(
        self,
        instagram_data_path: str,
        include_archived: bool = True
    ) -> Dict:
        """
        Export chats from Instagram data download files
        
        Args:
            instagram_data_path: Path to Instagram data download folder
            include_archived: Include archived chats
            
        Returns:
            Dictionary with export results
        """
        logger.info(f"Exporting Instagram chats from files: {instagram_data_path}")
        
        data_path = Path(instagram_data_path)
        
        if not data_path.exists():
            raise ValueError(f"Instagram data path does not exist: {instagram_data_path}")
        
        # Look for messages folder
        messages_path = data_path / "messages"
        if not messages_path.exists():
            # Try alternative locations
            messages_path = data_path / "direct_messages"
            if not messages_path.exists():
                messages_path = data_path / "inbox"
        
        if not messages_path.exists():
            raise ValueError(
                f"Messages folder not found in {instagram_data_path}. "
                "Expected: messages/, direct_messages/, or inbox/"
            )
        
        all_chats = []
        chat_files = list(messages_path.glob("**/*.json"))
        
        logger.info(f"Found {len(chat_files)} chat files")
        
        for chat_file in chat_files:
            try:
                with open(chat_file, 'r', encoding='utf-8') as f:
                    chat_data = json.load(f)
                
                # Handle different Instagram data formats
                if isinstance(chat_data, list):
                    # Direct list of messages
                    all_chats.extend(self._parse_messages(chat_data, chat_file.name))
                elif isinstance(chat_data, dict):
                    # Structured format
                    if "participants" in chat_data:
                        # Thread format
                        messages = chat_data.get("messages", [])
                        participants = chat_data.get("participants", [])
                        thread_title = chat_data.get("title", chat_file.stem)
                        
                        parsed = self._parse_thread(
                            messages,
                            participants,
                            thread_title,
                            chat_file.name
                        )
                        all_chats.extend(parsed)
                    elif "messages" in chat_data:
                        # Simple messages format
                        all_chats.extend(self._parse_messages(chat_data["messages"], chat_file.name))
                
            except Exception as e:
                logger.error(f"Error processing {chat_file}: {e}")
                continue
        
        if not all_chats:
            logger.warning("No chats found in the provided files")
            return {"count": 0, "files": []}
        
        logger.info(f"Parsed {len(all_chats)} messages from {len(chat_files)} files")
        
        return self._save_chats(all_chats, "file_export")
    
    def _parse_thread(
        self,
        messages: List[Dict],
        participants: List[Dict],
        thread_title: str,
        source_file: str
    ) -> List[Dict]:
        """Parse a message thread"""
        parsed = []
        
        participant_names = [p.get("name", "") for p in participants]
        
        for msg in messages:
            parsed_msg = {
                "id": msg.get("id", ""),
                "platform": "instagram",
                "type": "direct_message",
                "thread_title": thread_title,
                "participants": participant_names,
                "sender": msg.get("sender_name", ""),
                "content": msg.get("content", ""),
                "timestamp": self._parse_instagram_timestamp(msg.get("timestamp_ms")),
                "is_share": msg.get("share", {}).get("link") is not None,
                "is_photo": "photos" in msg or "image_path" in msg,
                "is_video": "videos" in msg or "video_path" in msg,
                "is_audio": "audio_files" in msg or "audio_path" in msg,
                "source_file": source_file,
                "metadata": {
                    "is_question": self._is_question(msg.get("content", "")),
                    "reactions": msg.get("reactions", []),
                }
            }
            
            # Add media info if present
            if "photos" in msg:
                parsed_msg["media"] = [{"type": "photo", "uri": p.get("uri", "")} for p in msg["photos"]]
            if "videos" in msg:
                parsed_msg["media"] = [{"type": "video", "uri": v.get("uri", "")} for v in msg["videos"]]
            
            parsed.append(parsed_msg)
        
        return parsed
    
    def _parse_messages(self, messages: List[Dict], source_file: str) -> List[Dict]:
        """Parse a list of messages"""
        parsed = []
        
        for msg in messages:
            parsed_msg = {
                "id": msg.get("id", ""),
                "platform": "instagram",
                "type": "direct_message",
                "sender": msg.get("sender_name", msg.get("from", "")),
                "content": msg.get("content", msg.get("text", "")),
                "timestamp": self._parse_instagram_timestamp(msg.get("timestamp_ms", msg.get("timestamp"))),
                "source_file": source_file,
                "metadata": {
                    "is_question": self._is_question(msg.get("content", msg.get("text", ""))),
                }
            }
            parsed.append(parsed_msg)
        
        return parsed
    
    def _parse_instagram_timestamp(self, timestamp: Optional[any]) -> str:
        """Parse Instagram timestamp to ISO-8601"""
        if not timestamp:
            return datetime.now().isoformat()
        
        try:
            if isinstance(timestamp, (int, float)):
                # Instagram uses milliseconds
                if timestamp > 1e10:
                    timestamp = timestamp / 1000
                dt = datetime.fromtimestamp(timestamp)
            elif isinstance(timestamp, str):
                dt = datetime.fromtimestamp(int(timestamp) / 1000)
            else:
                return datetime.now().isoformat()
            
            return dt.isoformat()
        except Exception as e:
            logger.warning(f"Error parsing timestamp {timestamp}: {e}")
            return datetime.now().isoformat()
    
    def _is_question(self, text: str) -> bool:
        """Check if text is a question"""
        if not text:
            return False
        question_words = [
            "?", "qué", "cuál", "cómo", "cuándo", "dónde", "por qué",
            "who", "what", "when", "where", "why", "how", "¿"
        ]
        return any(word in text.lower() for word in question_words)
    
    def _save_chats(self, chats: List[Dict], export_type: str) -> Dict:
        """Save chats in multiple formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = self.output_dir / f"instagram_chats_{export_type}_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(chats, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(chats)} chats to {json_file}")
        
        # Save as JSONL (one message per line)
        jsonl_file = self.output_dir / f"instagram_chats_{export_type}_{timestamp}.jsonl"
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for chat in chats:
                f.write(json.dumps(chat, ensure_ascii=False) + '\n')
        logger.info(f"Saved {len(chats)} chats to {jsonl_file}")
        
        # Save as grouped by thread (if thread info available)
        threads = {}
        for chat in chats:
            thread_key = chat.get("thread_title", chat.get("participants", ["Unknown"])[0] if chat.get("participants") else "Unknown")
            if thread_key not in threads:
                threads[thread_key] = []
            threads[thread_key].append(chat)
        
        threads_file = self.output_dir / f"instagram_chats_by_thread_{export_type}_{timestamp}.json"
        with open(threads_file, 'w', encoding='utf-8') as f:
            json.dump(threads, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(threads)} threads to {threads_file}")
        
        # Generate summary
        summary = {
            "export_type": export_type,
            "timestamp": timestamp,
            "total_messages": len(chats),
            "total_threads": len(threads),
            "date_range": {
                "earliest": min((c.get("timestamp", "") for c in chats), default=""),
                "latest": max((c.get("timestamp", "") for c in chats), default="")
            },
            "files": {
                "json": str(json_file),
                "jsonl": str(jsonl_file),
                "by_thread": str(threads_file)
            }
        }
        
        summary_file = self.output_dir / f"export_summary_{export_type}_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        return {
            "count": len(chats),
            "threads": len(threads),
            "files": [
                str(json_file),
                str(jsonl_file),
                str(threads_file),
                str(summary_file)
            ],
            "summary": summary
        }


def main():
    parser = argparse.ArgumentParser(
        description="Export Instagram chats from API or downloaded data files"
    )
    
    parser.add_argument(
        "--method",
        choices=["api", "files", "both"],
        default="files",
        help="Export method: api, files, or both (default: files)"
    )
    
    parser.add_argument(
        "--data-path",
        type=str,
        help="Path to Instagram data download folder (for file-based export)"
    )
    
    parser.add_argument(
        "--access-token",
        type=str,
        help="Instagram access token (for API export)"
    )
    
    parser.add_argument(
        "--business-account-id",
        type=str,
        help="Instagram business account ID (for API export)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="instagram_chats_export",
        help="Output directory for exported chats (default: instagram_chats_export)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        help="Maximum number of messages to export (for API method)"
    )
    
    args = parser.parse_args()
    
    exporter = InstagramChatExporter(output_dir=args.output_dir)
    
    results = {}
    
    if args.method in ["files", "both"]:
        if not args.data_path:
            # Try to find default Instagram data location
            default_paths = [
                Path.home() / "Downloads" / "instagram_data",
                Path.home() / "Downloads" / "instagram",
                Path("instagram_data"),
            ]
            
            found = False
            for path in default_paths:
                if path.exists():
                    args.data_path = str(path)
                    found = True
                    break
            
            if not found:
                logger.error(
                    "No data path provided and no default location found. "
                    "Please provide --data-path or download your Instagram data first."
                )
                logger.info(
                    "To download your Instagram data:\n"
                    "1. Go to Instagram Settings\n"
                    "2. Privacy and Security\n"
                    "3. Download Your Information\n"
                    "4. Select 'Messages' and request download"
                )
                return
        
        try:
            results["files"] = exporter.export_from_files(args.data_path)
            logger.success(f"✅ Exported {results['files']['count']} messages from files")
        except Exception as e:
            logger.error(f"Error exporting from files: {e}")
            results["files"] = {"error": str(e)}
    
    if args.method in ["api", "both"]:
        access_token = args.access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        business_account_id = args.business_account_id or os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
        
        if not access_token:
            logger.warning(
                "No access token provided. Set INSTAGRAM_ACCESS_TOKEN env var or use --access-token.\n"
                "Note: Instagram DMs require Instagram Messaging API permissions."
            )
        else:
            try:
                results["api"] = exporter.export_from_api(
                    access_token=access_token,
                    business_account_id=business_account_id,
                    limit=args.limit
                )
                logger.success(f"✅ Exported {results['api']['count']} messages from API")
            except Exception as e:
                logger.error(f"Error exporting from API: {e}")
                results["api"] = {"error": str(e)}
    
    # Print summary
    print("\n" + "="*60)
    print("EXPORT SUMMARY")
    print("="*60)
    for method, result in results.items():
        if "error" in result:
            print(f"\n{method.upper()}: ❌ {result['error']}")
        else:
            print(f"\n{method.upper()}:")
            print(f"  Messages: {result.get('count', 0)}")
            print(f"  Threads: {result.get('threads', 0)}")
            print(f"  Files saved: {len(result.get('files', []))}")
    
    print(f"\n📁 Output directory: {args.output_dir}")
    print("="*60)


if __name__ == "__main__":
    main()
