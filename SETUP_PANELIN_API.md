# Setup Panelin with Specific Model via API

This guide shows you how to create Panelin using the OpenAI API, which allows you to specify the exact model you want (bypassing the GPT Builder limitation).

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install openai python-dotenv
```

### 2. Get Your API Key

1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy it

### 3. Set Up Environment

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

Or export it:

```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

### 4. Run the Setup Script

```bash
# Basic usage (uses GPT-4)
python setup_panelin_with_model.py

# Specify a different model
python setup_panelin_with_model.py --model gpt-4-turbo

# With knowledge base files
python setup_panelin_with_model.py --model gpt-4 --knowledge-base "BMC_Base_Conocimiento_GPT.json" "BMC_Base_Unificada_v4.json"

# With web search enabled
python setup_panelin_with_model.py --model gpt-4 --enable-web-search
```

## 📋 Available Models

- `gpt-4` - Recommended for best accuracy
- `gpt-4-turbo` - Faster, good quality
- `gpt-4o` - Latest version, best performance
- `gpt-4o-mini` - Smaller, faster, cheaper
- `gpt-3.5-turbo` - Cheaper, less powerful
- `o1-preview` - Reasoning model (if available)
- `o1-mini` - Smaller reasoning model

## 💬 Chat with Panelin

After creating the assistant, you can chat with it:

```bash
python chat_with_panelin.py
```

The assistant ID will be saved in `.panelin_assistant_id` automatically.

## 🔧 Advanced Usage

### Create Assistant with All Features

```bash
python setup_panelin_with_model.py \
  --model gpt-4 \
  --knowledge-base \
    "BMC_Base_Conocimiento_GPT.json" \
    "BMC_Base_Unificada_v4.json" \
    "BMC_Catalogo_Completo_Shopify (1).json" \
    "panelin_truth_bmcuruguay_web_only_v2.json" \
    "panelin_context_consolidacion_sin_backend.md" \
  --enable-web-search
```

### Use in Your Own Code

```python
from openai import OpenAI

client = OpenAI(api_key="your-api-key")
assistant_id = "asst_xxxxx"  # From setup script

# Create a thread
thread = client.beta.threads.create()

# Send a message
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Hola, necesito cotizar ISODEC 100mm para 5m de luz"
)

# Run the assistant
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

# Get response
if run.status == "completed":
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    response = messages.data[0].content[0].text.value
    print(response)
```

## 📊 Comparison: GPT Builder vs API

| Feature | GPT Builder | API (This Script) |
|---------|-------------|-------------------|
| Model Selection | Limited (AUTO only on Free) | ✅ Full control |
| Knowledge Base | Manual upload | ✅ Programmatic |
| Code Interpreter | ✅ Yes | ✅ Yes |
| Web Search | ✅ Yes | ✅ Yes |
| Automation | ❌ Manual | ✅ Scriptable |
| Version Control | ❌ No | ✅ Yes (code) |

## ⚠️ Important Notes

1. **API Costs**: Using the API directly incurs costs per token. Check [OpenAI Pricing](https://openai.com/pricing)

2. **Model Availability**: Not all models are available for all accounts. If you get an error, try a different model.

3. **Knowledge Base Files**: Files uploaded via API are stored by OpenAI and count towards your file storage limits.

4. **Thread Management**: Each conversation uses a "thread". Threads persist until you delete them.

## 🆘 Troubleshooting

### "Model not found" error
- Try a different model (e.g., `gpt-4-turbo` instead of `gpt-4`)
- Check your API account has access to that model

### "API key invalid" error
- Verify your API key is correct
- Check it's set in `.env` or environment variable
- Make sure you have credits in your OpenAI account

### Files not uploading
- Check file paths are correct
- Ensure files are not too large (OpenAI has size limits)
- Try uploading files one at a time

## 📚 Next Steps

1. ✅ Create your assistant with the script
2. ✅ Test it with `chat_with_panelin.py`
3. ✅ Integrate into your application
4. ✅ Monitor usage and costs

## 🔗 Resources

- [OpenAI Assistants API Docs](https://platform.openai.com/docs/assistants/overview)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [OpenAI Pricing](https://openai.com/pricing)
