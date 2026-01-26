# Backup Files - Original Versions Before Merge Resolution

**Created:** 2026-01-25 22:46:07

This directory contains backup copies of the original conflicted versions before the merge resolution.

## Files Backed Up

### Home.md
- **`Home.md.ORIGINAL_HEAD_20260125_224607`** - Original HEAD version (Spanish, with quick start references)
- **`Home.md.ORIGINAL_INCOMING_20260125_224607`** - Original incoming version (English, comprehensive documentation)

### _Sidebar.md
- **`_Sidebar.md.ORIGINAL_HEAD_20260125_224607`** - Original HEAD version (old structure with repo docs section)
- **`_Sidebar.md.ORIGINAL_INCOMING_20260125_224607`** - Original incoming version (new organized structure)

## Current Merged Version

The current files (`Home.md` and `_Sidebar.md`) are the **merged versions** that combine:
- The comprehensive English documentation from incoming
- The quick setup guide references from HEAD
- Proper formatting and structure

## How to Restore

If you need to restore any of these versions:

```bash
# Restore HEAD version of Home.md
cp wiki/.backups/Home.md.ORIGINAL_HEAD_20260125_224607 wiki/Home.md

# Restore incoming version of Home.md
cp wiki/.backups/Home.md.ORIGINAL_INCOMING_20260125_224607 wiki/Home.md

# Restore HEAD version of _Sidebar.md
cp wiki/.backups/_Sidebar.md.ORIGINAL_HEAD_20260125_224607 wiki/_Sidebar.md

# Restore incoming version of _Sidebar.md
cp wiki/.backups/_Sidebar.md.ORIGINAL_INCOMING_20260125_224607 wiki/_Sidebar.md
```

## What Was Merged

The final merged version includes:
- ✅ Full English documentation (from incoming)
- ✅ Quick Setup Guides section with file references (from HEAD)
- ✅ All navigation links (from incoming)
- ✅ Proper GitHub wiki formatting
- ✅ No conflict markers
