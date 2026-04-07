from flask import Flask, render_template_string, send_file
import qrcode, io, json, random
from datetime import datetime

app = Flask(__name__)

# ---------------- STATE ----------------
state = {
    "screen": "WELCOME",   # WELCOME | DETECTING | RESULT
    "capacity": 0,
    "credits": 0,
    "txn_id": ""
}

# ---------------- COMMON CSS ----------------
CSS = """
<style>
body{
  margin:0;
  font-family:Arial;
  -webkit-user-select:none;
  -moz-user-select:none;
  -ms-user-select:none;
  user-select:none;
  -webkit-touch-callout:none;
}
.stack{width:100vw;height:100vh;display:flex;justify-content:center;align-items:center;}
.vbox{display:flex;flex-direction:column;align-items:center;text-align:center;}
.dark{background:#020617;color:white;}
.light{background:white;color:#111;}
.title{font-size:36px;font-weight:bold;}
.subtitle{font-size:24px;color:#ccc;}
.btn{font-size:30px;padding:15px 50px;border:none;border-radius:10px;background:#22c55e;}
.spinner{width:50px;height:50px;border:6px solid #ccc;border-top:6px solid #22c55e;border-radius:50%;animation:spin 1s linear infinite;}
@keyframes spin{100%{transform:rotate(360deg)}}
</style>
"""

# ---------------- HIDDEN ADMIN + LOCK JS ----------------
ADMIN_JS = """
<script>
let taps = 0;
let lastTap = 0;

function handleTap(x, y) {
  const now = Date.now();

  // top-left 50x50 px hidden zone
  if (x < 50 && y < 50) {
    if (now - lastTap < 400) taps++;
    else taps = 1;

    lastTap = now;

    if (taps >= 7) {
      window.location.href = "/admin";
    }
  }
}

// Touch support
document.addEventListener("touchstart", e => {
  const t = e.touches[0];
  handleTap(t.clientX, t.clientY);
});

// Mouse support
document.addEventListener("mousedown", e => {
  handleTap(e.clientX, e.clientY);
});

// Disable selection & interaction
document.addEventListener("selectstart", e => e.preventDefault());
document.addEventListener("dragstart", e => e.preventDefault());
document.addEventListener("contextmenu", e => e.preventDefault());
</script>
"""

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template_string(f"""
    <html>
    <head>{CSS}</head>
    <body class="dark">
      <div class="stack">
        <div class="vbox">
          <div class="title">Reverse Vending Machine</div>
          <div class="subtitle">Smart Recycling System</div><br>
          <button class="btn" onclick="start()">START</button>
        </div>
      </div>

      <script>
        function start() {{
          fetch('/start').then(() => location.href='/detect');
        }}
      </script>
      {ADMIN_JS}
    </body>
    </html>
    """)

# ---------------- START ----------------
@app.route("/start")
def start():
    state["screen"] = "DETECTING"
    return "OK"

# ---------------- DETECT ----------------
@app.route("/detect")
def detect():
    return render_template_string(f"""
    <html>
    <head>{CSS}</head>
    <body class="light">
      <div class="stack">
        <div class="vbox">
          <div class="title">Detecting Bottle...</div><br>
          <div class="spinner"></div>
        </div>
      </div>

      <script>
        setTimeout(() => {{
          fetch('/process').then(() => location.href='/result');
        }}, 3000);
      </script>
      {ADMIN_JS}
    </body>
    </html>
    """)

# ---------------- PROCESS (SIMULATED SENSOR) ----------------
@app.route("/process")
def process():
    state["capacity"] = random.choice([250, 500, 1000])
    state["credits"] = state["capacity"] // 50
    state["txn_id"] = f"TXN{random.randint(100000,999999)}"
    state["screen"] = "RESULT"
    return "OK"

# ---------------- QR ----------------
@app.route("/qr")
def qr():
    payload = {
        "machine_id": "RVM_001",
        "capacity_ml": state["capacity"],
        "credits": state["credits"],
        "txn_id": state["txn_id"],
        "time": datetime.now().isoformat()
    }
    img = qrcode.make(json.dumps(payload))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

# ---------------- RESULT ----------------
@app.route("/result")
def result():
    return render_template_string(f"""
    <html>
    <head>{CSS}</head>
    <body class="light">
      <div class="stack">
        <div class="vbox">
          <div class="title">Bottle Accepted</div><br>
          <div>Capacity: {state["capacity"]} ml</div>
          <div>Credits: ₹{state["credits"]}</div><br>
          <img src="/qr" width="200"><br><br>
          <button class="btn" onclick="reset()">Finish</button>
        </div>
      </div>

      <script>
        function reset() {{
          fetch('/reset').then(() => location.href='/');
        }}
        setTimeout(reset, 10000);
      </script>
      {ADMIN_JS}
    </body>
    </html>
    """)

# ---------------- RESET ----------------
@app.route("/reset")
def reset():
    state["screen"] = "WELCOME"
    return "OK"

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    return """
    <html>
    <body style="background:black;color:white;text-align:center;font-family:Arial;margin-top:100px;">
        <h1>ADMIN MODE</h1>
        <p>Maintenance access</p>
        <button onclick="window.location.href='/'"
                style="font-size:24px;padding:20px 40px;">
            Exit to Home
        </button>
    </body>
    </html>
    """

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
