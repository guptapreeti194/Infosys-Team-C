import requests

url = "http://localhost:11434/api/generate"
data = {
    "model": "llama3:latest",   # ✅ use the model you have installed
    "prompt": "What is the capital of France?",
    "stream": False
}

response = requests.post(url, json=data)
print(response.json().get("response", response.json()))
