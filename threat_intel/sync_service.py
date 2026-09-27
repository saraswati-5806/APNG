import requests

class ISACSyncService:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.local_cache = []

    def publish_ioc(self, ioc_data: dict) -> bool:
        """Publishes a local confirmed IoC bundle to ISAC peers."""
        print(f"[+] Publishing IoC {ioc_data.get('ioc_id')} from node {self.node_id}")
        self.local_cache.append(ioc_data)
        return True

    def sync_from_partner(self, partner_endpoint: str) -> list:
        """Pulls the latest IoC bundle from a partner node endpoint."""
        try:
            response = requests.get(f"{partner_endpoint}/api/ioc", timeout=5)
            if response.status_code == 200:
                bundles = response.json()
                print(f"[+] Successfully synced {len(bundles)} IoCs from partner node.")
                return bundles
        except Exception as e:
            print(f"[-] Failed to sync from partner node (air-gapped fallback active): {e}")
        return []