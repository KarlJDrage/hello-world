#!/usr/bin/env python3
"""
Voice Note to ClickUp SOP - Proof of Concept
A simple CLI tool demonstrating the multi-agent pipeline
"""

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import requests


@dataclass
class ProcessStep:
    """Represents a single step in a process"""
    step_number: int
    action: str
    role: Optional[str] = None
    tools: List[str] = None
    estimated_time: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class SOP:
    """Represents a complete SOP"""
    title: str
    purpose: str
    owner: str
    steps: List[ProcessStep]
    prerequisites: List[str]
    success_criteria: List[str]
    common_pitfalls: List[str]


class VoiceToSOPPipeline:
    """Main pipeline orchestrating the multi-agent workflow"""
    
    def __init__(self, openai_api_key: str, clickup_api_key: str):
        self.openai_api_key = openai_api_key
        self.clickup_api_key = clickup_api_key
        self.openai_base_url = "https://api.openai.com/v1"
        
    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Agent 1: Transcribe audio file to text using OpenAI Whisper
        """
        print("🎙️  Agent 1: Transcribing audio...")
        
        with open(audio_file_path, 'rb') as audio_file:
            response = requests.post(
                f"{self.openai_base_url}/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                files={"file": audio_file},
                data={"model": "whisper-1"}
            )
        
        if response.status_code != 200:
            raise Exception(f"Transcription failed: {response.text}")
        
        transcript = response.json()['text']
        print(f"✅ Transcription complete: {len(transcript)} characters")
        return transcript
    
    def analyze_process(self, transcript: str) -> Dict:
        """
        Agent 2: Analyze transcript to extract process structure
        """
        print("🔍 Agent 2: Analyzing process structure...")
        
        prompt = f"""You are a process analysis expert. Analyze this voice transcript of someone explaining a process.

Extract and structure the following information:

