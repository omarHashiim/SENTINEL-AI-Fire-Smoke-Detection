from __future__ import annotations

import time
import base64
import csv
import io
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st
from PIL import Image, ImageDraw

try:
    import cv2
except Exception:
    cv2 = None

# Optional: the app can start without Ultralytics installed.
try:
    from ultralytics import YOLO
except Exception:
    YOLO = None


# ---------------------------------------------------------------------
# App configuration + visual design
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Sentinel AI | Detection Console",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "SENTINEL"
APP_SUBTITLE = "INTELLIGENT DETECTION CONSOLE"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #090d14;
        --panel: #101722;
        --panel2: #141e2c;
        --line: rgba(151, 174, 204, .15);
        --muted: #8b9ab0;
        --text: #edf4ff;
        --cyan: #5eead4;
        --blue: #7aa7ff;
        --orange: #ffb86b;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 75% -15%, rgba(48, 91, 154, .20), transparent 42%),
            radial-gradient(ellipse at 0% 35%, rgba(20, 184, 166, .06), transparent 35%),
            var(--bg);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }
    [data-testid="stHeader"] { background: rgba(9,13,20,.75); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e1520 0%, #0a1018 100%);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div { padding-top: 1.4rem; }
    h1, h2, h3, p, label { color: var(--text); }
    h1 { letter-spacing: -1.6px; font-weight: 800 !important; }
    h2, h3 { letter-spacing: -.4px; }
    .block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1600px; }
    .brand {
        display:flex; align-items:center; gap:12px; padding: 8px 2px 24px;
        border-bottom: 1px solid var(--line); margin-bottom: 24px;
    }
    .brand-mark {
        width:44px; height:44px; display:flex; align-items:center; justify-content:center;
        border-radius:14px; font-size:23px; font-weight:800; color:#07111a;
        background:linear-gradient(135deg, var(--cyan), var(--blue));
        box-shadow: 0 0 28px rgba(94,234,212,.18);
    }
    .brand-name { font-weight:800; font-size:17px; letter-spacing:2px; }
    .brand-sub { color:var(--muted); font-size:9px; letter-spacing:1.8px; margin-top:4px; }
    .eyebrow { color:var(--cyan); font-family:'DM Mono', monospace; font-size:11px; letter-spacing:2px; }
    .hero-title { font-size:clamp(30px, 3.6vw, 48px); line-height:1.08; font-weight:800; letter-spacing:-1.8px; margin:8px 0 10px; }
    .hero-copy { color:var(--muted); font-size:14px; line-height:1.7; max-width:720px; }
    .pill {
        display:inline-flex; align-items:center; gap:7px; padding:7px 10px;
        border:1px solid rgba(94,234,212,.25); border-radius:999px;
        color:var(--cyan); background:rgba(94,234,212,.07);
        font:11px 'DM Mono', monospace; letter-spacing:.5px;
    }
    .dot { width:7px; height:7px; border-radius:50%; background:var(--cyan); display:inline-block; box-shadow:0 0 10px var(--cyan); }
    .section-label { color:#9eacc0; font:11px 'DM Mono', monospace; letter-spacing:1.8px; text-transform:uppercase; margin:8px 0 13px; }
    .metric {
        background:linear-gradient(145deg, rgba(21,31,46,.95), rgba(13,20,30,.95));
        border:1px solid var(--line); border-radius:16px; padding:18px 18px 16px;
        min-height:124px; position:relative; overflow:hidden;
    }
    .metric:after { content:''; position:absolute; top:0; left:0; width:42px; height:2px; background:var(--cyan); }
    .metric-label { color:var(--muted); font-size:11px; letter-spacing:1.2px; text-transform:uppercase; }
    .metric-value { color:var(--text); font-size:29px; font-weight:800; letter-spacing:-1px; margin:10px 0 4px; }
    .metric-note { color:#6e819a; font-size:11px; }
    .panel {
        background:rgba(15,23,34,.82); border:1px solid var(--line);
        border-radius:12px; padding:15px; height:100%;
    }
    .panel-title { font-size:15px; font-weight:700; margin-bottom:5px; }
    .panel-sub { font-size:12px; color:var(--muted); margin-bottom:16px; }
    .drop-hint {
        border:1px dashed rgba(122,167,255,.4); border-radius:14px; padding:22px;
        background:rgba(122,167,255,.04); text-align:center; color:var(--muted);
    }
    .stButton > button, .stDownloadButton > button {
        border-radius:10px; border:1px solid rgba(94,234,212,.32);
        background:linear-gradient(135deg, #5eead4, #8bb5ff); color:#07111a;
        font-weight:800; min-height:42px; transition:all .2s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color:var(--cyan); box-shadow:0 0 22px rgba(94,234,212,.14); color:#07111a;
    }
    div[data-testid="stFileUploader"] {
        background:rgba(122,167,255,.035); border:1px dashed rgba(122,167,255,.25);
        border-radius:13px; padding:8px;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] { margin-top:6px; }
    .status-row { display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid var(--line); font-size:12px; }
    .status-row:last-child { border-bottom:0; }
    .status-name { color:var(--muted); }
    .status-value { color:var(--text); font-family:'DM Mono', monospace; }
    .footer { color:#526178; font:10px 'DM Mono', monospace; letter-spacing:1px; text-align:center; padding:30px 0 4px; }
    .stTabs [data-baseweb="tab-list"] { gap:8px; border-bottom:1px solid var(--line); }
    .stTabs [data-baseweb="tab"] { color:var(--muted); padding:12px 16px; }
    .stTabs [aria-selected="true"] { color:var(--cyan) !important; }
    [data-testid="stAlert"] { border-radius:12px; }

     /* SENTINEL // premium command-console layer */
     .stApp {
         background-image:
           linear-gradient(rgba(94,234,212,.025) 1px, transparent 1px),
           linear-gradient(90deg, rgba(94,234,212,.025) 1px, transparent 1px),
           radial-gradient(ellipse at 78% 0%, rgba(74,116,210,.16), transparent 36%),
           radial-gradient(ellipse at 4% 52%, rgba(94,234,212,.045), transparent 30%);
         background-size: 42px 42px, 42px 42px, auto, auto;
     }
     .block-container { max-width: 1720px; padding: 1.0rem clamp(1rem, 1.2vw, 1.35rem) 2rem; }
     .hero-title { text-wrap: balance; }
     .eyebrow { display:flex; align-items:center; gap:9px; }
     .eyebrow:before { content:''; display:inline-block; width:22px; height:1px; background:var(--cyan); box-shadow:0 0 8px var(--cyan); }
     .pill { backdrop-filter: blur(10px); }
     .metric { box-shadow: 0 12px 35px rgba(0,0,0,.13); transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease; }
     .metric:hover { transform:translateY(-3px); border-color:rgba(94,234,212,.34); box-shadow:0 18px 38px rgba(0,0,0,.22); }
     .metric:before { content:''; position:absolute; width:100px; height:100px; right:-42px; bottom:-56px; border:1px solid rgba(122,167,255,.10); border-radius:50%; box-shadow:0 0 0 12px rgba(122,167,255,.025), 0 0 0 25px rgba(122,167,255,.018); }
     .panel { box-shadow: 0 14px 42px rgba(0,0,0,.12); backdrop-filter: blur(12px); transition:border-color .2s ease; }
     .panel:hover { border-color:rgba(122,167,255,.24); }
     .panel-title { letter-spacing:-.25px; }
     div[data-testid="stHorizontalBlock"] { align-items:stretch; }
     div[data-testid="stMarkdownContainer"] .panel { min-width:0; }
     @media (max-width: 1100px) {
       .panel { padding:12px; }
       .panel-title { font-size:13px; }
     }
     .section-label { display:flex; align-items:center; gap:10px; }
     .section-label:after { content:''; height:1px; flex:1; max-width:180px; background:linear-gradient(90deg, rgba(94,234,212,.35), transparent); }
     .brand-mark { position:relative; overflow:hidden; }
     .brand-mark:after { content:''; position:absolute; inset:-50%; background:linear-gradient(110deg, transparent 35%, rgba(255,255,255,.4), transparent 60%); transform:translateX(-100%); animation:brandSweep 5s ease-in-out infinite; }
     @keyframes brandSweep { 0%,65% { transform:translateX(-100%); } 85%,100% { transform:translateX(100%); } }
    [data-testid="stSidebar"] { box-shadow: 12px 0 38px rgba(0,0,0,.10); }
    [data-testid="stSidebar"] [data-testid="stRadio"] label { border-radius:10px; padding:7px 10px; transition:background .2s ease; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:rgba(94,234,212,.07); }
     .stButton > button, .stDownloadButton > button { box-shadow:0 7px 22px rgba(94,234,212,.07); letter-spacing:.15px; }
     div[data-testid="stFileUploader"] section { border:0; }
     .mission-banner { position:relative; display:grid; grid-template-columns:1fr auto; gap:22px; align-items:center; overflow:hidden; margin:8px 0 24px; padding:25px 28px; border:1px solid rgba(122,167,255,.22); border-radius:20px; background:linear-gradient(110deg, rgba(20,31,47,.96), rgba(12,20,31,.88)); box-shadow:0 18px 50px rgba(0,0,0,.18); }
     .mission-banner:before { content:''; position:absolute; width:260px; height:260px; right:5%; top:-155px; border:1px solid rgba(94,234,212,.13); border-radius:50%; box-shadow:0 0 0 22px rgba(94,234,212,.025), 0 0 0 48px rgba(94,234,212,.018), 0 0 0 76px rgba(94,234,212,.012); pointer-events:none; }
     .mission-kicker { color:var(--cyan); font:10px 'DM Mono',monospace; letter-spacing:2px; margin-bottom:9px; }
     .mission-heading { color:var(--text); font-size:clamp(21px,2.2vw,30px); font-weight:800; letter-spacing:-1px; line-height:1.12; }
     .mission-copy { color:var(--muted); font-size:12px; line-height:1.65; max-width:680px; margin-top:9px; }
     .mission-state { z-index:1; min-width:145px; text-align:center; border:1px solid rgba(94,234,212,.22); border-radius:15px; padding:15px 17px; background:rgba(94,234,212,.055); }
     .state-orbit { width:43px; height:43px; margin:0 auto 9px; border:1px solid rgba(94,234,212,.55); border-radius:50%; display:grid; place-items:center; position:relative; color:var(--cyan); font-size:18px; }
     .state-orbit:before { content:''; position:absolute; inset:-6px; border:1px dashed rgba(94,234,212,.28); border-radius:50%; animation:orbitSpin 18s linear infinite; }
     @keyframes orbitSpin { to { transform:rotate(360deg); } }
     .state-label { color:var(--cyan); font:10px 'DM Mono',monospace; letter-spacing:1.2px; }
     .state-note { color:var(--muted); font-size:10px; margin-top:4px; }
     .stDataFrame, [data-testid="stTable"] { border:1px solid var(--line); border-radius:12px; overflow:hidden; }
     .footer { border-top:1px solid rgba(151,174,204,.08); margin-top:28px; }
     @media (max-width: 760px) { .mission-banner { grid-template-columns:1fr; padding:21px; } .mission-state { display:flex; align-items:center; gap:12px; text-align:left; } .state-orbit { margin:0; flex:0 0 43px; } }
     .ops-grid { display:grid; grid-template-columns:1.15fr .85fr; gap:16px; margin:4px 0 20px; }
     .ops-card { position:relative; overflow:hidden; padding:20px; min-height:180px; border:1px solid var(--line); border-radius:18px; background:linear-gradient(145deg,rgba(18,29,44,.96),rgba(10,17,27,.94)); }
     .ops-card:after { content:""; position:absolute; width:190px; height:190px; right:-90px; bottom:-120px; border:1px solid rgba(94,234,212,.12); border-radius:50%; box-shadow:0 0 0 18px rgba(94,234,212,.025),0 0 0 40px rgba(94,234,212,.018); pointer-events:none; }
     .ops-kicker { color:var(--muted); font:10px 'DM Mono',monospace; letter-spacing:1.8px; text-transform:uppercase; }
     .ops-big { color:var(--text); font-size:clamp(24px,2.7vw,36px); font-weight:800; letter-spacing:-1.4px; line-height:1.15; margin:14px 0 8px; }
     .ops-copy { color:var(--muted); font-size:12px; line-height:1.7; max-width:520px; }
     .ops-chip { display:inline-flex; align-items:center; gap:7px; margin-top:15px; padding:7px 10px; border:1px solid rgba(94,234,212,.2); border-radius:9px; background:rgba(94,234,212,.05); color:var(--cyan); font:10px 'DM Mono',monospace; letter-spacing:.7px; }
     .readiness-row { display:flex; align-items:center; justify-content:space-between; gap:12px; padding:12px 0; border-bottom:1px solid var(--line); }
     .readiness-row:last-child { border-bottom:0; }
     .readiness-label { color:var(--muted); font-size:12px; }
     .readiness-value { font:11px 'DM Mono',monospace; text-align:right; }
     .readiness-good { color:var(--cyan); }
     .readiness-warn { color:var(--orange); }
     .dashboard-heading { display:flex; align-items:center; justify-content:space-between; gap:14px; margin:20px 0 12px; }
     .dashboard-heading-title { font-size:15px; font-weight:700; color:var(--text); }
     .dashboard-heading-meta { color:var(--muted); font:10px 'DM Mono',monospace; letter-spacing:1px; }
     .result-frame { padding:10px; border:1px solid var(--line); border-radius:15px; background:rgba(6,11,18,.55); }
     @media (max-width: 900px) { .ops-grid { grid-template-columns:1fr; } }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_model(model_path: str):
    if YOLO is None:
        raise RuntimeError(
            "Ultralytics is not installed. Install it with: pip install ultralytics"
        )
    if not Path(model_path).is_file():
        raise FileNotFoundError(
            f"Model file not found: {model_path}. Put your trained .pt file in the project "
            "folder or change the model path in the sidebar."
        )
    return YOLO(model_path)


def run_image_detection(image: Image.Image, model: Any, confidence: float):
    """Run YOLO on a PIL image. Returns annotated image + simple metrics."""
    start = time.perf_counter()
    result = model.predict(source=image, conf=confidence, verbose=False)[0]
    elapsed = time.perf_counter() - start
    annotated = result.plot()  # BGR numpy array
    annotated = Image.fromarray(annotated[:, :, ::-1])
    boxes = result.boxes
    count = len(boxes) if boxes is not None else 0

    confidences = []
    class_counts: dict[str, int] = {}
    if boxes is not None and count:
        for box in boxes:
            class_id = int(box.cls[0].item())
            score = float(box.conf[0].item())
            class_name = result.names.get(class_id, str(class_id))
            confidences.append(score)
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

    return {
        "image": annotated,
        "count": count,
        "avg_conf": sum(confidences) / len(confidences) if confidences else 0.0,
        "latency_ms": elapsed * 1000,
        "fps": 1 / elapsed if elapsed > 0 else 0.0,
        "classes": class_counts,
        "result": result,
    }


# ---------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="brand-mark">◈</div>
            <div>
                <div class="brand-name">SENTINEL AI</div>
                <div class="brand-sub">VISION INTELLIGENCE</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="eyebrow">SYSTEM CONFIGURATION</div>', unsafe_allow_html=True)
    nav_options = ["Overview", "Detection Studio", "Events & Reports", "System"]
    nav_target = st.session_state.pop("nav_target", "Overview")
    page = st.radio(
        "Navigation", nav_options, index=nav_options.index(nav_target) if nav_target in nav_options else 0,
        label_visibility="collapsed", key="main_navigation",
    )
    st.markdown("---")
    st.markdown('<div class="section-label">MODEL SETTINGS</div>', unsafe_allow_html=True)
    model_path = st.text_input("Model weights (.pt)", value="best.pt", help="Your best.pt file is in the same folder as app.py. Change this only if you move the weights.")
    confidence = st.slider("Confidence threshold", min_value=0.05, max_value=0.95, value=0.40, step=0.05)
    iou_threshold = st.slider("IoU threshold (NMS)", min_value=0.10, max_value=0.90, value=0.45, step=0.05)
    source_mode = st.selectbox("Input source", ["Image", "Video", "Webcam"])
    st.markdown("---")
    st.markdown('<div class="section-label">ALERT SETTINGS</div>', unsafe_allow_html=True)
    enable_telegram = st.checkbox("Enable Telegram alerts", value=False)
    telegram_token = st.text_input("Telegram bot token", type="password", disabled=not enable_telegram)
    telegram_chat_id = st.text_input("Telegram chat ID", disabled=not enable_telegram)
    st.caption("Telegram credentials are used only for this running session.")
    st.markdown('<div class="section-label">SESSION STATUS</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="status-row"><span class="status-name">Interface</span><span class="status-value">ONLINE</span></div>
        <div class="status-row"><span class="status-name">Inference engine</span><span class="status-value">{'READY' if YOLO else 'NOT INSTALLED'}</span></div>
        <div class="status-row"><span class="status-name">Active source</span><span class="status-value">{source_mode.upper()}</span></div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("SENTINEL AI · UI FOUNDATION v1.0")


# ---------------------------------------------------------------------
# Header + state
# ---------------------------------------------------------------------
if "event_log" not in st.session_state:
    st.session_state.event_log = []
if "last_detection" not in st.session_state:
    st.session_state.last_detection = None
if "model_cache" not in st.session_state:
    st.session_state.model_cache = None
if "model_cache_path" not in st.session_state:
    st.session_state.model_cache_path = None

if page == "Overview":
    st.markdown('<div style="display:flex;justify-content:space-between;align-items:center;padding:2px 0 18px;color:#83bfe8;font-size:11px;letter-spacing:3px;text-transform:uppercase">SMARTER DETECTION&nbsp;&nbsp; / &nbsp;&nbsp;SAFER TOMORROW <span style="letter-spacing:0;color:#a9c8e6;font-size:13px">◉ &nbsp; Sentinel User</span></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="eyebrow">COMPUTER VISION / MONITORING PLATFORM</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="hero-title">{page}</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-copy">A unified workspace for visual detection, event review, and model performance.</div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<span class="pill"><span class="dot"></span> CONSOLE READY</span> &nbsp; <span class="pill">YOLO INFERENCE</span> &nbsp; <span class="pill">EVENT AUDIT TRAIL</span>', unsafe_allow_html=True)
    st.write("")



def _image_to_png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


# Persistent event store adapted from the team's notebook.
PROJECT_DIR = Path(__file__).resolve().parent
ALERTS_DIR = PROJECT_DIR / "alerts"
SNAPSHOTS_DIR = ALERTS_DIR / "snapshots"
LOGS_DIR = ALERTS_DIR / "logs"
CSV_PATH = LOGS_DIR / "fire_smoke_events.csv"
CSV_HEADERS = ["timestamp", "class_name", "confidence", "image_name", "snapshot_path", "alert_type"]

def ensure_event_store() -> None:
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        with CSV_PATH.open("w", newline="", encoding="utf-8-sig") as handle:
            csv.writer(handle).writerow(CSV_HEADERS)

def read_persistent_events():
    ensure_event_store()
    try:
        with CSV_PATH.open("r", newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))
    except (OSError, csv.Error):
        return []

def append_persistent_event(timestamp: str, class_name: str, confidence_score: float,
                            image_name: str, snapshot_path: str, alert_type: str) -> None:
    ensure_event_store()
    with CSV_PATH.open("a", newline="", encoding="utf-8-sig") as handle:
        csv.writer(handle).writerow([
            timestamp, class_name, f"{confidence_score:.4f}", image_name, snapshot_path, alert_type
        ])

def send_telegram_alert(message: str, snapshot_path: str | None = None) -> tuple[bool, str]:
    if not enable_telegram:
        return False, "Telegram disabled"
    if not telegram_token.strip() or not telegram_chat_id.strip():
        return False, "Add both Telegram bot token and chat ID in the sidebar."
    try:
        import requests
        base_url = f"https://api.telegram.org/bot{telegram_token.strip()}"
        response = requests.post(
            f"{base_url}/sendMessage",
            data={"chat_id": telegram_chat_id.strip(), "text": message},
            timeout=12,
        )
        response.raise_for_status()
        if snapshot_path and Path(snapshot_path).is_file():
            with Path(snapshot_path).open("rb") as image_file:
                photo_response = requests.post(
                    f"{base_url}/sendPhoto",
                    data={"chat_id": telegram_chat_id.strip()},
                    files={"photo": image_file},
                    timeout=20,
                )
                photo_response.raise_for_status()
        return True, "Telegram alert sent"
    except Exception as exc:
        return False, f"Telegram failed: {exc}"

def fire_smoke_classes(class_counts: dict[str, int]) -> dict[str, int]:
    return {
        name: count for name, count in class_counts.items()
        if ("fire" in name.lower() or "smoke" in name.lower())
    }


def annotate_video_frame(frame, result, tracks: dict, alpha: float = 0.12):
    """Draw detections with light temporal smoothing to reduce frame-to-frame box jitter.

    Tracks are matched by class and nearby box center. This is visual smoothing, not
    a replacement for a dedicated multi-object tracker.
    """
    output = frame.copy()
    boxes = result.boxes
    current_tracks = {}
    if boxes is None:
        return output, current_tracks

    detections = []
    for box in boxes:
        cls_id = int(box.cls[0].item())
        score = float(box.conf[0].item())
        xyxy = [float(v) for v in box.xyxy[0].tolist()]
        detections.append((cls_id, score, xyxy))

    used_old = set()
    for cls_id, score, xyxy in detections:
        x1, y1, x2, y2 = xyxy
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        best_key, best_dist = None, float("inf")
        for key, old in tracks.items():
            if key in used_old or old["cls"] != cls_id:
                continue
            ox1, oy1, ox2, oy2 = old["xyxy"]
            ocx, ocy = (ox1 + ox2) / 2, (oy1 + oy2) / 2
            dist = ((cx - ocx) ** 2 + (cy - ocy) ** 2) ** 0.5
            max_dist = max(35.0, 0.75 * max(x2 - x1, y2 - y1, ox2 - ox1, oy2 - oy1))
            if dist < best_dist and dist <= max_dist:
                best_key, best_dist = key, dist

        if best_key is not None:
            used_old.add(best_key)
            old_xyxy = tracks[best_key]["xyxy"]
            # Stronger exponential smoothing: use only 12% of the new box position
            # per frame, reducing rapid visual jitter while still following real motion.
            smooth = [alpha * now + (1 - alpha) * before for now, before in zip(xyxy, old_xyxy)]
            # Ignore tiny coordinate changes caused by detector noise.
            smooth = [before if abs(now - before) < 3 else now
                      for now, before in zip(smooth, old_xyxy)]
            track_key = best_key
        else:
            smooth = xyxy
            track_key = f"{cls_id}_{len(current_tracks)}"

        current_tracks[track_key] = {"cls": cls_id, "xyxy": smooth}
        x1, y1, x2, y2 = [int(round(v)) for v in smooth]
        name = result.names.get(cls_id, str(cls_id))
        label = f"{name} {score:.2f}"
        # Use distinct colors for fire and smoke, with a readable label background.
        lower = name.lower()
        color = (0, 140, 255) if "fire" in lower else (255, 180, 40) if "smoke" in lower else (94, 234, 212)
        cv2.rectangle(output, (x1, y1), (x2, y2), color, 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale, thickness = 0.6, 2
        (tw, th), baseline = cv2.getTextSize(label, font, scale, thickness)
        top = max(0, y1 - th - baseline - 6)
        cv2.rectangle(output, (x1, top), (x1 + tw + 8, top + th + baseline + 6), color, -1)
        cv2.putText(output, label, (x1 + 4, top + th + 1), font, scale, (10, 15, 20), thickness, cv2.LINE_AA)

    return output, current_tracks


# ---------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------
if page == "Overview":
    last = st.session_state.last_detection or {}
    persistent_events = read_persistent_events()
    model_exists = Path(model_path).is_file()
    fire_count = sum("fire" in str(r.get("class_name", "")).lower() for r in persistent_events)
    smoke_count = sum("smoke" in str(r.get("class_name", "")).lower() for r in persistent_events)
    total_alerts = len(persistent_events)
    avg_saved = sum(float(r.get("confidence", 0) or 0) for r in persistent_events) / total_alerts if total_alerts else 0
    has_alert = bool(last.get("alert_classes"))

    # Compact top navigation matching the reference dashboard.
    st.markdown('''<div style="display:flex;justify-content:space-between;align-items:center;padding:0 2px 15px;color:#83bfe8;font-size:10px;letter-spacing:3px;text-transform:uppercase;border-bottom:1px solid rgba(85,151,205,.10);margin-bottom:18px">SMARTER DETECTION&nbsp;&nbsp; / &nbsp;&nbsp; SAFER TOMORROW <span style="letter-spacing:0;color:#a9c8e6;font-size:12px;text-transform:none">◉ &nbsp; Sentinel User&nbsp;⌄</span></div>''', unsafe_allow_html=True)

    banner_col, metric_cols = st.columns([1.55, 2.15], gap="small")
    with banner_col:
        border = "#ff5364" if has_alert else "#12d9d0"
        title = "Fire Detected" if has_alert else ("Analysis Complete" if last.get("image") is not None else "System Standing By")
        confidence_value = last.get("avg_conf")
        conf_text = f"High confidence · {confidence_value:.1%}" if isinstance(confidence_value, (int, float)) and has_alert else (f"Average confidence · {confidence_value:.1%}" if isinstance(confidence_value, (int, float)) else "Ready for your next analysis")
        stamp = last.get("timestamp", "No analysis run yet")
        filename = last.get("filename", "Open Detection Studio to begin")
        preview_html = ""
        preview_image = last.get("image")
        if preview_image is not None:
            try:
                preview_buffer = io.BytesIO()
                preview_image.convert("RGB").save(preview_buffer, format="JPEG", quality=82)
                preview_data = base64.b64encode(preview_buffer.getvalue()).decode("ascii")
                preview_html = f'<img src="data:image/jpeg;base64,{preview_data}" style="width:34%;height:104px;object-fit:cover;border-radius:8px;align-self:center;border:1px solid #294d69" />'
            except Exception:
                preview_html = ""
        st.markdown(f'''<div style="height:142px;box-sizing:border-box;padding:12px 12px 12px 18px;border:1px solid #193e5d;border-left:6px solid {border};border-radius:11px;background:radial-gradient(ellipse at 90% 20%,rgba(49,82,111,.30),transparent 38%),linear-gradient(110deg,#21131d,#081b2c);overflow:hidden;display:flex;align-items:center;gap:14px">
        <div style="flex:1;min-width:0">
        <div style="color:#9bc8e8;font-size:10px;letter-spacing:1.4px;margin-bottom:9px">LAST ANALYSIS</div>
        <div style="font-size:22px;line-height:1.2;font-weight:800;color:#f3f8ff">{title}</div><div style="color:{border};font-size:13px;margin-top:5px">{conf_text}</div>
        <div style="color:#9ebbd5;font-size:11px;margin-top:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{stamp} · {filename}</div></div>{preview_html}</div>''', unsafe_allow_html=True)
    with metric_cols:
        cards = st.columns(4, gap="small")
        values = [
            ("TOTAL ALERTS", str(total_alerts), "Saved events", "#00d9ee", "◉"),
            ("FIRE EVENTS", str(fire_count), f"{fire_count / total_alerts:.1%} of alerts" if total_alerts else "No saved fire events", "#ff5364", "♨"),
            ("SMOKE EVENTS", str(smoke_count), f"{smoke_count / total_alerts:.1%} of alerts" if total_alerts else "No saved smoke events", "#258fff", "☁"),
            ("AVG. CONFIDENCE", f"{avg_saved:.1%}" if total_alerts else "—", "Across saved alerts", "#00d7b4", "◇"),
        ]
        for col, (label, value, note, accent, icon) in zip(cards, values):
            with col:
                st.markdown(f'''<div style="height:142px;box-sizing:border-box;padding:13px 13px;border:1px solid #123d5d;border-radius:11px;background:linear-gradient(145deg,#061b30,#081426);position:relative;overflow:hidden"><div style="width:29px;height:29px;display:grid;place-items:center;border-radius:9px;background:{accent}19;color:{accent};font-size:17px;margin-bottom:9px">{icon}</div><div style="font-size:9px;color:#a4c9e8;letter-spacing:.6px;white-space:nowrap">{label}</div><div style="font-size:25px;line-height:1.2;font-weight:800;color:#f5faff;margin-top:7px">{value}</div><div style="font-size:9px;color:#7fa7c8;margin-top:5px;white-space:nowrap">{note}</div></div>''', unsafe_allow_html=True)

    st.write("")
    donut_col, trend_col, ready_col = st.columns([1.05, 1.28, .82], gap="small")

    # Each card is rendered as one complete HTML fragment. Streamlit places
    # separate markdown calls in separate DOM blocks; split divs break layout.
    fire_pct = fire_count / total_alerts * 100 if total_alerts else 0
    smoke_pct = smoke_count / total_alerts * 100 if total_alerts else 0
    ring = (f"conic-gradient(#ff4e5d 0 {fire_pct:.2f}%,#258fff {fire_pct:.2f}% 100%)"
            if total_alerts else "conic-gradient(#16344d 0 100%)")
    donut_html = f'''<div class="panel" style="min-height:255px;box-sizing:border-box">
      <div class="panel-title">ALERTS OVERVIEW</div>
      <div class="panel-sub">Distribution of detected events</div>
      <div style="display:flex;align-items:center;gap:15px;padding:6px 0 3px">
        <div style="width:136px;height:136px;flex:0 0 136px;border-radius:50%;background:{ring};display:flex;align-items:center;justify-content:center">
          <div style="width:91px;height:91px;border-radius:50%;background:#06182b;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;font-size:24px;font-weight:800">{total_alerts}<span style="font-size:10px;font-weight:400;color:#9dc1df">Total alerts</span></div>
        </div>
        <div style="flex:1;font-size:12px;color:#e6f3ff;min-width:0">
          <div style="margin-bottom:17px"><span style="color:#ff5364">●</span> Fire <b style="float:right">{fire_count}</b><div style="color:#9fc1df;font-size:11px;margin-top:4px">{fire_pct:.1f}%</div></div>
          <div><span style="color:#258fff">●</span> Smoke <b style="float:right">{smoke_count}</b><div style="color:#9fc1df;font-size:11px;margin-top:4px">{smoke_pct:.1f}%</div></div>
        </div>
      </div></div>'''

    daily_fire, daily_smoke = {}, {}
    for row in persistent_events:
        try:
            dt = datetime.fromisoformat(str(row.get("timestamp", "")).replace("Z", "+00:00"))
            day = dt.strftime("%b %d")
            target = daily_fire if "fire" in str(row.get("class_name", "")).lower() else daily_smoke
            target[day] = target.get(day, 0) + 1
        except Exception:
            continue
    days = sorted(set(daily_fire) | set(daily_smoke))[-7:]
    if not days:
        days = [datetime.now().strftime("%b %d")]
    fire_vals = [daily_fire.get(day, 0) for day in days]
    smoke_vals = [daily_smoke.get(day, 0) for day in days]
    max_y = max(4, max(fire_vals + smoke_vals, default=0))
    w, h, left, top, plot_h = 440, 166, 28, 10, 112
    xs = [left + i * (w - left - 12) / max(1, len(days)-1) for i in range(len(days))]
    def points(vals):
        return " ".join(f"{x:.1f},{top+plot_h-(v/max_y)*plot_h:.1f}" for x,v in zip(xs, vals))
    grid = ''.join(
        f'<line x1="{left}" y1="{top+i*plot_h/4:.1f}" x2="{w-5}" y2="{top+i*plot_h/4:.1f}" stroke="#16324b" stroke-width="1"/>'
        f'<text x="15" y="{top+i*plot_h/4+4:.1f}" fill="#91b7d8" font-size="10" text-anchor="middle">{max_y-int(i*max_y/4)}</text>'
        for i in range(5))
    labels = ''.join(f'<text x="{x:.1f}" y="145" fill="#91b7d8" font-size="10" text-anchor="middle">{day}</text>' for x,day in zip(xs,days))
    dots1 = ''.join(f'<circle cx="{x:.1f}" cy="{top+plot_h-(v/max_y)*plot_h:.1f}" r="3" fill="#ff5364"/>' for x,v in zip(xs,fire_vals))
    dots2 = ''.join(f'<circle cx="{x:.1f}" cy="{top+plot_h-(v/max_y)*plot_h:.1f}" r="3" fill="#258fff"/>' for x,v in zip(xs,smoke_vals))
    trend_svg = f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="Daily fire and smoke alerts">{grid}<polyline points="{points(fire_vals)}" fill="none" stroke="#ff5364" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><polyline points="{points(smoke_vals)}" fill="none" stroke="#258fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>{dots1}{dots2}{labels}</svg>'
    trend_html = f'''<div class="panel" style="min-height:255px;box-sizing:border-box">
      <div class="panel-title">EVENTS TREND</div><div class="panel-sub">Daily alerts (fire &amp; smoke)</div>
      {trend_svg}
      <div style="display:flex;gap:18px;font-size:10px;color:#b7cce1;margin-top:2px"><span><b style="color:#ff5364">●</b> Fire</span><span><b style="color:#258fff">●</b> Smoke</span></div>
      </div>'''

    checks = [("AI Model", model_exists, Path(model_path).name if model_exists else "Missing weights"),
              ("Ultralytics", YOLO is not None, "Inference engine"),
              ("OpenCV", cv2 is not None, "Image/video support"),
              ("Storage", True, "CSV audit log")]
    readiness_rows = "".join(
        f'''<div style="display:flex;align-items:center;justify-content:space-between;gap:6px;padding:10px 0;border-bottom:1px solid #12314a">
        <div><div style="font-size:11px;color:#e3f0ff">{label}</div><div style="font-size:9px;color:#83aaca">{detail}</div></div>
        <b style="color:{"#00e3bd" if ok else "#ffb85c"};font-size:15px">{"✓" if ok else "!"}</b></div>'''
        for label, ok, detail in checks)
    ready_html = f'''<div class="panel" style="min-height:255px;box-sizing:border-box">
      <div class="panel-title">SYSTEM READINESS</div><div class="panel-sub">Runtime checks</div>
      {readiness_rows}</div>'''

    with donut_col:
        st.markdown(donut_html, unsafe_allow_html=True)
    with trend_col:
        st.markdown(trend_html, unsafe_allow_html=True)
    with ready_col:
        st.markdown(ready_html, unsafe_allow_html=True)

    st.write("")
    st.markdown('<div class="panel" style="padding:15px 14px 10px"><div style="display:flex;justify-content:space-between;align-items:center;gap:12px"><div><div class="panel-title">EVENTS &amp; REPORTS</div><div class="panel-sub" style="margin-bottom:0">Complete history of detected events</div></div><span style="font-size:10px;color:#86b7df">LATEST SAVED EVENTS</span></div></div>', unsafe_allow_html=True)
    if persistent_events:
        recent_rows = persistent_events[::-1][:8]
        table_col, detail_col = st.columns([2.15, 1], gap="small")
        with table_col:
            recent = []
            for row in recent_rows:
                try: conf_text = f"{float(row.get('confidence',0)):.2f}"
                except Exception: conf_text = str(row.get("confidence", "—"))
                recent.append({"TIMESTAMP": row.get("timestamp", ""), "TYPE": str(row.get("class_name", "")).upper(), "CONFIDENCE": conf_text, "IMAGE / SOURCE": row.get("image_name", ""), "ALERT": row.get("alert_type", "")})
            st.dataframe(recent, use_container_width=True, hide_index=True, height=310)
            if st.button("OPEN FULL EVENT HISTORY  →", use_container_width=True, key="overview_events"):
                st.session_state["nav_target"] = "Events & Reports"
                st.rerun()
        with detail_col:
            selected = recent_rows[0]
            st.markdown('<div class="panel-title">EVENT DETAILS</div>', unsafe_allow_html=True)
            snapshot_path = Path(str(selected.get("snapshot_path", "")))
            if snapshot_path.is_file():
                st.image(str(snapshot_path), use_container_width=True)
            else:
                st.markdown('<div style="height:110px;display:flex;align-items:center;justify-content:center;border:1px solid #173a55;border-radius:8px;color:#7197b8">No preview available</div>', unsafe_allow_html=True)
            try: selected_conf = float(selected.get("confidence", 0) or 0)
            except Exception: selected_conf = 0.0
            is_fire = "fire" in str(selected.get("class_name", "")).lower()
            accent = "#ff5364" if is_fire else "#258fff"
            st.markdown(f'''<div style="margin:8px 0 12px;color:{accent};font-weight:700;font-size:13px">● &nbsp; {str(selected.get("class_name", "Unknown")).title()} Detected</div><div class="status-row"><span class="status-name">Timestamp</span><span class="status-value">{selected.get("timestamp", "—")}</span></div><div class="status-row"><span class="status-name">Class</span><span class="status-value">{selected.get("class_name", "—")}</span></div><div class="status-row"><span class="status-name">Confidence</span><span class="status-value">{selected_conf:.1%}</span></div><div class="status-row"><span class="status-name">Source</span><span class="status-value">{selected.get("image_name", "—")}</span></div>''', unsafe_allow_html=True)
    elif st.session_state.event_log:
        st.dataframe(st.session_state.event_log[:8], use_container_width=True, hide_index=True)
    else:
        st.info("No alerts saved yet. Run an image or video analysis in Detection Studio to populate the dashboard.")

elif page == "Detection Studio":
    st.markdown('<div class="section-label">INFERENCE / DETECTION STUDIO</div>', unsafe_allow_html=True)
    source_mode = st.selectbox("Choose analysis mode", ["Image", "Video", "Webcam"], index=["Image", "Video", "Webcam"].index(source_mode), key="studio_source")
    if source_mode == "Image":
        uploaded = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "bmp", "webp"], key="image_upload")
        if uploaded:
            original = Image.open(uploaded).convert("RGB")
            col1, col2 = st.columns(2, gap="large")
            with col1:
                st.markdown('<div class="panel-title">SOURCE IMAGE</div>', unsafe_allow_html=True)
                st.image(original, use_container_width=True)
            with col2:
                st.markdown('<div class="panel-title">ANNOTATED OUTPUT</div>', unsafe_allow_html=True)
                if st.button("▶  RUN DETECTION", use_container_width=True, key="run_image"):
                    try:
                        with st.spinner("Loading model and running inference..."):
                            if st.session_state.model_cache is None or st.session_state.model_cache_path != model_path:
                                st.session_state.model_cache = load_model(model_path)
                                st.session_state.model_cache_path = model_path
                            # Use the selected confidence; IoU is configurable too.
                            result = st.session_state.model_cache.predict(
                                source=original, conf=confidence, iou=iou_threshold, verbose=False
                            )[0]
                            elapsed_ms = result.speed.get("inference", 0.0)
                            annotated_array = result.plot()
                            annotated = Image.fromarray(annotated_array[:, :, ::-1])
                            boxes = result.boxes
                            count = len(boxes) if boxes is not None else 0
                            scores, classes = [], {}
                            if boxes is not None:
                                for box in boxes:
                                    cls_id = int(box.cls[0].item())
                                    score = float(box.conf[0].item())
                                    cls_name = result.names.get(cls_id, str(cls_id))
                                    scores.append(score)
                                    classes[cls_name] = classes.get(cls_name, 0) + 1
                            detection = {
                                "image": annotated,
                                "count": count,
                                "avg_conf": sum(scores) / len(scores) if scores else 0.0,
                                "latency_ms": float(elapsed_ms),
                                "fps": 1000 / elapsed_ms if elapsed_ms else 0.0,
                                "classes": classes,
                                "filename": uploaded.name,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            }
                            st.session_state.last_detection = detection
                            st.session_state.event_log.insert(0, {
                                "time": detection["timestamp"],
                                "source": uploaded.name,
                                "objects": count,
                                "avg_conf": detection["avg_conf"],
                                "status": "Detection complete",
                            })

                            # Persist only fire/smoke detections that meet the chosen confidence threshold.
                            alert_classes = fire_smoke_classes(classes)
                            if alert_classes:
                                ensure_event_store()
                                stamp = datetime.now().astimezone()
                                snapshot_name = f"alert_{stamp.strftime('%Y%m%d_%H%M%S_%f')}_{Path(uploaded.name).stem}.jpg"
                                snapshot_path = SNAPSHOTS_DIR / snapshot_name
                                annotated.save(snapshot_path, format="JPEG", quality=92)
                                timestamp_iso = stamp.isoformat(timespec="seconds")
                                telegram_messages = []
                                for class_name, class_count in alert_classes.items():
                                    matching_scores = []
                                    if boxes is not None:
                                        for box in boxes:
                                            cls_id = int(box.cls[0].item())
                                            cls_name = result.names.get(cls_id, str(cls_id))
                                            score = float(box.conf[0].item())
                                            if cls_name == class_name and score >= confidence:
                                                matching_scores.append(score)
                                    for score in matching_scores:
                                        append_persistent_event(
                                            timestamp_iso, class_name, score, uploaded.name,
                                            str(snapshot_path), "Snapshot + CSV"
                                        )
                                        telegram_messages.append(
                                            f"SENTINEL AI FIRE/SMOKE ALERT\nDetected: {class_name}"
                                            f"\nConfidence: {score:.1%}\nTime: {timestamp_iso}"
                                        )
                                if telegram_messages and enable_telegram:
                                    sent, detail = send_telegram_alert("\n\n".join(telegram_messages), str(snapshot_path))
                                    detection["telegram_status"] = detail
                                detection["snapshot_path"] = str(snapshot_path)
                                detection["alert_classes"] = alert_classes
                            st.rerun()
                    except Exception as exc:
                        st.error(f"Detection failed: {exc}")
                last = st.session_state.last_detection or {}
                if last.get("image") is not None:
                    st.image(last["image"], use_container_width=True)
                    st.download_button(
                        "⬇  Download annotated image",
                        data=_image_to_png_bytes(last["image"]),
                        file_name="sentinel_detection.png",
                        mime="image/png",
                        use_container_width=True,
                    )
                else:
                    st.markdown('<div class="drop-hint">Your annotated image will appear here after inference.</div>', unsafe_allow_html=True)

            last = st.session_state.last_detection or {}
            if last.get("filename") == uploaded.name:
                st.write("")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    metric_card("Objects", str(last["count"]), "Detected instances")
                with c2:
                    metric_card("Avg. confidence", f'{last["avg_conf"]:.1%}', "Detected instances")
                with c3:
                    metric_card("Inference", f'{last["latency_ms"]:.1f} ms', "Model-reported inference time")
                with c4:
                    metric_card("Classes", str(len(last["classes"])), "Unique classes detected")
                if last["classes"]:
                    st.write("")
                    st.markdown('<div class="panel-title">CLASS BREAKDOWN</div>', unsafe_allow_html=True)
                    st.bar_chart(last["classes"])
                else:
                    st.info("No objects passed the current confidence threshold.")
                if last.get("alert_classes"):
                    st.error("FIRE / SMOKE ALERT DETECTED")
                    st.write("Detected alert classes:", ", ".join(last["alert_classes"].keys()))
                    if last.get("snapshot_path"):
                        st.caption(f"Snapshot saved: {last['snapshot_path']}")
                    if last.get("telegram_status"):
                        st.info(last["telegram_status"])
                    elif enable_telegram:
                        st.caption("Telegram was enabled, but no matching alert message was sent.")
                elif last.get("count", 0) > 0:
                    st.success("Objects detected, but no class name matched Fire/Smoke alert rules.")
    elif source_mode == "Video":
        st.markdown('<div class="panel-title">VIDEO ANALYSIS</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Upload a clip and run your trained YOLO model frame by frame.</div>', unsafe_allow_html=True)
        if cv2 is None:
            st.error("OpenCV is not installed. Install it with: pip install opencv-python-headless")
        video = st.file_uploader("Upload a video", type=["mp4", "mov", "avi", "mkv"], key="video_upload")
        if video:
            st.video(video)
            st.caption(f"Selected file: {video.name}")
            frame_step = st.select_slider(
                "Process frames", options=[1, 2, 3, 5], value=1,
                help="1 processes every frame (most accurate, slower). Larger values process fewer frames for speed."
            )
            video_confidence = st.slider(
                "Video confidence threshold", min_value=0.05, max_value=0.95, value=0.25, step=0.05,
                help="Lower than the image threshold by default because smoke can be faint or blurred between video frames."
            )
            st.caption("Tip: if smoke is still missing, try 0.15–0.20. A lower threshold can also add false detections.")
            if st.button("▶  RUN VIDEO DETECTION", use_container_width=True, key="run_video"):
                if cv2 is None:
                    st.error("OpenCV is required. Run: pip install opencv-python-headless")
                else:
                    temp_input = None
                    temp_output = None
                    capture = None
                    writer = None
                    try:
                        with st.spinner("Loading model..."):
                            if st.session_state.model_cache is None or st.session_state.model_cache_path != model_path:
                                st.session_state.model_cache = load_model(model_path)
                                st.session_state.model_cache_path = model_path
                            model = st.session_state.model_cache

                        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(video.name).suffix or ".mp4") as src:
                            src.write(video.getvalue())
                            temp_input = src.name
                        capture = cv2.VideoCapture(temp_input)
                        if not capture.isOpened():
                            raise RuntimeError("Could not open this video. Try an MP4 encoded with H.264 or a standard AVI file.")

                        fps_in = capture.get(cv2.CAP_PROP_FPS)
                        fps_in = fps_in if fps_in and fps_in > 0 else 20.0
                        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        frame_total = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
                        if width <= 0 or height <= 0:
                            raise RuntimeError("The video has invalid dimensions.")

                        processed_dir = PROJECT_DIR / "alerts" / "processed_videos"
                        processed_dir.mkdir(parents=True, exist_ok=True)
                        output_name = f"sentinel_{Path(video.name).stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                        output_path = processed_dir / output_name
                        temp_output = str(output_path)
                        writer = cv2.VideoWriter(
                            temp_output, cv2.VideoWriter_fourcc(*"mp4v"), fps_in / frame_step,
                            (width, height)
                        )
                        if not writer.isOpened():
                            raise RuntimeError("Could not create the output video. Check that OpenCV video codecs are available.")

                        progress = st.progress(0, text="Preparing video...")
                        status = st.empty()
                        frame_idx = 0
                        processed_frames = 0
                        total_detections = 0
                        all_classes = {}
                        alert_max = {}
                        last_annotated = None
                        video_tracks = {}
                        start_time = time.perf_counter()

                        while True:
                            ok, frame = capture.read()
                            if not ok:
                                break
                            frame_idx += 1
                            if (frame_idx - 1) % frame_step != 0:
                                continue
                            result = model.predict(
                                source=frame, conf=video_confidence, iou=iou_threshold,
                                imgsz=960, verbose=False
                            )[0]
                            annotated_frame, video_tracks = annotate_video_frame(frame, result, video_tracks)
                            last_annotated = annotated_frame
                            writer.write(annotated_frame)
                            processed_frames += 1
                            boxes = result.boxes
                            if boxes is not None:
                                for box in boxes:
                                    cls_id = int(box.cls[0].item())
                                    score = float(box.conf[0].item())
                                    cls_name = result.names.get(cls_id, str(cls_id))
                                    total_detections += 1
                                    all_classes[cls_name] = all_classes.get(cls_name, 0) + 1
                                    if "fire" in cls_name.lower() or "smoke" in cls_name.lower():
                                        alert_max[cls_name] = max(alert_max.get(cls_name, 0.0), score)
                            if frame_total > 0:
                                progress.progress(min(frame_idx / frame_total, 1.0), text=f"Processing frame {frame_idx}/{frame_total}...")
                            status.caption(f"Frames processed: {processed_frames} · Detections: {total_detections}")

                        capture.release()
                        capture = None
                        writer.release()
                        writer = None
                        progress.progress(1.0, text="Video analysis complete")
                        elapsed = time.perf_counter() - start_time

                        st.session_state.last_video_detection = {
                            "path": str(output_path), "name": output_name, "frames": processed_frames,
                            "detections": total_detections, "classes": all_classes,
                            "elapsed": elapsed, "alert_classes": alert_max,
                        }
                        st.success(f"Video detection complete — {processed_frames} frames analyzed in {elapsed:.1f} seconds.")
                        if all_classes:
                            st.markdown('<div class="section-label">DETECTION SUMMARY</div>', unsafe_allow_html=True)
                            m1, m2, m3 = st.columns(3)
                            with m1:
                                metric_card("Frames analyzed", str(processed_frames), f"Every {frame_step} frame(s)")
                            with m2:
                                metric_card("Detections", str(total_detections), "Across processed frames")
                            with m3:
                                metric_card("Classes", str(len(all_classes)), "Unique detected classes")
                            st.bar_chart(all_classes)
                        else:
                            st.info("No objects passed the selected confidence threshold in the processed frames.")

                        if alert_max and last_annotated is not None:
                            ensure_event_store()
                            stamp = datetime.now().astimezone()
                            snapshot_path = SNAPSHOTS_DIR / f"video_alert_{stamp.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                            Image.fromarray(cv2.cvtColor(last_annotated, cv2.COLOR_BGR2RGB)).save(snapshot_path, format="JPEG", quality=92)
                            timestamp_iso = stamp.isoformat(timespec="seconds")
                            messages = []
                            for class_name, score in alert_max.items():
                                append_persistent_event(timestamp_iso, class_name, score, video.name, str(snapshot_path), "Video detection")
                                messages.append(f"SENTINEL AI VIDEO ALERT\nDetected: {class_name}\nMax confidence: {score:.1%}\nTime: {timestamp_iso}\nVideo: {video.name}")
                            st.error("FIRE / SMOKE CLASS DETECTED IN VIDEO")
                            st.caption("At least one processed frame matched a class containing 'fire' or 'smoke'. Review the clip and event log.")
                            if enable_telegram:
                                sent, detail = send_telegram_alert("\n\n".join(messages), str(snapshot_path))
                                st.info(detail)

                        with output_path.open("rb") as output_file:
                            st.download_button(
                                "⬇  Download annotated video", data=output_file.read(),
                                file_name=output_name, mime="video/mp4", use_container_width=True
                            )
                        st.video(str(output_path))
                        if last_annotated is not None:
                            st.image(cv2.cvtColor(last_annotated, cv2.COLOR_BGR2RGB), caption="Last processed frame", use_container_width=True)
                    except Exception as exc:
                        st.error(f"Video detection failed: {exc}")
                    finally:
                        if capture is not None:
                            capture.release()
                        if writer is not None:
                            writer.release()
                        for temp_path in (temp_input,):
                            if temp_path and os.path.exists(temp_path):
                                try:
                                    os.remove(temp_path)
                                except OSError:
                                    pass
    else:
        st.info("Webcam mode will be connected to the team's real-time detection pipeline.")
        st.warning("For now, this page does not start a webcam or claim that live detection is running.")
        st.code("Integration target: webcam frame → YOLO inference → annotated frame → FPS / detections", language="text")

elif page == "Events & Reports":
    st.markdown('<div class="section-label">AUDIT / EVENTS & REPORTS</div>', unsafe_allow_html=True)
    persistent_events = read_persistent_events()
    session_events = st.session_state.event_log

    # Normalize saved CSV records for filtering and analytics.
    normalized = []
    for row in persistent_events:
        item = dict(row)
        try:
            item["_confidence"] = float(item.get("confidence", 0) or 0)
        except (TypeError, ValueError):
            item["_confidence"] = 0.0
        try:
            item["_datetime"] = datetime.fromisoformat(str(item.get("timestamp", "")).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            item["_datetime"] = None
        item["_class"] = str(item.get("class_name", "Unknown"))
        normalized.append(item)

    total_alerts = len(normalized)
    fire_count = sum("fire" in row["_class"].lower() for row in normalized)
    smoke_count = sum("smoke" in row["_class"].lower() for row in normalized)
    avg_conf = sum(row["_confidence"] for row in normalized) / total_alerts if total_alerts else 0.0

    # Header callout and metric strip.
    st.markdown(f'''<div class="mission-banner" style="margin-bottom:18px">
      <div><div class="mission-kicker">SENTINEL AI / AUDIT CENTER</div>
      <div class="mission-heading">Events &amp; Reports</div>
      <div class="mission-copy">Review saved fire and smoke detections, inspect evidence, and export a filtered audit report.</div></div>
      <div class="ops-chip">● &nbsp; {total_alerts} SAVED ALERTS</div></div>''', unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4, gap="medium")
    with k1: metric_card("Total alerts", str(total_alerts), "Persisted in CSV")
    with k2: metric_card("Fire events", str(fire_count), f"{fire_count / total_alerts:.1%} of alerts" if total_alerts else "No saved alerts")
    with k3: metric_card("Smoke events", str(smoke_count), f"{smoke_count / total_alerts:.1%} of alerts" if total_alerts else "No saved alerts")
    with k4: metric_card("Average confidence", f"{avg_conf:.1%}" if total_alerts else "—", "Across saved alert records")

    st.write("")
    filter_col, analytics_col = st.columns([0.9, 1.5], gap="large")
    with filter_col:
        st.markdown('<div class="panel-title">Reports &amp; filters</div>', unsafe_allow_html=True)
        classes = sorted({row["_class"] for row in normalized})
        chosen_classes = st.multiselect("Detected class", classes, default=classes, placeholder="Choose classes") if classes else []
        search_text = st.text_input("Source filename", placeholder="Search by filename…")
        confidence_floor = st.slider("Minimum confidence", 0, 100, 0, 5) / 100
        valid_dates = [row["_datetime"].date() for row in normalized if row["_datetime"] is not None]
        date_range = st.date_input("Date range", value=(min(valid_dates), max(valid_dates))) if valid_dates else ()
        st.caption(f"Event database: {CSV_PATH}")
        if st.button("Clear session-only events", use_container_width=True):
            st.session_state.event_log = []
            st.rerun()
        st.caption("Only temporary session activity is cleared. Saved CSV alerts and snapshots are not deleted.")

    filtered = []
    for row in normalized:
        if chosen_classes and row["_class"] not in chosen_classes:
            continue
        if not chosen_classes and classes:
            continue
        if row["_confidence"] < confidence_floor:
            continue
        if search_text and search_text.casefold() not in str(row.get("image_name", "")).casefold():
            continue
        if len(date_range) == 2 and row["_datetime"] is not None:
            if not (date_range[0] <= row["_datetime"].date() <= date_range[1]):
                continue
        filtered.append(row)

    with analytics_col:
        st.markdown('<div class="panel-title">Alert analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Class distribution for the current filters</div>', unsafe_allow_html=True)
        class_counts = {}
        for row in filtered:
            class_counts[row["_class"]] = class_counts.get(row["_class"], 0) + 1
        if class_counts:
            max_count = max(class_counts.values()) or 1
            for class_name, count in sorted(class_counts.items(), key=lambda pair: pair[1], reverse=True):
                share = count / len(filtered) * 100 if filtered else 0
                width = max(3, int(count / max_count * 100))
                safe_class = (class_name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
                st.markdown(f'''<div style="margin:13px 0 17px">
                  <div style="display:flex;justify-content:space-between;gap:12px;margin-bottom:7px;font-size:14px">
                    <span>{safe_class}</span><span style="color:#8fb4d8;font-family:monospace">{count} <span style="color:#7e91a8">/ {share:.1f}%</span></span></div>
                  <div style="height:10px;border-radius:99px;background:#172638;overflow:hidden">
                    <div style="height:100%;width:{width}%;border-radius:99px;background:linear-gradient(90deg,#27d9d0,#65aaff)"></div></div></div>''', unsafe_allow_html=True)
        else:
            st.info("No saved alerts match these filters.")
        if filtered:
            scores = [row["_confidence"] for row in filtered]
            st.caption(f"Showing {len(filtered)} of {total_alerts} saved records · confidence range {min(scores):.1%}–{max(scores):.1%}")

    st.write("")
    st.markdown('<div class="panel-title">Event history</div>', unsafe_allow_html=True)
    report_col, count_col = st.columns([1, 2])
    with report_col:
        export_rows = [{key: row.get(key, "") for key in CSV_HEADERS} for row in filtered]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(export_rows)
        st.download_button("⬇  Export filtered alerts (CSV)", data=output.getvalue(), file_name="sentinel_filtered_alerts.csv", mime="text/csv", use_container_width=True, disabled=not filtered)
    with count_col:
        st.caption(f"{len(filtered)} matching event(s) · newest first")

    if filtered:
        display_rows = []
        for row in sorted(filtered, key=lambda item: item.get("_datetime") or datetime.min, reverse=True):
            display_rows.append({
                "Timestamp": row.get("timestamp", ""),
                "Class": row.get("class_name", ""),
                "Confidence": f'{row["_confidence"]:.1%}',
                "Source file": row.get("image_name", ""),
                "Alert type": row.get("alert_type", ""),
            })
        st.dataframe(display_rows, use_container_width=True, hide_index=True, height=320)

        options = list(range(len(filtered)))
        selected_index = st.selectbox(
            "Inspect event evidence",
            options,
            format_func=lambda i: f'{filtered[i].get("timestamp", "Unknown time")} · {filtered[i].get("class_name", "Unknown")} · {filtered[i]["_confidence"]:.1%}',
        )
        selected = filtered[selected_index]
        detail_col, image_col = st.columns([1, 1.5], gap="large")
        with detail_col:
            st.markdown('<div class="panel-title">Selected event</div>', unsafe_allow_html=True)
            metric_card("Detected class", selected.get("class_name", "Unknown"), "Model classification")
            metric_card("Confidence", f'{selected["_confidence"]:.1%}', "Model confidence score")
            st.write(f'**Timestamp:** {selected.get("timestamp", "—")}')
            st.write(f'**Source:** {selected.get("image_name", "—")}')
            st.write(f'**Alert type:** {selected.get("alert_type", "—")}')
        with image_col:
            st.markdown('<div class="panel-title">Evidence snapshot</div>', unsafe_allow_html=True)
            snapshot_path = Path(str(selected.get("snapshot_path", "")))
            if snapshot_path.is_file():
                st.image(str(snapshot_path), caption=snapshot_path.name, use_container_width=True)
            else:
                st.warning("No snapshot is available at the saved path for this event.")
    else:
        st.info("No alerts match the selected filters. Try widening the date range or lowering minimum confidence.")

    if session_events:
        with st.expander(f"Temporary activity in this session ({len(session_events)})"):
            st.dataframe(session_events, use_container_width=True, hide_index=True)

else:  # System
    st.markdown('<div class="section-label">DIAGNOSTICS / SYSTEM</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Runtime checks</div>', unsafe_allow_html=True)
        checks = [
            ("Streamlit interface", True, "Loaded"),
            ("Ultralytics package", YOLO is not None, "Available" if YOLO else "Install ultralytics"),
            ("Model weights", Path(model_path).is_file(), "Found" if Path(model_path).is_file() else "No .pt file at configured path"),
        ]
        for label, ok, detail in checks:
            icon = "✓" if ok else "!"
            color = "#5eead4" if ok else "#ffb86b"
            st.markdown(
                f'<div class="status-row"><span class="status-name">{label}</span><span style="color:{color};font-family:DM Mono,monospace">{icon} {detail}</span></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">Integration checklist</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-sub">Connect these to the team\'s implementation before final submission.</div>', unsafe_allow_html=True)
        for item in [
            "Trained YOLO weights (.pt)",
            "Image inference with confidence and IoU controls",
            "Fire/Smoke class matching and alert conditions",
            "Persistent CSV logging and annotated snapshots",
            "Optional Telegram message + snapshot delivery",
            "Video detection with adjustable confidence and temporal box smoothing",
            "Webcam / FPS optimization (next integration step)",
            "Model evaluation metrics (mAP / precision / recall)",
        ]:
            st.markdown(f"• {item}")
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<div class="footer">SENTINEL AI · COMPUTER VISION WORKSPACE · CONNECT REAL MODEL OUTPUTS BEFORE DEMO</div>',
    unsafe_allow_html=True,
)

