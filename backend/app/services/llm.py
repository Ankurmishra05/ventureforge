import os
import time

import requests
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")
ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")

groq_client = Groq(api_key=groq_key) if groq_key else None

openrouter_client = OpenAI(
    api_key=openrouter_key,
    base_url="https://openrouter.ai/api/v1",
) if openrouter_key else None


def ask_groq(prompt, temperature=0.4):
    if not groq_client:
        raise Exception("Groq key missing")

    res = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an elite startup strategist."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return res.choices[0].message.content


def ask_openrouter(prompt, temperature=0.4):
    if not openrouter_client:
        raise Exception("OpenRouter key missing")

    res = openrouter_client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=[
            {"role": "system", "content": "You are an elite startup strategist."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return res.choices[0].message.content


def ask_ollama(prompt, temperature=0.4):
    r = requests.post(
        f"{ollama_url}/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
        },
        timeout=60,
    )
    return r.json()["response"]


def ask_llm_with_provider(prompt, temperature=0.4):
    providers = [
        ("Groq", ask_groq),
        ("OpenRouter", ask_openrouter),
        ("Ollama", ask_ollama),
    ]

    errors = []

    for name, fn in providers:
        for _attempt in range(2):
            try:
                output = fn(prompt, temperature)
                print(f"Success via {name}")
                return output, name
            except Exception as exc:
                errors.append(f"{name}: {str(exc)}")
                time.sleep(2)

    raise Exception("All providers failed -> " + " | ".join(errors))


def ask_llm(prompt, temperature=0.4):
    output, _provider = ask_llm_with_provider(prompt, temperature)
    return output
