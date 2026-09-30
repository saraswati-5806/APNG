"use client";

import { useEffect, useState } from "react";
import { get, post } from "../lib/api-client";

const names = {
  overview: "Network Overview",
  alerts: "Security Alerts",
  topology: "Network Topology",
  threats: "Threat Intelligence",
  remediation: "Remediation Queue",
};

function formatSize(bytes) {
  if (bytes === 0) return "0 Bytes";

  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));

  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
}

export default function Home() {
  const [activePage, setActivePage] = useState("overview");
  const [selectedFile, setSelectedFile] = useState(null);
  const [scanStatus, setScanStatus] = useState("");
  const [scanning, setScanning] = useState(false);
  const [result, setResult] = useState(false);
  const [toastMessage, setToastMessage] = useState("");
  const [alerts, setAlerts] = useState([]);
  const [remediationActions, setRemediationActions] = useState({});
  const [alertLoadError, setAlertLoadError] = useState("");
  const [iocs, setIocs] = useState([]);
  const [iocLoadError, setIocLoadError] = useState("");

  async function loadAlerts() {
    try {
      setAlertLoadError("");
      const data = await get("/api/alerts/");
      setAlerts(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to load alerts:", error);
      setAlertLoadError("Unable to load alerts from APNG backend.");
    }
  }

  async function loadIOCs() {
    try {
      setIocLoadError("");
      const data = await get("/api/ioc/");
      setIocs(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Failed to load IoCs:", error);
      setIocLoadError("Unable to load threat intelligence from APNG backend.");
    }
  }

  useEffect(() => {
    loadAlerts();

    if (activePage === "threats") {
      loadIOCs();
    }
  }, [activePage]);

  function showToast(message) {
    setToastMessage(message);

    setTimeout(() => {
      setToastMessage("");
    }, 2200);
  }

  function go(id) {
    setActivePage(id);
    window.scrollTo(0, 0);
  }

  function fileSelected(event) {
    const file = event.target.files?.[0];

    if (!file) return;

    setSelectedFile(file);
    setResult(false);
    setScanStatus("✓ File ready for scanning");

    showToast("File added successfully");
  }

  function startScan() {
    if (!selectedFile || scanning) {
      if (!selectedFile) {
        showToast("Please add a file first");
      }

      return;
    }

    setScanning(true);
    setResult(false);
    setScanStatus("⟳ Scanning file... 0%");

    let progress = 0;

    const scanner = setInterval(() => {
      progress += 10;

      setScanStatus(`⟳ Scanning file... ${progress}%`);

      if (progress >= 100) {
        clearInterval(scanner);

        setScanStatus("✓ Scan completed successfully");
        setResult(true);
        setScanning(false);

        showToast("Scan completed");
      }
    }, 250);
  }

  async function requestRemediation(alert) {
    try {
      const data = await post("/api/remediate/", {
        alert_id: alert.alert_id,
        action_type: alert.recommended_action,
      });

      setRemediationActions((prev) => ({
        ...prev,
        [alert.alert_id]: data,
      }));

      showToast("Remediation request created");
    } catch (error) {
      console.error("Failed to create remediation:", error);
      showToast("Failed to create remediation request");
    }
  }

  async function confirmRemediation(alert) {
    const action = remediationActions[alert.alert_id];

    if (!action?.action_id) {
      showToast("No pending remediation action");
      return;
    }

    const confirmedBy = window.prompt(
      "Confirm remediation as:",
      "admin"
    );

    if (!confirmedBy) return;

    try {
      await post(
        `/api/remediate/${action.action_id}/confirm`,
        {
          confirmed_by: confirmedBy,
        }
      );

      const updatedAlerts = await get("/api/alerts/");
      setAlerts(updatedAlerts);

      setRemediationActions((prev) => {
        const updated = { ...prev };
        delete updated[alert.alert_id];
        return updated;
      });

      showToast("Remediation confirmed");
    } catch (error) {
      console.error("Failed to confirm remediation:", error);
      showToast("Failed to confirm remediation");
    }
  }

  return (
    <>
      <div className="app">

        {/* SIDEBAR */}
        <aside className="side">
          <div className="logo">
            <div className="logoIcon">A</div>

            <div>
              <b>APNG</b>
              <small>AUTONOMOUS GUARDIAN</small>
            </div>
          </div>

          <nav className="nav">

            <button
              className={activePage === "overview" ? "on" : ""}
              onClick={() => go("overview")}
            >
              ◈ <span>Overview</span>
            </button>

            <button
              className={activePage === "alerts" ? "on" : ""}
              onClick={() => go("alerts")}
            >
              ⚠ <span>Security Alerts</span>
            </button>

            <button
              className={activePage === "topology" ? "on" : ""}
              onClick={() => go("topology")}
            >
              ◎ <span>Network Topology</span>
            </button>

            <button
              className={activePage === "threats" ? "on" : ""}
              onClick={() => go("threats")}
            >
              ⌁ <span>Threat Intelligence</span>
            </button>

            <button
              className={activePage === "remediation" ? "on" : ""}
              onClick={() => go("remediation")}
            >
              ✓ <span>Remediation</span>
            </button>

          </nav>
        </aside>

        {/* MAIN */}
        <main>

          {/* HEADER */}
          <header>
            <div>
              <div className="ey">
                SECURITY OPERATIONS CENTER
              </div>

              <h1>{names[activePage]}</h1>
            </div>

            <div>
              <span className="status">
                <i></i>
                Local services online
              </span>
            </div>
          </header>

          {/* OVERVIEW */}
          {activePage === "overview" && (
            <section className="page show">

              <div className="hero">

                <div>
                  <span className="chip">
                    ● READY TO SCAN
                  </span>

                  <h2>
                    Scan the file.
                    <br />
                    <em>Understand the threat.</em>
                  </h2>

                  <p>
                    APNG is an offline-first predictive
                    network guardian for analyzing network
                    and security data locally. Add a file
                    and start the scan.
                  </p>
                </div>

                <div className="radar">
                  <div className="scan"></div>

                  <div className="core">
                    APNG
                  </div>
                </div>

              </div>

              {/* UPLOAD */}
              <div className="upload">

                <h3>
                  Add a file to start scanning
                </h3>

                <p>
                  Select a PCAP, PCAPNG, LOG, JSON or TXT file.
                </p>

                <input
                  type="file"
                  id="fileInput"
                  className="fileInput"
                  accept=".pcap,.pcapng,.log,.json,.txt"
                  onChange={fileSelected}
                />

                <label
                  htmlFor="fileInput"
                  className="addFile"
                >
                  ＋ Add File
                </label>

                <button
                  className="scanBtn"
                  onClick={startScan}
                  disabled={!selectedFile || scanning}
                >
                  ⟳ Scan File
                </button>

                {selectedFile && (
                  <div
                    className="fileName"
                    style={{ display: "block" }}
                  >
                    Selected file: {selectedFile.name} (
                    {formatSize(selectedFile.size)})
                  </div>
                )}

                <div className="scanStatus">
                  {scanStatus}
                </div>

              </div>

              {/* RESULT */}
              {result && (
                <div className="result show">

                  <div className="resultHeader">

                    <h3>
                      Scan Result
                    </h3>

                    <span className="safe">
                      ✓ Scan Complete
                    </span>

                  </div>

                  <div className="resultGrid">

                    <div className="resultBox">
                      <label>FILE</label>

                      <strong>
                        {selectedFile?.name || "-"}
                      </strong>
                    </div>

                    <div className="resultBox">
                      <label>STATUS</label>

                      <strong className="green">
                        ANALYZED
                      </strong>
                    </div>

                    <div className="resultBox">
                      <label>SCAN ENGINE</label>

                      <strong>
                        APNG Local
                      </strong>
                    </div>

                  </div>

                </div>
              )}

            </section>
          )}

          {/* SECURITY ALERTS */}
          {activePage === "alerts" && (
            <section className="page show">

              <div className="title">

                <div>
                  <div className="ey">
                    DETECTION CENTER
                  </div>

                  <h2>
                    Security Alerts
                  </h2>
                </div>

              </div>

              <div className="panel">

                {alerts.length === 0 ? (
                  <p className="meta">
                    No alerts available.
                  </p>
                ) : (
                  <div>
                    {alerts.map((alert) => (
                      <div key={alert.alert_id}>

                        <h3>{alert.alert_id}</h3>

                        <p>
                          Source IP: {alert.source?.ip}
                        </p>

                        <p>
                          Risk Level: {alert.risk_level}
                        </p>

                        <p>
                          Recommended Action:{" "}
                          {alert.recommended_action}
                        </p>

                        <p>
                          Status: {alert.status}
                        </p>

                      </div>
                    ))}
                  </div>
                )}

              </div>

            </section>
          )}

          {/* NETWORK TOPOLOGY */}
          {activePage === "topology" && (
            <section className="page show">

              <div className="title">

                <div>
                  <div className="ey">
                    THREE.JS / WEBXR CONCEPT
                  </div>

                  <h2>
                    Network Topology
                  </h2>
                </div>

                <button
                  className="btn"
                  onClick={() =>
                    showToast("2D fallback enabled")
                  }
                >
                  2D Fallback
                </button>

              </div>

              <div className="topology">

                <div className="line l1"></div>
                <div className="line l2"></div>
                <div className="line l3"></div>
                <div className="line l4"></div>

                <div className="node center">
                  <b>APNG</b>
                  <small>ORCHESTRATOR</small>
                </div>

                <div className="node a">
                  <b>EDGE-04</b>
                  <small>NETWORK NODE</small>
                </div>

                <div className="node b">
                  <b>APP-03</b>
                  <small>APPLICATION</small>
                </div>

                <div className="node c">
                  <b>DB-01</b>
                  <small>DATABASE</small>
                </div>

                <div className="node d">
                  <b>WORKSTATION</b>
                  <small>ENDPOINT</small>
                </div>

                <div className="legend">

                  <span>
                    <i className="healthy"></i>
                    Healthy
                  </span>

                </div>

              </div>

            </section>
          )}

          {/* THREAT INTELLIGENCE */}
          {activePage === "threats" && (
            <section className="page show">

              <div className="title">

                <div>
                  <div className="ey">
                    ISAC-STYLE SHARING
                  </div>

                  <h2>
                    Threat Intelligence
                  </h2>
                </div>

                <button
                  className="btn primary"
                  onClick={() => {
                    loadIOCs();
                    showToast("IoC feed refreshed");
                  }}
                >
                  Refresh Feed
                </button>

              </div>

              <div className="panel">

                {iocLoadError && (
                  <p className="meta">
                    {iocLoadError}
                  </p>
                )}

                {iocs.length === 0 ? (
                  <p className="meta">
                    No IoCs available.
                  </p>
                ) : (
                  <div>
                    {iocs.map((ioc) => (
                      <div
                        key={ioc.ioc_id}
                        style={{
                          padding: "20px",
                          marginBottom: "16px",
                          border: "1px solid rgba(255,255,255,0.1)",
                          borderRadius: "10px",
                        }}
                      >
                        <h3>
                          {ioc.ioc_id || "Unknown IoC"}
                        </h3>

                        <p>
                          Type: {ioc.type || "N/A"}
                        </p>

                        <p>
                          Value: {ioc.value || "N/A"}
                        </p>

                        <p>
                          Confidence: {ioc.confidence || "N/A"}
                        </p>

                        <p>
                          First Seen: {ioc.first_seen || "N/A"}
                        </p>

                        <p>
                          Shared By: {ioc.shared_by_org_hash || "N/A"}
                        </p>

                        <p>
                          TLP: {ioc.tlp || "N/A"}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

              </div>

            </section>
          )}

          {/* REMEDIATION */}
          {activePage === "remediation" && (
            <section className="page show">

              <div className="title">

                <div>
                  <div className="ey">
                    HUMAN-IN-THE-LOOP
                  </div>

                  <h2>
                    Remediation Queue
                  </h2>
                </div>

                <button
                  className="btn"
                  onClick={loadAlerts}
                >
                  Refresh Queue
                </button>

              </div>

              <div className="panel">

                {alertLoadError && (
                  <p className="meta">
                    {alertLoadError}
                  </p>
                )}

                {alerts.filter(
                  (alert) =>
                    String(alert.status || "").trim() ===
                    "PENDING_CONFIRMATION"
                ).length === 0 ? (
                  <p className="meta">
                    No pending remediation actions.
                  </p>
                ) : (
                  <div>
                    {alerts
                      .filter(
                        (alert) =>
                          String(alert.status || "").trim() ===
                          "PENDING_CONFIRMATION"
                      )
                      .map((alert) => {
                        const action = remediationActions[alert.alert_id];

                        return (
                          <div
                            key={alert.alert_id}
                            style={{
                              padding: "20px",
                              marginBottom: "16px",
                              border: "1px solid rgba(255,255,255,0.1)",
                              borderRadius: "10px",
                            }}
                          >
                            <h3>{alert.alert_id}</h3>

                            <p>
                              Source IP: {alert.source?.ip || "N/A"}
                            </p>

                            <p>
                              Asset: {alert.source?.asset_name || "N/A"}
                            </p>

                            <p>
                              Action: {alert.recommended_action || "N/A"}
                            </p>

                            <p>
                              Status: {alert.status}
                            </p>

                            {!action ? (
                              <button
                                className="btn primary"
                                onClick={() => requestRemediation(alert)}
                              >
                                Request Remediation
                              </button>
                            ) : (
                              <button
                                className="btn primary"
                                onClick={() => confirmRemediation(alert)}
                              >
                                Confirm Remediation
                              </button>
                            )}
                          </div>
                        );
                      })}
                  </div>
                )}
              </div>

            </section>
          )}

        </main>

      </div>

      {/* TOAST */}
      <div
        className={`toast ${
          toastMessage ? "on" : ""
        }`}
      >
        {toastMessage}
      </div>
    </>
  );
}