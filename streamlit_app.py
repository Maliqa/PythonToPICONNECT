"""
=============================================================
 TAHAP 3 — Streamlit OPC DA Simulator Dashboard
=============================================================
 CARA PAKAI:
   1. pip install streamlit (kalau belum)
      py -3.11 -m pip install streamlit plotly
   2. Jalankan:
      py -3.11 -m streamlit run streamlit_app.py
   3. Buka browser: http://localhost:8501
=============================================================
"""

import streamlit as st
import PIconnect as PI
import random
import math
import time
import plotly.graph_objects as go
from datetime import datetime
from collections import deque

# ─────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────

PI_SERVER   = "PISRVCISDEMO"
MAX_HISTORY = 60   # Jumlah data point yang ditampilkan di chart

ASSETS = {
    "Compressor-01": {
        "icon": "🔵",
        "tags": {
            "Vibration RMS (mm/s)" : {"tag": "DEMO.COMP01.VIB.RMS",  "baseline": 2.5,  "noise": 0.15, "spike_min": 12, "spike_max": 25, "spike_prob": 0.04},
            "Temperature (°C)"     : {"tag": "DEMO.COMP01.TEMP",     "baseline": 75.0, "noise": 0.8,  "spike_min": 95, "spike_max": 110,"spike_prob": 0.03},
            "Suction Pressure (bar)": {"tag": "DEMO.COMP01.PRESS",   "baseline": 5.5,  "noise": 0.05, "spike_min": 7,  "spike_max": 9,  "spike_prob": 0.02},
        }
    },
    "Pump-01": {
        "icon": "🟢",
        "tags": {
            "Vibration RMS (mm/s)" : {"tag": "DEMO.PUMP01.VIB.RMS",  "baseline": 1.8,  "noise": 0.12, "spike_min": 10, "spike_max": 22, "spike_prob": 0.04},
            "Temperature (°C)"     : {"tag": "DEMO.PUMP01.TEMP",     "baseline": 60.0, "noise": 0.6,  "spike_min": 85, "spike_max": 100,"spike_prob": 0.03},
            "Discharge Pressure (bar)": {"tag": "DEMO.PUMP01.PRESS", "baseline": 8.0,  "noise": 0.08, "spike_min": 11, "spike_max": 13, "spike_prob": 0.02},
        }
    },
    "Motor-01": {
        "icon": "🟡",
        "tags": {
            "Vibration RMS (mm/s)" : {"tag": "DEMO.MTR01.VIB.RMS",  "baseline": 1.2,  "noise": 0.10, "spike_min": 8,  "spike_max": 18, "spike_prob": 0.04},
            "Temperature (°C)"     : {"tag": "DEMO.MTR01.TEMP",     "baseline": 85.0, "noise": 1.0,  "spike_min": 110,"spike_max": 130,"spike_prob": 0.03},
            "Current (A)"          : {"tag": "DEMO.MTR01.PRESS",    "baseline": 42.0, "noise": 0.5,  "spike_min": 60, "spike_max": 75, "spike_prob": 0.02},
        }
    },
}

# Alarm thresholds
THRESHOLDS = {
    "Vibration RMS (mm/s)"     : {"warning": 7.1, "alarm": 11.2},
    "Temperature (°C)"         : {"warning": 85,  "alarm": 100},
    "Suction Pressure (bar)"   : {"warning": 7.0, "alarm": 8.5},
    "Discharge Pressure (bar)" : {"warning": 10,  "alarm": 12},
    "Current (A)"              : {"warning": 55,  "alarm": 65},
}

# ─────────────────────────────────────────────
#  SESSION STATE INIT
# ─────────────────────────────────────────────

