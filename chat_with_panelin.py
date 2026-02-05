#!/usr/bin/env python3
"""
Chat with Panelin Assistant
============================

Simple script to chat with your Panelin assistant created via API.

Usage:
    python chat_with_panelin.py
    python chat_with_panelin.py --assistant-id YOUR_ASSISTANT_ID
"""

import os
import sys
import argparse
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def get_assistant_id(assistant_id_arg: str = None) -> str:
    """Get assistant ID from argument, file, or prompt user"""
    if assistant_id_arg:
        return assistant_id_arg
    
    # Try to read from file
    id_file = Path(".panelin_assistant_id")
    if id_file.exists():
        return id_file.read_text().strip()
    
    # Prompt user
    print("⚠️  No assistant ID found.")
    assistant_id = input("Enter your Panelin Assistant ID: ").strip()
    if not assistant_id:
        print("❌ Assistant ID is required. Exiting.")
        sys.exit(1)
    return assistant_id


def chat_with_panelin(client: OpenAI, assistant_id: str):
    """Interactive chat with Panelin"""
    print("\n" + "=" * 60)
    print("💬 Chat with Panelin - BMC Assistant Pro")
    print("=" * 60)
    print("Type 'exit' or 'quit' to end the conversation\n")
    
    # Create a thread
    thread = client.beta.threads.create()
    print(f"✅ Thread created: {thread.id}\n")
    
    while True:
        # Get user input
        user_message = input("You: ").strip()
        
        if user_message.lower() in ["exit", "quit", "salir"]:
            print("\n👋 Goodbye!")
            break
        
        if not user_message:
            continue
        
        try:
            # Add message to thread
            message = client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message
            )
            
            # Run assistant
            print("\n🤔 Panelin is thinking...")
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )
            
            # Wait for completion
            import time
            while run.status in ["queued", "in_progress"]:
                time.sleep(1)
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            if run.status == "completed":
                # Get messages
                messages = client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                
                # Get the latest assistant message
                assistant_message = messages.data[0]
                if assistant_message.role == "assistant":
                    content = assistant_message.content[0].text.value
                    print(f"\nPanelin: {content}\n")
                else:
                    print("\n⚠️  No response from assistant\n")
            else:
                print(f"\n❌ Run failed with status: {run.status}\n")
                if run.last_error:
                    print(f"   Error: {run.last_error.message}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Chat with Panelin Assistant"
    )
    parser.add_argument(
        "--assistant-id",
        type=str,
        help="Assistant ID (or set in .panelin_assistant_id file)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (or set OPENAI_API_KEY env var)"
    )
    
    args = parser.parse_args()
    
    # Get API key
    from config.settings import settings
    api_key = args.api_key or settings.OPENAI_API_KEY
    if not api_key:
        print("❌ OpenAI API key required.")
        print("   Set OPENAI_API_KEY environment variable or use --api-key")
        sys.exit(1)
    
    client = OpenAI(api_key=api_key)
    
    # Get assistant ID
    assistant_id = get_assistant_id(args.assistant_id)
    
    # Start chat
    chat_with_panelin(client, assistant_id)


if __name__ == "__main__":
    main()
