import os
from dotenv import load_dotenv

load_dotenv()

TEST_PROMPT = (
    "You are an assistive communication tool. "
    "A person using AAC wants to say something about being hungry. "
    "Complete this partial message in a clear, natural way: 'I want to eat...'"
)

def test_openai():
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": TEST_PROMPT}],
            max_tokens=200
        )
        print(" GPT-4 WORKING")
        print(f"   Output: {response.choices[0].message.content[:100]}\n")
    except Exception as e:
        print(f" GPT-4 FAILED: {e}\n")

def test_anthropic():
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=200,
            messages=[{"role": "user", "content": TEST_PROMPT}]
        )
        print(" CLAUDE WORKING")
        print(f"   Output: {response.content[0].text[:100]}\n")
    except Exception as e:
        print(f" CLAUDE FAILED: {e}\n")

def test_groq():
    try:
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": TEST_PROMPT}],
            max_tokens=200
        )
        print(" GROQ (Llama 3) WORKING")
        print(f"   Output: {response.choices[0].message.content[:100]}\n")
    except Exception as e:
        print(f" GROQ FAILED: {e}\n")
if __name__ == "__main__":
    print("  LLM AUDIT — API KEY TEST")
    test_openai()
    test_anthropic()
    test_groq()