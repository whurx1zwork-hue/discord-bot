from flask import Flask
from threading import Thread
import requests
import time
import os

app = Flask('')

@app.route('/')
def home():
    return "Discord Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    print("✅ Веб-сервер запущен для поддержания активности")
