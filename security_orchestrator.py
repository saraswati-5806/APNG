import os
import time
import json
import fakeredis
from llm_engine.ollama_client import generate_guidance
from llm_engine.log_parser import parse_raw_log
from threat_intel.sync_service import ISACSyncService

# Use in-memory fakeredis to bypass Docker/Redis connection requirements
r = fakeredis.FakeRedis()
isac_node = ISACSyncService(node_id="apng_security_node_01")

def run_security_pipeline():
    print("[*] APNG Security Orchestrator started (Air-gapped / Local Mode).")
    
    # Pre-seed a test anomaly into the stream so the loop catches it immediately
    r.xadd("apng_telemetry", {b"sensor": b"edge-switch-04", b"status": b"anomaly", b"details": b"Unauthorized port scan detected"})

    while True:
        try:
            streams = r.xread({"apng_telemetry": "0"}, count=5, block=3000)
            if not streams:
                time.sleep(1)
                continue

            for stream, messages in streams:
                for message_id, data in messages:
                    print(f"\n[!] Telemetry Event Received [{message_id}]: {data}")
                    
                    status = data.get(b"status", b"normal").decode("utf-8")
                    sensor = data.get(b"sensor", b"unknown-sensor").decode("utf-8")
                    
                    if status == "anomaly":
                        print(f"[!] Anomaly detected on sensor {sensor}. Triggering Local LLM analysis...")
                        
                        alert_context = f"Anomaly detected on sensor {sensor} with high severity risk rating."
                        log_excerpt = json.dumps({k.decode(): v.decode() for k, v in data.items()})
                        
                        ai_recommendation = generate_guidance(alert_context, log_excerpt)
                        print(f"\n--- Ollama Security Guidance ---\n{ai_recommendation}\n--------------------------------")
                        
                        mock_ioc = {
                            "ioc_id": f"IOC-{message_id.decode()}",
                            "type": "telemetry_anomaly",
                            "value": sensor,
                            "confidence": "HIGH",
                            "first_seen": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "shared_by_org_hash": "apng_local_node",
                            "tlp": "AMBER"
                        }
                        isac_node.publish_ioc(mock_ioc)
            break # Exit loop after processing for test verification
        except Exception as e:
            print(f"[-] Error in security orchestration loop: {e}")
            break

if __name__ == "__main__":
    run_security_pipeline()