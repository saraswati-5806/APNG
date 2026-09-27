from threat_intel.sync_service import ISACSyncService

# Initialize sync service for local node
sync_svc = ISACSyncService(node_id="team_apng_local")

# Test publishing a mock IoC bundle
mock_ioc = {
    "ioc_id": "IOC-9931",
    "type": "ip",
    "value": "203.0.113.55",
    "confidence": "HIGH",
    "first_seen": "2026-08-19T09:00:00Z",
    "shared_by_org_hash": "7f21a9",
    "tlp": "AMBER"
}

sync_svc.publish_ioc(mock_ioc)

# Test syncing from a non-existent partner node to verify air-gapped fallback error handling
fallback_result = sync_svc.sync_from_partner("http://localhost:9999")
print(f"[+] Air-gapped fallback result handled cleanly: {fallback_result == []}")