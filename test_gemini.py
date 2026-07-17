import requests
import json
import os

print('Testing Gemini API (gemini-2.5-flash)...')
API_KEY = input('Masukkan API Key Gemini Anda: ').strip()

if not API_KEY:
    print('API Key kosong.')
    exit(1)

print('\n[1] Mencoba generateContent dengan gemini-2.5-flash...')
url_gen = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}'

# Format request sesuai dengan yang kita tulis di script.py
payload = {
    'contents': [{'role': 'user', 'parts': [{'text': 'Berikan 1 ide video YouTube singkat tentang AI dalam format JSON dengan key "judul" dan "ide".'}]}],
    'generationConfig': {
        'maxOutputTokens': 8192,
        'responseMimeType': 'application/json'
    }
}

resp = requests.post(url_gen, json=payload, headers={'Content-Type': 'application/json'})
if resp.status_code == 200:
    print('BERHASIL!')
    result_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
    print('\nHasil Respons JSON dari Google:')
    print(result_text)
else:
    print(f'GAGAL: {resp.status_code} {resp.text}')