1. Process Title (short, descriptive)
2. Purpose (why this process exists)
3. Owner/Role (who is responsible)
4. Prerequisites (what's needed before starting)
5. Steps (break down into clear, actionable steps with:
   - Step number
   - Action (what to do)
   - Role (who does it, if mentioned)
   - Tools/systems (if mentioned)
   - Estimated time (if mentioned)
   - Any notes or details
6. Success Criteria (how to know it's done correctly)
7. Common Pitfalls (potential issues or mistakes)

Return ONLY valid JSON in this exact format:
{{
    "title": "string",
    "purpose": "string",
    "owner": "string",
    "prerequisites": ["string"],
    "steps": [
        {{
            "step_number": 1,
            "action": "string",
            "role": "string or null",
            "tools": ["string"],
            "estimated_time": "string or null",
            "notes": "string or null"
        }}
    ],
    "success_criteria": ["string"],
    "common_pitfalls": ["string"]
}}

Transcript:
{transcript}
"""
        
        response = requests.post(
            f"{self.openai_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Process analysis failed: {response.text}")
        
        analysis = json.loads(response.json()['choices'][0]['message']['content'])
        print(f"✅ Process analyzed: {len(analysis['steps'])} steps identified")
        return analysis
    
    def format_sop(self, analysis: Dict) -> str:
        """
        Agent 3: Format the analyzed process into a structured SOP
        """
        print("📝 Agent 3: Formatting SOP...")
        
        prompt = f"""You are an SOP (Standard Operating Procedure) documentation expert.

Take this structured process data and format it into a professional, clear, and actionable SOP document.

Use this format (ClickUp markdown compatible):

# [Title]

## Purpose
[Clear explanation of why this process exists]

## Owner
[Who is responsible]

## Prerequisites
- List prerequisites
- One per line

## Steps

### 1. [Step Title]
**Action:** [What to do]
**Role:** [Who does it]
**Tools:** [Systems/tools needed]
**Time:** [Estimated duration]
**Notes:** [Additional context]

[Continue for all steps...]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Common Pitfalls & Troubleshooting
- **Issue:** [Problem] → **Solution:** [How to fix]

## Version History
- v1.0 - Initial creation - [Date]

---

Process data:
{json.dumps(analysis, indent=2)}
"""
        
        response = requests.post(
            f"{self.openai_base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"SOP formatting failed: {response.text}")
        
        sop_document = response.json()['choices'][0]['message']['content']
        print(f"✅ SOP formatted: {len(sop_document)} characters")
        return sop_document
    
    def publish_to_clickup(
        self, 
        sop_document: str, 
        list_id: str,
        title: str
    ) -> Dict:
        """
        Agent 4: Publish the formatted SOP to ClickUp
        """
        print("🚀 Agent 4: Publishing to ClickUp...")
        
        response = requests.post(
            f"https://api.clickup.com/api/v2/list/{list_id}/task",
            headers={
                "Authorization": self.clickup_api_key,
                "Content-Type": "application/json"
            },
            json={
                "name": title,
                "description": sop_document,
                "markdown_description": sop_document,
                "tags": ["SOP", "AI-Generated"],
            }
        )
        
        if response.status_code not in [200, 201]:
            raise Exception(f"ClickUp publishing failed: {response.text}")
        
        task_data = response.json()
        task_url = task_data['url']
        print(f"✅ SOP published to ClickUp: {task_url}")
        return task_data
    
    def process_voice_note(
        self, 
        audio_file_path: str, 
        clickup_list_id: str,
        save_intermediate: bool = True
    ) -> Dict:
        """
        Main workflow: Process a voice note end-to-end
        """
        print("\n" + "="*60)
        print("🎯 Starting Voice Note → ClickUp SOP Pipeline")
        print("="*60 + "\n")
        
        # Step 1: Transcribe
        transcript = self.transcribe_audio(audio_file_path)
        if save_intermediate:
            with open('transcript.txt', 'w') as f:
                f.write(transcript)
            print("   💾 Saved transcript to: transcript.txt")
        
        # Step 2: Analyze
        analysis = self.analyze_process(transcript)
        if save_intermediate:
            with open('analysis.json', 'w') as f:
                json.dump(analysis, f, indent=2)
            print("   💾 Saved analysis to: analysis.json")
        
        # Step 3: Format
        sop_document = self.format_sop(analysis)
        if save_intermediate:
            with open('sop.md', 'w') as f:
                f.write(sop_document)
            print("   💾 Saved SOP to: sop.md")
        
        # Step 4: Publish
        task_data = self.publish_to_clickup(
            sop_document, 
            clickup_list_id,
            analysis['title']
        )
        
        print("\n" + "="*60)
        print("✨ Pipeline Complete!")
        print("="*60)
        print(f"📋 Title: {analysis['title']}")
        print(f"📊 Steps: {len(analysis['steps'])}")
        print(f"🔗 ClickUp URL: {task_data['url']}")
        print("\n")
        
        return {
            'transcript': transcript,
            'analysis': analysis,
            'sop_document': sop_document,
            'clickup_task': task_data
        }


def main():
    """Example usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Convert voice notes to ClickUp SOPs"
    )
    parser.add_argument(
        'audio_file',
        help='Path to audio file (mp3, mp4, mpeg, mpga, m4a, wav, or webm)'
    )
    parser.add_argument(
        'clickup_list_id',
        help='ClickUp List ID where SOP should be created'
    )
    parser.add_argument(
        '--openai-key',
        default=os.getenv('OPENAI_API_KEY'),
        help='OpenAI API key (or set OPENAI_API_KEY env var)'
    )
    parser.add_argument(
        '--clickup-key',
        default=os.getenv('CLICKUP_API_KEY'),
        help='ClickUp API key (or set CLICKUP_API_KEY env var)'
    )
    
    args = parser.parse_args()
    
    if not args.openai_key:
        print("❌ Error: OpenAI API key required")
        print("   Set OPENAI_API_KEY environment variable or use --openai-key")
        return
    
    if not args.clickup_key:
        print("❌ Error: ClickUp API key required")
        print("   Set CLICKUP_API_KEY environment variable or use --clickup-key")
        return
    
    # Initialize pipeline
    pipeline = VoiceToSOPPipeline(
        openai_api_key=args.openai_key,
        clickup_api_key=args.clickup_key
    )
    
    # Process the voice note
    try:
        result = pipeline.process_voice_note(
            audio_file_path=args.audio_file,
            clickup_list_id=args.clickup_list_id,
            save_intermediate=True
        )
    except Exception as e:
        print(f"\n❌ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print("✅ Success! Check ClickUp for your new SOP.")


if __name__ == "__main__":
    main()
