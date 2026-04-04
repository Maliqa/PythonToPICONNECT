import time
import requests
import json
import random
import urllib3
from datetime import datetime

urllib3.disable_warnings()

# === KONFIGURASI ===
PI_WEBAPI_URL  = "https://PISRVCISDEMO/piwebapi"
PI_TAG_NAME    = "TEST_OPC"
PI_SERVER_NAME = "PISRVCISDEMO"
PI_USERNAME    = "piadmin"
PI_PASSWORD    = "piadmin"  # ganti password lo
SCAN_INTERVAL  = 5

# === SESSION ===
session = requests.Session()
session.auth = (PI_USERNAME, PI_PASSWORD)
session.verify = False
session.headers.update({"Content-Type": "application/json"})

def get_webid():
    url = PI_WEBAPI_URL + "/points"
    params = {"path": "\\\\" + PI_SERVER_NAME + "\\" + PI_TAG_NAME}
    r = session.get(url, params=params)
    if r.status_code == 200:
        wid = r.json().get("WebId")
        print("[OK] WebID: " + str(wid))
        return wid
    else:
        print("[ERROR] Get WebID gagal: " + str(r.status_code))
        print(r.text)
        return None

def write_value(web_id, value):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    url = PI_WEBAPI_URL + "/streams/" + web_id + "/value"
    payload = {"Timestamp": ts, "Value": value, "Good": True}
    r = session.post(url, data=json.dumps(payload))
    return r.status_code in [200, 202, 204], ts

def main():
    print("=== OPC Simulation -> PI Web API ===")
    print("Tag: " + PI_TAG_NAME)
    print("Server: " + PI_SERVER_NAME)
    print("Interval: " + str(SCAN_INTERVAL) + " detik")
    print("====================================")

    web_id = get_webid()
    if not web_id:
        print("FATAL: WebID tidak dapat diambil. Cek tag name dan PI Web API.")
        return

    print("\nMulai kirim data... (Ctrl+C untuk stop)\n")
    count = 0

    while True:
        try:
            value = round(random.uniform(0, 32767), 4)
            ok, ts = write_value(web_id, value)
            count += 1
            status = "OK" if ok else "GAGAL"
            print("[" + ts + "] Value: " + str(value) + " -> " + status + " (#" + str(count) + ")")
            time.sleep(SCAN_INTERVAL)
        except KeyboardInterrupt:
            print("\nSelesai. Total kiriman: " + str(count))
            break
        except Exception as e:
            print("[ERROR] " + str(e))
            time.sleep(SCAN_INTERVAL)

main()