def init_state():
    if "running" not in st.session_state:
        st.session_state.running = False
    if "history" not in st.session_state:
        st.session_state.history = {
            asset: {sensor: deque(maxlen=MAX_HISTORY) for sensor in cfg["tags"]}
            for asset, cfg in ASSETS.items()
        }
    if "timestamps" not in st.session_state:
        st.session_state.timestamps = deque(maxlen=MAX_HISTORY)
    if "spike_state" not in st.session_state:
        st.session_state.spike_state = {
            asset: {sensor: 0 for sensor in cfg["tags"]}
            for asset, cfg in ASSETS.items()
        }
    if "total_sent" not in st.session_state:
        st.session_state.total_sent = 0
    if "fault_events" not in st.session_state:
        st.session_state.fault_events = []
    if "pi_points" not in st.session_state:
        st.session_state.pi_points = {}
    if "connected" not in st.session_state:
        st.session_state.connected = False

# ─────────────────────────────────────────────
#  PI CONNECTION
# ─────────────────────────────────────────────

@st.cache_resource
def connect_pi():
    """Connect ke PI Server dan resolve semua tags"""
    try:
        server = PI.PIServer(server=PI_SERVER)
        points = {}
        for asset, cfg in ASSETS.items():
            for sensor, tag_cfg in cfg["tags"].items():
                tag_name = tag_cfg["tag"]
                results = list(server.search(tag_name))
                if results:
                    points[tag_name] = results[0]
        return server, points, True
    except Exception as e:
        return None, {}, False

# ─────────────────────────────────────────────
#  DATA GENERATOR
# ─────────────────────────────────────────────

def generate_value(asset, sensor, cfg, t):
    """Generate nilai simulasi dengan spike logic"""
    spike_remaining = st.session_state.spike_state[asset][sensor]
    baseline = cfg["baseline"]
    noise    = random.gauss(0, cfg["noise"])
    sine     = baseline * 0.05 * math.sin(2 * math.pi * t / 120)

    if spike_remaining > 0:
        value = random.uniform(cfg["spike_min"], cfg["spike_max"])
        st.session_state.spike_state[asset][sensor] -= 1
        is_fault = True
    elif random.random() < cfg["spike_prob"]:
        value = random.uniform(cfg["spike_min"], cfg["spike_max"])
        st.session_state.spike_state[asset][sensor] = 3
        is_fault = True
        st.session_state.fault_events.append({
            "time"  : datetime.now().strftime("%H:%M:%S"),
            "asset" : asset,
            "sensor": sensor,
            "value" : round(value, 2)
        })
        # Keep only last 10 events
        if len(st.session_state.fault_events) > 10:
            st.session_state.fault_events.pop(0)
    else:
        value = baseline + sine + noise
        is_fault = False

    return max(0.01, round(value, 3)), is_fault

# ─────────────────────────────────────────────
#  ALARM STATUS
# ─────────────────────────────────────────────

def get_alarm_status(sensor, value):
    key = next((k for k in THRESHOLDS if k in sensor), None)
    if not key:
        return "normal"
    t = THRESHOLDS[key]
    if value >= t["alarm"]:
        return "alarm"
    elif value >= t["warning"]:
        return "warning"
    return "normal"

STATUS_COLOR = {"normal": "🟢", "warning": "🟡", "alarm": "🔴"}

# ─────────────────────────────────────────────
#  CHART
# ─────────────────────────────────────────────

def make_chart(timestamps, values, sensor, asset):
    key = next((k for k in THRESHOLDS if k in sensor), None)
    fig = go.Figure()

    # Data line
    fig.add_trace(go.Scatter(
        x=list(timestamps), y=list(values),
        mode="lines+markers",
        line=dict(color="#00b4d8", width=2),
        marker=dict(size=4),
        name=sensor,
    ))

    # Threshold lines
    if key:
        t = THRESHOLDS[key]
        fig.add_hline(y=t["warning"], line_dash="dash", line_color="orange",
                      annotation_text="Warning", annotation_position="bottom right")
        fig.add_hline(y=t["alarm"], line_dash="dash", line_color="red",
                      annotation_text="Alarm", annotation_position="bottom right")

    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0.1)",
        font=dict(color="white", size=10),
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)"),
        showlegend=False,
    )
    return fig

