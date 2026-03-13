import argparse
import datetime as dt
import requests


def main() -> None:
    ap = argparse.ArgumentParser(description="Simulate eSSL ADMS attendance push")
    ap.add_argument("--server", default="http://localhost:8000", help="Backend base URL")
    ap.add_argument("--pin", required=True, help="Employee PIN/UserID")
    ap.add_argument("--name", default="", help="Employee name (optional)")
    args = ap.parse_args()

    now = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"PIN={args.pin}\tName={args.name}\tDateTime={now}\tStatus=0\tVerify=1\tWorkCode=0"
    url = args.server.rstrip("/") + "/iclock/cdata"
    r = requests.post(url, data=line.encode("utf-8"))
    print("POST", url, "->", r.status_code, r.text[:200])


if __name__ == "__main__":
    main()

