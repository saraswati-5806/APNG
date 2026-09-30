import os
import time
import json
import getpass
import requests
import fakeredis

from llm_engine.ollama_client import generate_guidance
from llm_engine.log_parser import parse_raw_log
from threat_intel.sync_service import ISACSyncService
from ml_engine.scorer import predict


# Use in-memory fakeredis to bypass Docker/Redis connection requirements
r = fakeredis.FakeRedis()
isac_node = ISACSyncService(node_id="apng_security_node_01")


def send_alert_to_backend(data, llm_explanation):
    username = os.getenv("APNG_USERNAME") or input(
        "Backend username: "
    )

    password = os.getenv("APNG_PASSWORD") or getpass.getpass(
        "Backend password: "
    )

    login = requests.post(
        "http://127.0.0.1:8000/api/auth/login",
        data={
            "username": username,
            "password": password,
        },
        timeout=10,
    )

    if login.status_code != 200:
        print(f"[-] Backend login failed: {login.status_code}")
        print(login.text)
        return

    token = login.json()["access_token"]

    payload = {
        "sensor": data[b"sensor"].decode("utf-8"),
        "source_ip": data[b"source_ip"].decode("utf-8"),
        "asset_name": data[b"sensor"].decode("utf-8"),
        "status": data[b"status"].decode("utf-8"),
        "details": llm_explanation,

        "flow_duration": float(
            data[b"Flow Duration"].decode("utf-8")
        ),
        "total_fwd_packets": float(
            data[b"Total Fwd Packets"].decode("utf-8")
        ),
        "total_backward_packets": float(
            data[b"Total Backward Packets"].decode("utf-8")
        ),
        "total_length_fwd_packets": float(
            data[b"Total Length of Fwd Packets"].decode("utf-8")
        ),
        "total_length_bwd_packets": float(
            data[b"Total Length of Bwd Packets"].decode("utf-8")
        ),
        "flow_bytes_per_sec": float(
            data[b"Flow Bytes/s"].decode("utf-8")
        ),
        "flow_packets_per_sec": float(
            data[b"Flow Packets/s"].decode("utf-8")
        ),
        "packet_length_mean": float(
            data[b"Packet Length Mean"].decode("utf-8")
        ),
        "packet_length_std": float(
            data[b"Packet Length Std"].decode("utf-8")
        ),
        "syn_flag_count": float(
            data[b"SYN Flag Count"].decode("utf-8")
        ),
        "ack_flag_count": float(
            data[b"ACK Flag Count"].decode("utf-8")
        ),
    }

    response = requests.post(
        "http://127.0.0.1:8000/api/telemetry/ingest",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}"
        },
        timeout=30,
    )

    print(
        f"[+] Backend telemetry response: "
        f"{response.status_code}"
    )
    print(
        f"[+] Backend alert response: "
        f"{response.text}"
    )


def run_security_pipeline():
    print(
        "[*] APNG Security Orchestrator started "
        "(Air-gapped / Local Mode)."
    )

    r.xadd(
        "apng_telemetry",
        {
            b"sensor": b"edge-switch-04",
            b"source_ip": b"10.0.4.55",
            b"status": b"anomaly",
            b"details": b"Unauthorized port scan detected",

            b"Flow Duration": b"1000",
            b"Total Fwd Packets": b"10",
            b"Total Backward Packets": b"8",
            b"Total Length of Fwd Packets": b"500",
            b"Total Length of Bwd Packets": b"400",
            b"Flow Bytes/s": b"900",
            b"Flow Packets/s": b"18",
            b"Packet Length Mean": b"50",
            b"Packet Length Std": b"10",
            b"SYN Flag Count": b"1",
            b"ACK Flag Count": b"1",
        },
    )

    while True:
        try:
            streams = r.xread(
                {"apng_telemetry": "0"},
                count=5,
                block=3000,
            )

            if not streams:
                time.sleep(1)
                continue

            for stream, messages in streams:
                for message_id, data in messages:
                    print(
                        f"\n[!] Telemetry Event Received "
                        f"[{message_id}]: {data}"
                    )

                    status = data.get(
                        b"status",
                        b"normal"
                    ).decode("utf-8")

                    sensor = data.get(
                        b"sensor",
                        b"unknown-sensor"
                    ).decode("utf-8")

                    if status == "anomaly":
                        print(
                            f"[!] Anomaly detected on sensor {sensor}."
                        )

                        ml_features = {
                            "Flow Duration": float(
                                data[b"Flow Duration"].decode()
                            ),
                            "Total Fwd Packets": float(
                                data[b"Total Fwd Packets"].decode()
                            ),
                            "Total Backward Packets": float(
                                data[b"Total Backward Packets"].decode()
                            ),
                            "Total Length of Fwd Packets": float(
                                data[
                                    b"Total Length of Fwd Packets"
                                ].decode()
                            ),
                            "Total Length of Bwd Packets": float(
                                data[
                                    b"Total Length of Bwd Packets"
                                ].decode()
                            ),
                            "Flow Bytes/s": float(
                                data[b"Flow Bytes/s"].decode()
                            ),
                            "Flow Packets/s": float(
                                data[b"Flow Packets/s"].decode()
                            ),
                            "Packet Length Mean": float(
                                data[b"Packet Length Mean"].decode()
                            ),
                            "Packet Length Std": float(
                                data[b"Packet Length Std"].decode()
                            ),
                            "SYN Flag Count": float(
                                data[b"SYN Flag Count"].decode()
                            ),
                            "ACK Flag Count": float(
                                data[b"ACK Flag Count"].decode()
                            ),
                        }

                        ml_result = predict(ml_features)

                        print(
                            f"[+] ML prediction: "
                            f"{ml_result['prediction']}"
                        )
                        print(
                            f"[+] ML anomaly score: "
                            f"{ml_result['anomaly_score']}"
                        )

                        alert_context = (
                            f"Anomaly detected on sensor {sensor}. "
                            f"ML prediction: "
                            f"{ml_result['prediction']}. "
                            f"Anomaly score: "
                            f"{ml_result['anomaly_score']:.6f}."
                        )

                        log_excerpt = json.dumps(
                            {
                                k.decode(): v.decode()
                                for k, v in data.items()
                            }
                        )

                        print("[*] Triggering Local LLM analysis...")

                        ai_recommendation = generate_guidance(
                            alert_context,
                            log_excerpt,
                        )

                        print(
                            "\n--- Ollama Security Guidance ---"
                        )
                        print(ai_recommendation)
                        print(
                            "--------------------------------"
                        )

                        # Send the complete event to FastAPI
                        send_alert_to_backend(
                            data,
                            ai_recommendation,
                        )

                        mock_ioc = {
                            "ioc_id": f"IOC-{message_id.decode()}",
                            "type": "telemetry_anomaly",
                            "value": sensor,
                            "confidence": "HIGH",
                            "first_seen": time.strftime(
                                "%Y-%m-%dT%H:%M:%SZ"
                            ),
                            "shared_by_org_hash": "apng_local_node",
                            "tlp": "AMBER",
                        }

                        isac_node.publish_ioc(mock_ioc)

            break

        except Exception as e:
            print(
                f"[-] Error in security orchestration loop: {e}"
            )
            break


if __name__ == "__main__":
    run_security_pipeline()