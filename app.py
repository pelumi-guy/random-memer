#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Author  : Tushar Mittal (chiragmittal.mittal@gmail.com)
Flask API to return random meme images
"""

import random
import requests
from bs4 import BeautifulSoup
from flask import Flask, send_file
from PIL import Image
from io import BytesIO

app = Flask(__name__)

def get_new_memes():
    """Scrapes the website and extracts image URLs

    Returns:
        imgs [list]: List of image URLs
    """
    url = 'https://www.memedroid.com/memes/tag/programming'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(response.content, 'lxml')
    imgs = []
    for img_tag in soup.find_all('img', class_='img-responsive'):
        src = img_tag.get('src')
        if src and src.startswith('http') and (src.endswith('.jpeg') or src.endswith('.jpg') or src.endswith('.png') or src.endswith('.webp')):
            imgs.append(src)
    return imgs


def serve_pil_image(pil_img):
    """Stores the downloaded image file in-memory
    and sends it as response

    Args:
        pil_img: Pillow Image object

    Returns:
        [response]: Sends image file as response
    """
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

@app.after_request
def set_response_headers(response):
    """Sets Cache-Control header to no-cache so GitHub
    fetches new image everytime
    """
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route("/health", methods=['GET'])
def health_check():
    return "OK", 200

@app.route("/", methods=['GET'])
def return_meme():
    memes = get_new_memes()
    if not memes:
        return "No memes found. Please check your network connection or try again later.", 503
    img_url = random.choice(memes)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        res = requests.get(img_url, headers=headers, stream=True, timeout=10)
        res.raise_for_status()
        res.raw.decode_content = True
        img = Image.open(res.raw)
        return serve_pil_image(img)
    except Exception as e:
        return f"Failed to load meme image: {str(e)}", 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

