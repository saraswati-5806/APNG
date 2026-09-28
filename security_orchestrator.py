import os
import time
import json
import fakeredis

from llm_engine.ollama_client import generate_guidance
from llm_engine.log_parser import parse_raw_log
from threat_intel.sync_service import ISACSyncService
from ml_engine.scorer import predict


# Use in-memory fakeredis to bypass Docker/Redis connection requirements
r = fakeredis.FakeRedis()
isac_node = ISACSyncService(node_id="apng_security_node_01")


def run_security_pipeline():
    print("[*] APNG Security Orchestrator started (Air-gapped / Local Mode).")

    # Pre-seed a test anomaly into the stream so the loop catches it immediately
    r.xadd(
        "apng_telemetry",
        {
            b"sensor": b"edge-switch-04",
            b"source_ip": b"10.0.4.55",
            b"status": b"anomaly",
            b"details": b"Unauthorized port scan detected",

            # 11 ML features
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

                        # ==========================================
                        # ML ENGINE
                        # ==========================================

                        ml_features = {
                            "Flow Duration": float(
                                data[b"Flow Duration"].decode("utf-8")
                            ),
                            "Total Fwd Packets": float(
                                data[b"Total Fwd Packets"].decode("utf-8")
                            ),
                            "Total Backward Packets": float(
                                data[b"Total Backward Packets"].decode("utf-8")
                            ),
                            "Total Length of Fwd Packets": float(
                                data[
                                    b"Total Length of Fwd Packets"
                                ].decode("utf-8")
                            ),
                            "Total Length of Bwd Packets": float(
                                data[
                                    b"Total Length of Bwd Packets"
                                ].decode("utf-8")
                            ),
                            "Flow Bytes/s": float(
                                data[b"Flow Bytes/s"].decode("utf-8")
                            ),
                            "Flow Packets/s": float(
                                data[b"Flow Packets/s"].decode("utf-8")
                            ),
                            "Packet Length Mean": float(
                                data[
                                    b"Packet Length Mean"
                                ].decode("utf-8")
                            ),
                            "Packet Length Std": float(
                                data[
                                    b"Packet Length Std"
                                ].decode("utf-8")
                            ),
                            "SYN Flag Count": float(
                                data[b"SYN Flag Count"].decode("utf-8")
                            ),
                            "ACK Flag Count": float(
                                data[b"ACK Flag Count"].decode("utf-8")
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

                        # ==========================================
                        # LOCAL LLM ANALYSIS
                        # ==========================================

                        print(
                            "[*] Triggering Local LLM analysis..."
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

                        ai_recommendation = generate_guidance(
                            alert_context,
                            log_excerpt
                        )

                        print(
                            "\n--- Ollama Security Guidance ---"
                        )
                        print(ai_recommendation)
                        print(
                            "--------------------------------"
                        )

                        # ==========================================
                        # IOC SHARING
                        # ==========================================

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

            # Exit after processing one test batch
            break

        except Exception as e:
            print(
                f"[-] Error in security orchestration loop: {e}"
            )
            break


if __name__ == "__main__":
    run_security_pipeline()