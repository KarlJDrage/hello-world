# Quick Start Guide: Voice Note to ClickUp SOP

This guide will help you get the proof-of-concept running in under 10 minutes.

## Prerequisites

1. **Python 3.11+** installed
2. **OpenAI API Key** ([get one here](https://platform.openai.com/api-keys))
3. **ClickUp API Key** ([get one here](https://app.clickup.com/settings/apps))
4. **ClickUp List ID** (where you want SOPs created)

### Finding Your ClickUp List ID

1. Open ClickUp and navigate to the List where you want SOPs
2. The URL will look like: `https://app.clickup.com/[workspace]/[space]/[list-id]`
3. The List ID is the number at the end (e.g., `123456789`)

Or use the ClickUp API:
```bash
curl https://api.clickup.com/api/v2/team \
  -H "Authorization: YOUR_CLICKUP_API_KEY"
```

## Installation

### 1. Clone/Download This Code

```bash
# If you have the code in a directory
cd /path/to/voice-to-sop

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up API Keys

**Option A - Environment Variables (Recommended):**
```bash
export OPENAI_API_KEY="sk-..."
export CLICKUP_API_KEY="pk_..."
```

**Option B - Pass as Arguments:**
```bash
# You'll add --openai-key and --clickup-key to commands below
```

## Usage

### Basic Command

```bash
python voice_to_sop.py \
  /path/to/your/recording.m4a \
  YOUR_CLICKUP_LIST_ID
```

### With Explicit API Keys

```bash
python voice_to_sop.py \
  /path/to/your/recording.m4a \
  YOUR_CLICKUP_LIST_ID \
  --openai-key sk-... \
  --clickup-key pk_...
```

### Example Output

```
============================================================
🎯 Starting Voice Note → ClickUp SOP Pipeline
============================================================

🎙️  Agent 1: Transcribing audio...
✅ Transcription complete: 2,458 characters
   💾 Saved transcript to: transcript.txt

🔍 Agent 2: Analyzing process structure...
✅ Process analyzed: 8 steps identified
   💾 Saved analysis to: analysis.json

📝 Agent 3: Formatting SOP...
✅ SOP formatted: 3,124 characters
   💾 Saved SOP to: sop.md

🚀 Agent 4: Publishing to ClickUp...
✅ SOP published to ClickUp: https://app.clickup.com/t/...

============================================================
✨ Pipeline Complete!
============================================================
📋 Title: Weekly Team Status Report Process
📊 Steps: 8
🔗 ClickUp URL: https://app.clickup.com/t/...

✅ Success! Check ClickUp for your new SOP.
```

## What Gets Created

The pipeline will create:

1. **transcript.txt** - Raw transcription with cleanup
2. **analysis.json** - Structured process data
3. **sop.md** - Formatted SOP document
4. **ClickUp Task** - Published SOP in your specified List

## Testing the Pipeline

### Record a Test Voice Note

Record yourself explaining a simple process. For example:

> "Hi, I'm going to explain our weekly status report process. 
> First, every Monday morning at 9am, the team lead opens the status report template in our shared drive.
> Then they review the previous week's action items to see what was completed.
> Next, they meet with each team member for 10 minutes to gather updates.
> After all meetings, they compile the updates into the template.
> Then they add any new action items for the upcoming week.
> Finally, they email the report to stakeholders by Monday 2pm.
> The report should include completed items, in-progress items, blockers, and next week's priorities."

Save this as an audio file (use your phone's voice recorder, or record in any audio app).

### Run the Pipeline

```bash
python voice_to_sop.py weekly_status.m4a YOUR_CLICKUP_LIST_ID
```

### Review the Output

1. Check the generated files (`transcript.txt`, `analysis.json`, `sop.md`)
2. Go to ClickUp and find your new SOP task
3. Review the formatting and accuracy

## Customizing the Pipeline

### Adjusting AI Prompts

The prompts for each agent are in the `voice_to_sop.py` file:

- **Line ~45-90**: Transcription (Agent 1)
- **Line ~92-158**: Process Analysis (Agent 2) - **Most important to customize**
- **Line ~160-230**: SOP Formatting (Agent 3) - **Second most important**
- **Line ~232-260**: ClickUp Publishing (Agent 4)

### Adding Custom SOP Templates

Edit the `format_sop()` method around line 190 to change the SOP structure:

```python
# Example: Add a "Tools Required" section
prompt = f"""...

## Tools & Resources
- Tool 1
- Tool 2

## Steps
...
"""
```

### Adding ClickUp Custom Fields

Edit the `publish_to_clickup()` method around line 250:

```python
json={
    "name": title,
    "description": sop_document,
    "custom_fields": [
        {
            "id": "your-custom-field-id",
            "value": "some-value"
        }
    ],
    "tags": ["SOP", "AI-Generated", "Your-Custom-Tag"],
}
```

## Troubleshooting

### "Transcription failed"
- Check your OpenAI API key is valid
- Ensure audio file format is supported (mp3, m4a, wav, etc.)
- Check audio file isn't corrupted

### "Process analysis failed"
- Check your OpenAI API key has credits
- Try with a shorter/clearer recording
- Check the response from OpenAI in error message

### "ClickUp publishing failed"
- Verify your ClickUp API key is valid
- Check the List ID is correct
- Ensure you have permission to create tasks in that List

### Audio file not supported
Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm

Convert unsupported formats:
```bash
# Using ffmpeg (install: brew install ffmpeg)
ffmpeg -i input.ogg output.mp3
```

## Cost Estimation

For a **10-minute voice recording**:
- Transcription (Whisper): ~$0.06
- GPT-4 processing (3 calls): ~$0.15-0.30
- **Total: ~$0.21-0.36 per SOP**

Monthly estimate (50 SOPs): ~$10-18

## Next Steps

Once you've tested this POC and it works for your needs:

1. **Build a Web Interface**: Use Streamlit or React for easier recording/uploading
2. **Add Batch Processing**: Upload multiple recordings at once
3. **Create Template Library**: Different SOP types (technical, operational, etc.)
4. **Add Video Integration**: Auto-attach Loom/screen recordings
5. **Implement Review Workflow**: Multi-step approval process
6. **Add Analytics**: Track SOP usage and effectiveness

## Need Help?

Common issues and solutions:

**Q: Can I use this with recorded phone calls?**
A: Yes! Just export the audio from your phone and upload it.

**Q: Does this work with other languages?**
A: Yes, Whisper supports 50+ languages. Just speak in your language.

**Q: Can I integrate with tools other than ClickUp?**
A: Absolutely! Replace the `publish_to_clickup()` method with any API (Notion, Confluence, etc.)

**Q: How accurate is the SOP generation?**
A: Depends on how clear your voice recording is. The clearer and more structured your explanation, the better the output.

**Q: Can I edit the SOP before publishing?**
A: Currently it publishes automatically. To add a review step, remove the `publish_to_clickup()` call and manually review `sop.md` before publishing.

## Advanced: Adding a Review Step

If you want to review before publishing:

```bash
# Run without publishing
python voice_to_sop.py recording.m4a YOUR_LIST_ID --no-publish

# Review the generated sop.md file
cat sop.md

# If happy, publish manually
python -c "
from voice_to_sop import VoiceToSOPPipeline
import os

pipeline = VoiceToSOPPipeline(
    os.getenv('OPENAI_API_KEY'),
    os.getenv('CLICKUP_API_KEY')
)

with open('sop.md', 'r') as f:
    sop = f.read()

pipeline.publish_to_clickup(sop, 'YOUR_LIST_ID', 'Your SOP Title')
"
```

---

🎉 **That's it! You're ready to start converting voice notes to SOPs.**

Feel free to modify the code to fit your exact needs. The pipeline is designed to be modular and easy to customize.
