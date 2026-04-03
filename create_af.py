"""
=============================================================
 TAHAP 2 — Buat PI AF Hierarchy via AF SDK
=============================================================
 CARA PAKAI:
   py -3.11 C:\PI_Demo\create_af.py
=============================================================
"""

import clr
import sys

AF_SDK_PATH = r"C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0"
sys.path.append(AF_SDK_PATH)
clr.AddReference("OSIsoft.AFSDK")

import OSIsoft.AF as AF
import OSIsoft.AF.Asset as AFAsset
import OSIsoft.AF.PI as AFPI

PI_SERVER_NAME = "PISRVCISDEMO"
AF_DB_NAME     = "DEMO_PLANT"

ASSETS = [
    {
        "name"        : "Compressor-01",
        "description" : "Centrifugal Compressor Unit 01",
        "attributes"  : [
            {"name": "Vibration RMS",     "tag": "DEMO.COMP01.VIB.RMS", "uom": "mm/s"},
            {"name": "Temperature",       "tag": "DEMO.COMP01.TEMP",    "uom": "degC"},
            {"name": "Suction Pressure",  "tag": "DEMO.COMP01.PRESS",   "uom": "bar"},
        ]
    },
    {
        "name"        : "Pump-01",
        "description" : "Centrifugal Pump Unit 01",
        "attributes"  : [
            {"name": "Vibration RMS",      "tag": "DEMO.PUMP01.VIB.RMS", "uom": "mm/s"},
            {"name": "Bearing Temperature","tag": "DEMO.PUMP01.TEMP",    "uom": "degC"},
            {"name": "Discharge Pressure", "tag": "DEMO.PUMP01.PRESS",   "uom": "bar"},
        ]
    },
    {
        "name"        : "Motor-01",
        "description" : "Induction Motor Unit 01",
        "attributes"  : [
            {"name": "Vibration RMS",       "tag": "DEMO.MTR01.VIB.RMS", "uom": "mm/s"},
            {"name": "Winding Temperature", "tag": "DEMO.MTR01.TEMP",    "uom": "degC"},
            {"name": "Current",             "tag": "DEMO.MTR01.CURR",    "uom": "A"},
        ]
    },
]

def main():
    print("=" * 60)
    print("  Membuat PI AF Hierarchy")
    print("=" * 60)

    # Connect ke AF Server
    try:
        pi_systems = AF.PISystems()
        pi_system  = pi_systems.DefaultPISystem
        if pi_system is None:
            pi_system = pi_systems[PI_SERVER_NAME]
        pi_system.Connect()
        print(f"  Connected ke AF Server: {pi_system.Name}\n")
    except Exception as e:
        print(f"  [ERROR] Gagal connect ke AF Server: {e}")
        return

    # Buat atau ambil database
    if pi_system.Databases.Contains(AF_DB_NAME):
        db = pi_system.Databases[AF_DB_NAME]
        print(f"  [SKIP] Database '{AF_DB_NAME}' sudah ada")
    else:
        db = pi_system.Databases.Add(AF_DB_NAME)
        print(f"  [OK]   Database '{AF_DB_NAME}' dibuat")

    # Buat root element "Rotating Equipment"
    print(f"\n  Membuat hierarki elemen...")
    root_name = "Rotating Equipment"
    if db.Elements.Contains(root_name):
        root = db.Elements[root_name]
        print(f"  [SKIP] Element '{root_name}' sudah ada")
    else:
        root = db.Elements.Add(root_name)
        root.Description = "Rotating Equipment Assets"
        print(f"  [OK]   Element '{root_name}' dibuat")

    # Connect ke PI DA untuk resolve tags
    pi_servers = AFPI.PIServers()
    pi_server  = pi_servers[PI_SERVER_NAME]
    pi_server.Connect()

    # Buat child elements per aset
    for asset in ASSETS:
        print(f"\n  → {asset['name']}")

        if root.Elements.Contains(asset["name"]):
            el = root.Elements[asset["name"]]
            print(f"    [SKIP] Element sudah ada")
        else:
            el = root.Elements.Add(asset["name"])
            el.Description = asset["description"]
            print(f"    [OK]   Element dibuat")

        # Buat attributes dan link ke PI Tag
        for attr_def in asset["attributes"]:
            attr_name = attr_def["name"]
            tag_name  = attr_def["tag"]

            if el.Attributes.Contains(attr_name):
                print(f"      [SKIP] Attribute '{attr_name}' sudah ada")
                continue

            try:
                attr = el.Attributes.Add(attr_name)
                attr.Description = f"PI Tag: {tag_name}"

                # Set data reference ke PI Point
                dr_plugin = pi_system.DataReferencePlugIns["PI Point"]
                attr.DataReferencePlugIn = dr_plugin
                attr.ConfigString = f"\\\\{PI_SERVER_NAME}\\{tag_name};ReadOnly=False"

                print(f"      [OK]   '{attr_name}' → {tag_name}")
            except Exception as e:
                print(f"      [ERR]  '{attr_name}' — {e}")

    # Simpan ke AF Server
    try:
        db.CheckIn()
        print(f"\n  {'─'*55}")
        print(f"  PI AF Hierarchy berhasil dibuat!")
        print(f"  Buka PI System Explorer (PSE) untuk verifikasi.")
        print(f"  Database: {AF_DB_NAME}")
        print(f"\n  Lanjut: py -3.11 -m streamlit run C:\\PI_Demo\\streamlit_app.py")
        print(f"  {'─'*55}\n")
    except Exception as e:
        print(f"  [ERROR] CheckIn gagal: {e}")

if __name__ == "__main__":
    main()