# ─────────────────────────────────────────────
#  MAIN UI
# ─────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="OPC DA Simulator — PI Demo",
        page_icon="🏭",
        layout="wide",
    )

    init_state()

    # Header
    st.markdown("## 🏭 OPC DA Simulator — PI Demo Plant")
    st.markdown("**Target:** PISRVCISDEMO | **AF Database:** DEMO_PLANT")
    st.divider()

    # Connect PI
    server, pi_points, connected = connect_pi()
    if connected:
        st.session_state.pi_points   = pi_points
        st.session_state.connected   = True

    # ── Sidebar Controls ──
    with st.sidebar:
        st.markdown("### ⚙️ Control Panel")

        conn_status = "✅ Connected" if connected else "❌ Disconnected"
        st.markdown(f"**PI Server:** `{PI_SERVER}`")
        st.markdown(f"**Status:** {conn_status}")
        st.markdown(f"**Tags Loaded:** {len(pi_points)}/9")
        st.divider()

        interval = st.slider("Interval (detik)", 2, 30, 5)
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶ START", type="primary", use_container_width=True):
                st.session_state.running = True
        with col2:
            if st.button("⏹ STOP", use_container_width=True):
                st.session_state.running = False

        st.divider()
        st.markdown(f"**Data Points Sent:** `{st.session_state.total_sent}`")
        st.markdown(f"**Fault Events:** `{len(st.session_state.fault_events)}`")

        # Fault log
        if st.session_state.fault_events:
            st.divider()
            st.markdown("### ⚡ Fault Log")
            for ev in reversed(st.session_state.fault_events[-5:]):
                st.markdown(
                    f"`{ev['time']}` **{ev['asset']}**  \n"
                    f"{ev['sensor']}: `{ev['value']}`"
                )

    # ── Asset Panels ──
    t = st.session_state.total_sent

    for asset, cfg in ASSETS.items():
        st.markdown(f"### {cfg['icon']} {asset}")
        cols = st.columns(3)

        for idx, (sensor, tag_cfg) in enumerate(cfg["tags"].items()):
            with cols[idx]:
                if st.session_state.running:
                    value, is_fault = generate_value(asset, sensor, tag_cfg, t)
                    st.session_state.history[asset][sensor].append(value)

                    # Push ke PI
                    tag_name = tag_cfg["tag"]
                    if tag_name in st.session_state.pi_points:
                        try:
                            st.session_state.pi_points[tag_name].update_value(value)
                        except Exception:
                            pass
                else:
                    history = st.session_state.history[asset][sensor]
                    value   = history[-1] if history else tag_cfg["baseline"]
                    is_fault = False

                alarm  = get_alarm_status(sensor, value)
                icon   = STATUS_COLOR[alarm]
                border = {"normal": "#00b4d8", "warning": "orange", "alarm": "red"}[alarm]

                st.markdown(
                    f"""
                    <div style="border:1px solid {border}; border-radius:8px; padding:10px; margin-bottom:5px;">
                        <div style="font-size:11px; color:#aaa;">{sensor}</div>
                        <div style="font-size:28px; font-weight:bold; color:white;">{value:.2f}</div>
                        <div style="font-size:11px;">{icon} {'⚡ FAULT' if is_fault else alarm.upper()}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Mini chart
                history = st.session_state.history[asset][sensor]
                if len(history) > 2:
                    fig = make_chart(
                        st.session_state.timestamps,
                        history, sensor, asset
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"{asset}_{sensor}")

        st.divider()

    # Update timestamps & counter
    if st.session_state.running:
        st.session_state.timestamps.append(datetime.now().strftime("%H:%M:%S"))
        st.session_state.total_sent += 1
        time.sleep(interval)
        st.rerun()


if __name__ == "__main__":
    main()