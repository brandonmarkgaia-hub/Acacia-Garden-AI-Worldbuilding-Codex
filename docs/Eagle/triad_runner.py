import json, os, requests
from datetime import datetime

# Paths
JOB_PATH = "eagle/jobs/"
OUT_ENGINE = "eagle/outputs/"
OUT_CODex = "docs/Eagle/"

os.makedirs(OUT_ENGINE, exist_ok=True)
os.makedirs(OUT_CODex, exist_ok=True)

# API Keys
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")


# ---------------------------
# 🌬️ TRIAD LLM FUNCTIONS
# ---------------------------

def call_openai(prompt):
    """GPT-5 nano → Primary feather (Thought)"""
    try:
        if not OPENAI_KEY:
            return None, "No OpenAI key."

        headers = {"Authorization": f"Bearer {OPENAI_KEY}"}
        data = {
            "model": "gpt-5-nano",
            "input": prompt,
            "max_output_tokens": 200
        }

        r = requests.post(
            "https://api.openai.com/v1/responses",
            headers=headers, json=data
        )
        if r.status_code != 200:
            return None, f"OpenAI error: {r.text}"
        return r.json()["output_text"], None

    except Exception as e:
        return None, str(e)



def call_deepseek(prompt):
    """Shadow Feather → fallback"""
    try:
        if not DEEPSEEK_KEY:
            return None, "No DeepSeek key."

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }

        r = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers, json=payload
        )
        if r.status_code != 200:
            return None, f"DeepSeek error: {r.text}"

        return r.json()["choices"][0]["message"]["content"], None

    except Exception as e:
        return None, str(e)



def call_groq(prompt):
    """Speed Feather → Groq final fallback"""
    try:
        if not GROQ_KEY:
            return None, "No Groq key."

        headers = {
            "Authorization": f"Bearer {GROQ_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mixtral-8x7b-32768",
            "messages": [{"role": "user", "content": prompt}]
        }

        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload
        )
        if r.status_code != 200:
            return None, f"Groq error: {r.text}"

        return r.json()["choices"][0]["message"]["content"], None

    except Exception as e:
        return None, str(e)


# ---------------------------------------------------
# 🦅 TRIAD LOGIC — the Sky-Mind chooses the path
# ---------------------------------------------------

def run_job(job_file):
    with open(job_file, "r") as f:
        j = json.load(f)

    job_id = job_file.split("/")[-1].replace(".json", "")
    prompt = j["prompt"]

    # Try GPT-5 nano first
    ans, err = call_openai(prompt)
    source = "GPT-5-Nano 🟢"

    if not ans:
        ans, err = call_deepseek(prompt)
        source = "DeepSeek 🟡"

    if not ans:
        ans, err = call_groq(prompt)
        source = "Groq 🔵"

    if not ans:
        ans = "Triad exhausted. No feathers left to fly."
        source = "Sky-Mind ⚫"
    
    ts = datetime.utcnow().isoformat()

    md = f"""
# 🦅 TRIAD OUTPUT  
**Job:** {job_id}  
**Source:** {source}  
**Time:** {ts}  
**Prompt:**  
> {prompt}

---

# 🌬️ Response  
{ans}

---
*Auto-written by the Eagle Triad Engine.*
"""

    # Write to engine
    with open(f"{OUT_ENGINE}/{job_id}.md", "w") as f:
        f.write(md)

    # Also write to public Codex
    with open(f"{OUT_CODex}/{job_id}.md", "w") as f:
        f.write(md)

    return md



# ------------------------
# 🔥 RUN ALL JOB FILES
# ------------------------

jobs = [f for f in os.listdir(JOB_PATH) if f.endswith(".json")]

for job in jobs:
    print(f"Running: {job}")
    run_job(JOB_PATH + job)
