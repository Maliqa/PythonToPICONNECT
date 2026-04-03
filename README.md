# 🏭 OPC DA Simulator — PI System Demo

Simulasi data source OPC DA menggunakan Python yang push data langsung ke **PI Data Archive** via **PIconnect (PI SDK)**, dengan hierarki aset di **PI AF**, dan divisualisasikan di **PI Vision**.

---

## 📐 Architecture

```
Streamlit App (localhost:8501)
        │
        │  PIconnect + AF SDK (pythonnet)
        │  OSIsoft.AFSDK.dll
        ▼
PI Data Archive (\\PISRVCISDEMO)
        │  9 PI Tags — Float32 — mm/s, degC, bar, A
        │
        │  PI Point Data Reference
        ▼
PI Asset Framework — Database: DEMO_PLANT
        │
        ├── Rotating Equipment
        │       ├── Compressor-01
        │       │       ├── Vibration RMS  → DEMO.COMP01.VIB.RMS
        │       │       ├── Temperature    → DEMO.COMP01.TEMP
        │       │       └── Suction Press  → DEMO.COMP01.PRESS
        │       ├── Pump-01
        │       │       ├── Vibration RMS  → DEMO.PUMP01.VIB.RMS
        │       │       ├── Bearing Temp   → DEMO.PUMP01.TEMP
        │       │       └── Discharge Press→ DEMO.PUMP01.PRESS
        │       └── Motor-01
        │               ├── Vibration RMS  → DEMO.MTR01.VIB.RMS
        │               ├── Winding Temp   → DEMO.MTR01.TEMP
        │               └── Current        → DEMO.MTR01.CURR
        │
        │  AF Asset Browse
        ▼
PI Vision (localhost/PIVision)
```

---

## 🗂️ File Structure

```
C:\PI_Demo\
├── create_tags.py      # Buat 9 PI Tags di Data Archive via AF SDK
├── create_af.py        # Buat PI AF hierarchy (DEMO_PLANT)
└── streamlit_app.py    # Dashboard simulasi OPC DA + push ke PI
```

---

## ⚙️ Requirements

| Komponen | Versi |
|---|---|
| OS | Windows 10 (10.0.19045) |
| Python | 3.11.9 (64-bit) |
| PIconnect | 0.12.4 |
| pythonnet | 3.0.5 |
| AF SDK | 2.10.11.2717 |
| PI Data Archive | PISRVCISDEMO |
| Streamlit | 1.x |
| Plotly | 6.x |

**AF SDK DLL Path:**
```
C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0\OSIsoft.AFSDK.dll
```

---

## 🚀 Quick Start

### 1. Install dependencies
```cmd
py -3.11 -m pip install PIconnect streamlit plotly
```

### 2. Buat PI Tags
```cmd
py -3.11 C:\PI_Demo\create_tags.py
```
Output: `Created: 9 | Skipped: 0 | Failed: 0`

### 3. Buat PI AF Hierarchy
```cmd
py -3.11 C:\PI_Demo\create_af.py
```
Lalu buka **PI System Explorer → DEMO_PLANT → Check In**

### 4. Jalankan Streamlit
```cmd
py -3.11 -m streamlit run C:\PI_Demo\streamlit_app.py
```
Buka browser: `http://localhost:8501`

### 5. Lihat di PI Vision
```
http://localhost/PIVision → New Display → Browse DEMO_PLANT
```

---

## 📊 Simulasi Data

### Vibration RMS
| Parameter | Nilai |
|---|---|
| Baseline | 2.5 mm/s (Compressor), 1.8 (Pump), 1.2 (Motor) |
| Noise | Gaussian σ = 0.10–0.15 |
| Sine component | Amplitude 5% baseline, T = 120s |
| Spike probability | 4% per interval |
| Spike range | 8–28 mm/s (bearing fault simulation) |
| Spike duration | 3 intervals |

### Temperature
| Parameter | Nilai |
|---|---|
| Baseline | 75°C (Comp), 60°C (Pump), 85°C (Motor) |
| Spike range | 85–130°C |
| Spike probability | 3% per interval |

### Pressure / Current
| Parameter | Nilai |
|---|---|
| Pressure baseline | 5.5 bar (Comp suction), 8.0 bar (Pump discharge) |
| Current baseline | 42 A (Motor) |
| Spike probability | 2% per interval |

### Alarm Thresholds
| Sensor | Warning | Alarm |
|---|---|---|
| Vibration RMS | 7.1 mm/s | 11.2 mm/s |
| Temperature | 85°C | 100°C |
| Pressure | 7–10 bar | 8.5–12 bar |
| Current | 55 A | 65 A |

---

## 🔧 Troubleshooting

### PIconnect OK tapi data tidak masuk PI Vision
→ Buka PSE → pilih DEMO_PLANT → klik **Check In**
→ Refresh browser PI Vision (F5)

### `No method matches given arguments for PIServer.CreatePIPoint`
→ Pastikan menggunakan `Dictionary[String, Object]` dari `System.Collections.Generic`, bukan Python `dict`

### `Failed building wheel for pythonnet`
→ Python 3.14 tidak support. Gunakan **Python 3.11.9**

### Streamlit: `No module named streamlit`
→ Jalankan: `py -3.11 -m pip install streamlit plotly`

### PI Vision DEMO_PLANT kosong
→ Lakukan **Check In** di PSE dulu setelah `create_af.py` jalan

---

## 🧠 Konsep yang Dipakai

- **PIconnect** — Python wrapper untuk PI SDK, memungkinkan akses PI Data Archive tanpa PI Web API
- **pythonnet (clr)** — Bridge antara Python dan .NET DLL (AF SDK)
- **PI AF** — Asset Framework untuk memberikan konteks engineering pada raw PI Tags
- **PI Point Data Reference** — Mekanisme linking antara AF Attribute dan PI Tag
- **Streamlit** — Python web framework untuk rapid dashboard development
- **Bearing Fault Simulation** — Random spike injection untuk simulate kondisi fault pada rotating equipment

---

## 📝 Notes

- Script ini dibuat untuk **demo & learning** di environment PISRVCISDEMO
- Tidak memerlukan PI Web API — koneksi langsung via PI SDK (COM-based)
- Semua data adalah **simulasi** — bukan data plant real
- Interval default: **5 detik** per data point

---

*Generated: 2026-04-04 | PI Demo Lab | PISRVCISDEMO*

