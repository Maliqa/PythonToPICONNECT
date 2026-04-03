"""
=============================================================
 TAHAP 1 — Buat PI Tags via AF SDK (pythonnet)
=============================================================
 CARA PAKAI:
   py -3.11 C:\PI_Demo\create_tags.py
=============================================================
"""

import clr
import sys

AF_SDK_PATH = r"C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0"
sys.path.append(AF_SDK_PATH)
clr.AddReference("OSIsoft.AFSDK")

from OSIsoft.AF.PI import PIServers, PIPoint
from System.Collections.Generic import Dictionary
from System import String, Object

PI_SERVER_NAME = "PISRVCISDEMO"

TAGS = [
    {"name": "DEMO.COMP01.VIB.RMS",  "descriptor": "Compressor 01 Vibration RMS",   "eng_units": "mm/s", "zero": 0, "span": 50},
    {"name": "DEMO.COMP01.TEMP",     "descriptor": "Compressor 01 Temperature",      "eng_units": "degC", "zero": 0, "span": 200},
    {"name": "DEMO.COMP01.PRESS",    "descriptor": "Compressor 01 Suction Pressure", "eng_units": "bar",  "zero": 0, "span": 20},
    {"name": "DEMO.PUMP01.VIB.RMS",  "descriptor": "Pump 01 Vibration RMS",          "eng_units": "mm/s", "zero": 0, "span": 50},
    {"name": "DEMO.PUMP01.TEMP",     "descriptor": "Pump 01 Bearing Temperature",    "eng_units": "degC", "zero": 0, "span": 150},
    {"name": "DEMO.PUMP01.PRESS",    "descriptor": "Pump 01 Discharge Pressure",     "eng_units": "bar",  "zero": 0, "span": 20},
    {"name": "DEMO.MTR01.VIB.RMS",   "descriptor": "Motor 01 Vibration RMS",         "eng_units": "mm/s", "zero": 0, "span": 50},
    {"name": "DEMO.MTR01.TEMP",      "descriptor": "Motor 01 Winding Temperature",   "eng_units": "degC", "zero": 0, "span": 200},
    {"name": "DEMO.MTR01.CURR",      "descriptor": "Motor 01 Current",               "eng_units": "A",    "zero": 0, "span": 100},
]

def make_attributes(tag_def):
    """Buat IDictionary<string, object> yang dibutuhkan AF SDK"""
    d = Dictionary[String, Object]()
    d["descriptor"]      = tag_def["descriptor"]
    d["engunits"]        = tag_def["eng_units"]
    d["pointtype"]       = "Float32"
    d["zero"]            = float(tag_def["zero"])
    d["span"]            = float(tag_def["span"])
    d["compressing"]     = 1
    d["excdev"]          = 0.5
    d["excdevpercent"]   = 1.0
    return d

def main():
    print("=" * 60)
    print("  Membuat PI Tags di PISRVCISDEMO (via AF SDK)")
    print("=" * 60)

    try:
        pi_servers = PIServers()
        server = pi_servers[PI_SERVER_NAME]
        server.Connect()
        print(f"  Connected: {server.Name}\n")
    except Exception as e:
        print(f"  [ERROR] Gagal connect: {e}")
        return

    created = skipped = failed = 0

    for tag_def in TAGS:
        name = tag_def["name"]

        # Cek apakah tag sudah ada
        try:
            PIPoint.FindPIPoint(server, name)
            print(f"  [SKIP] {name} — sudah ada")
            skipped += 1
            continue
        except:
            pass

        # Buat tag baru
        try:
            attrs = make_attributes(tag_def)
            server.CreatePIPoint(name, attrs)
            print(f"  [OK]   {name} — {tag_def['descriptor']} ({tag_def['eng_units']})")
            created += 1
        except Exception as e:
            print(f"  [ERR]  {name} — {e}")
            failed += 1

    print(f"\n  {'─'*55}")
    print(f"  Selesai! Created: {created} | Skipped: {skipped} | Failed: {failed}")
    print(f"\n  Lanjut ke: py -3.11 C:\\PI_Demo\\create_af.py")
    print(f"  {'─'*55}\n")

if __name__ == "__main__":
    main()
