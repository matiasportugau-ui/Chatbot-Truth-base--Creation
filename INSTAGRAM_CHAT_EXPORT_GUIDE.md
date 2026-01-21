# Instagram Chat Export Guide

This guide explains how to export all your Instagram chats using the `export_instagram_chats.py` script.

## Quick Start

### Method 1: Export from Instagram Data Download (Recommended)

This is the easiest and most reliable method for personal accounts.

#### Step 1: Download Your Instagram Data

1. Open Instagram on your phone or web browser
2. Go to **Settings** → **Privacy and Security** → **Download Your Information**
3. Select **Messages** (or select "Everything" for complete data)
4. Choose format: **JSON**
5. Click **Request Download**
6. Wait for Instagram to prepare your data (usually takes a few minutes to hours)
7. Download the ZIP file when ready

#### Step 2: Extract and Export

```bash
# Extract the downloaded ZIP file
unzip instagram-*.zip -d instagram_data

# Run the export script
python3 export_instagram_chats.py --method files --data-path instagram_data
```

The script will:
- ✅ Find all chat files in the Instagram data
- ✅ Parse messages from all conversations
- ✅ Export in multiple formats:
  - `instagram_chats_file_export_*.json` - All messages in JSON format
  - `instagram_chats_file_export_*.jsonl` - One message per line (JSONL)
  - `instagram_chats_by_thread_*.json` - Messages grouped by conversation
  - `export_summary_*.json` - Summary statistics

### Method 2: Export via Instagram Graph API

**Note:** This method requires:
- Instagram Business Account
- Instagram Graph API access
- Instagram Messaging API permissions (limited availability)

```bash
# Set environment variables
export INSTAGRAM_ACCESS_TOKEN="your_access_token"
export INSTAGRAM_BUSINESS_ACCOUNT_ID="your_business_account_id"

# Run export
python3 export_instagram_chats.py --method api
```

## Usage Examples

### Basic File Export
```bash
python3 export_instagram_chats.py --data-path ~/Downloads/instagram_data
```

### Custom Output Directory
```bash
python3 export_instagram_chats.py \
  --data-path instagram_data \
  --output-dir my_exported_chats
```

### Both Methods (API + Files)
```bash
python3 export_instagram_chats.py \
  --method both \
  --data-path instagram_data \
  --access-token $INSTAGRAM_ACCESS_TOKEN
```

## Output Format

### JSON Format
```json
[
  {
    "id": "message_id",
    "platform": "instagram",
    "type": "direct_message",
    "thread_title": "Conversation Name",
    "participants": ["User1", "User2"],
    "sender": "User1",
    "content": "Message text",
    "timestamp": "2024-01-20T10:30:00",
    "is_photo": false,
    "is_video": false,
    "metadata": {
      "is_question": true,
      "reactions": []
    }
  }
]
```

### Thread Grouping
Messages are automatically grouped by conversation thread, making it easy to see complete conversations.

## Troubleshooting

### "Messages folder not found"
- Make sure you extracted the ZIP file
- Check that the path contains a `messages/`, `direct_messages/`, or `inbox/` folder
- Instagram data structure may vary - check the folder structure manually

### "No chats found"
- Verify that you selected "Messages" when downloading your data
- Check that the JSON files contain message data
- Some Instagram data exports may use different folder structures

### API Method Not Working
- Instagram DMs via API require special permissions
- Most users should use the file-based export method instead
- Business accounts need Instagram Messaging API access

## Tips

1. **Complete Export**: Select "Everything" when downloading from Instagram to get all your data
2. **Regular Backups**: Export your chats periodically to maintain backups
3. **Privacy**: The exported files contain all your messages - keep them secure
4. **Large Exports**: For accounts with many messages, the export may take time to process

## File Locations

By default, exports are saved to `instagram_chats_export/` directory:
```
instagram_chats_export/
├── instagram_chats_file_export_20240120_103000.json
├── instagram_chats_file_export_20240120_103000.jsonl
├── instagram_chats_by_thread_file_export_20240120_103000.json
└── export_summary_file_export_20240120_103000.json
```

## Need Help?

If you encounter issues:
1. Check that your Instagram data download is complete
2. Verify the folder structure matches expected format
3. Check the script output for specific error messages
4. Ensure you have read permissions for the data folder
