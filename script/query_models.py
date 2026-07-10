import os
import time
import csv
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

os.makedirs("outputs", exist_ok=True)
logging.basicConfig(
    filename="outputs/run_log.txt",
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s"
)

from openai import OpenAI
import anthropic
from groq import Groq 
openai_client    = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
groq_client    = Groq(api_key=os.getenv("GOOGLE_API_KEY"))

def query_gpt4(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def query_claude(prompt):
    response = anthropic_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()
def query_groq(prompt):
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def run_audit():
    input_file  = "prompts/prompts.csv"
    output_file = "outputs/model_outputs.csv"

    fieldnames = [
        "prompt_id", "category", "disability_type", "task_type",
        "prompt_text", "notes",
        "gpt4_output",   "gpt4_error",
        "claude_output", "claude_error",
        "groq_output", "groq_error",
        "timestamp"
    ]

    with open(input_file, newline="", encoding="utf-8") as infile, \
         open(output_file, "w", newline="", encoding="utf-8") as outfile:

        reader = csv.DictReader(infile)
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        prompts = list(reader)
        total = len(prompts)
        print(f"\nStarting audit — {total} prompts x 3 models = {total * 3} API calls\n")

        for i, row in enumerate(prompts, start=1):
            pid    = row["prompt_id"]
            prompt = row["prompt_text"]
            print(f"[{i}/{total}] {pid} ...", end=" ", flush=True)

            result = {
                "prompt_id":       pid,
                "category":        row["category"],
                "disability_type": row["disability_type"],
                "task_type":       row["task_type"],
                "prompt_text":     prompt,
                "notes":           row["notes"],
                "gpt4_output":     "", "gpt4_error":    "",
                "claude_output":   "", "claude_error":  "",
                "groq_output":   "", "groq_error":  "",
                "timestamp":       datetime.utcnow().isoformat()
            }

            for label, fn in [("GPT4", query_gpt4),
                               ("Claude", query_claude),
                               ("Groq", query_groq)]:
                key = label.lower() + "_output"
                err = label.lower() + "_error"
                try:
                    result[key] = fn(prompt)
                    print(f"{label}", end=" ", flush=True)
                except Exception as e:
                    result[err] = str(e)
                    print(f"{label}", end=" ", flush=True)
                time.sleep(0.5)

            print()
            time.sleep(1.0)
            writer.writerow(result)
            outfile.flush()

    print(f"\nDone. Results saved to {output_file}")

if __name__ == "__main__":
    run_audit()