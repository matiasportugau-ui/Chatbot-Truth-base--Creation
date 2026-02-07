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
import requests
from datetime import datetime

load_dotenv()

BACKEND_URL = os.getenv("PANELIN_BACKEND_URL", "http://localhost:8000")


def log_conversation_create(thread_id: str, assistant_id: str, user_name: str = None):
    """Log conversation creation to backend"""
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/conversations",
            json={
                "thread_id": thread_id,
                "assistant_id": assistant_id,
                "user_name": user_name,
                "user_type": "customer"
            },
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Warning: Failed to log conversation: {response.status_code}")
            return None
    except Exception as e:
        print(f"Warning: Failed to log conversation: {e}")
        return None


def log_message(conversation_id: str, message_id: str, thread_id: str, 
               role: str, content: str, created_at):
    """Log message to backend"""
    try:
        requests.post(
            f"{BACKEND_URL}/api/conversations/{conversation_id}/messages",
            json={
                "message_id": message_id,
                "thread_id": thread_id,
                "role": role,
                "content": content,
                "created_at": created_at.isoformat()
            },
            timeout=5
        )
    except Exception as e:
        print(f"Warning: Failed to log message: {e}")


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
    """Interactive chat with Panelin with conversation logging"""
    print("\n" + "=" * 60)
    print("💬 Chat with Panelin - BMC Assistant Pro")
    print("=" * 60)
    print("Type 'exit' or 'quit' to end the conversation\n")
    
    # Get user name for logging
    user_name = input("Your name (optional, for logging): ").strip() or None
    
    # Create a thread
    thread = client.beta.threads.create()
    print(f"✅ Thread created: {thread.id}\n")
    
    # Log conversation creation
    conversation = log_conversation_create(thread.id, assistant_id, user_name)
    conversation_id = conversation.get("id") if conversation else None
    
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
            
            # Log user message
            if conversation_id:
                log_message(
                    conversation_id, 
                    message.id, 
                    thread.id, 
                    "user", 
                    user_message,
                    datetime.now()
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
                    
                    # Log assistant message
                    if conversation_id:
                        log_message(
                            conversation_id,
                            assistant_message.id,
                            thread.id,
                            "assistant",
                            content,
                            datetime.now()
                        )
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
