import os
import requests

print('Testing Cloudflare Workers AI...')
ACCOUNT_ID = input('Masukkan Cloudflare Account ID Anda: ').strip()
API_TOKEN = input('Masukkan Cloudflare API Token Anda: ').strip()

if not ACCOUNT_ID or not API_TOKEN:
    print('Kredensial kosong.')
    exit(1)

model = '@cf/black-forest-labs/flux-1-schnell'
url = f'https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/{model}'

payload = {
    'prompt': 'Tuliskan 1 ide video',  # Not really for LLM, but just testing connection. Wait, this is image generation!
    # Let's write a proper prompt.
    'prompt': 'A cute cat with sunglasses relaxing on the beach, watercolor style'
}

headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}

print(f'\nMencoba generate gambar dengan {model}...')
resp = requests.post(url, headers=headers, json=payload, timeout=60)

if resp.status_code == 200:
    print('BERHASIL! Mendapatkan respons 200 OK.')
    content_type = resp.headers.get('Content-Type', '')
    
    if 'image/' in content_type:
        with open('test_output.png', 'wb') as f:
            f.write(resp.content)
        print('Gambar berhasil disimpan sebagai test_output.png (berupa binary/bytes).')
    else:
        try:
            data = resp.json()
            if data.get('success'):
                import base64
                if isinstance(data.get('result'), dict) and 'image' in data['result']:
                    image_data = data['result']['image']
                    with open('test_output.png', 'wb') as f:
                        f.write(base64.b64decode(image_data))
                    print('Gambar berhasil disimpan sebagai test_output.png (berupa JSON Base64).')
                else:
                    print('Struktur JSON tidak dikenali:', data)
            else:
                print('Gagal menghasilkan gambar (success: false):', data)
        except Exception as e:
            print('Gagal memproses JSON:', e)
            print('Respons mentah (sebagian):', resp.content[:200])
else:
    print(f'GAGAL: {resp.status_code}')
    print(resp.text[:500])
