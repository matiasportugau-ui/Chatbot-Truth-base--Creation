# Setup Instructions - Panelin with Specific Model

## ⚠️ Current Status

The script is ready to run, but you need a valid OpenAI API key.

## 🔑 Step 1: Get Your API Key

1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Copy the key (it starts with `sk-`)

## 🔧 Step 2: Set Your API Key

### Option A: Environment Variable (Recommended)
```bash
export OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Option B: Create .env File
Create a file named `.env` in this directory:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## 🚀 Step 3: Run the Setup

### Basic Setup (No Knowledge Base Files)
```bash
python3 setup_panelin_with_model.py --model gpt-4
```

### With Knowledge Base Files
```bash
python3 setup_panelin_with_model.py \
  --model gpt-4 \
  --knowledge-base \
    "BMC_Base_Conocimiento_GPT-2.json" \
    "BMC_Catalogo_Completo_Shopify (1).json" \
    "panelin_context_consolidacion_sin_backend.md" \
  --enable-web-search
```

### Available Models
- `gpt-4` - Best accuracy (recommended)
- `gpt-4-turbo` - Faster
- `gpt-4o` - Latest, best performance
- `gpt-4o-mini` - Smaller, cheaper
- `gpt-3.5-turbo` - Cheapest option

## ✅ What the Script Does

1. ✅ Creates a Panelin assistant with your chosen model (NOT AUTO!)
2. ✅ Uploads knowledge base files (if provided)
3. ✅ Configures code interpreter and web search
4. ✅ Saves assistant ID to `.panelin_assistant_id`

## 💬 After Setup: Chat with Panelin

```bash
python3 chat_with_panelin.py
```

## 🆘 Troubleshooting

### "Incorrect API key" error
- Verify your API key is correct
- Make sure it starts with `sk-`
- Check you have credits in your OpenAI account
- Try creating a new API key

### "Model not found" error
- Try a different model (e.g., `gpt-4-turbo`)
- Check your account has access to that model
- Some models require specific subscription tiers

### Files not uploading
- Check file paths are correct
- Ensure files aren't too large
- Verify API key has proper permissions

## 📝 Notes

- The assistant will be created with the exact model you specify
- Files are uploaded to OpenAI's servers
- Each API call incurs costs (check OpenAI pricing)
- The assistant ID is saved for reuse
