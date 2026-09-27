"use client";

import { useEffect, useState } from "react";
import { get } from "../lib/api-client";

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

  useEffect(() => {
    get("/api/alerts/")
      .then((data) => setAlerts(data))
      .catch((error) =>
        console.error("Failed to load alerts:", error)
      );
  }, []);

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
                  onClick={() =>
                    showToast("IoC sync started")
                  }
                >
                  Sync Feed
                </button>

              </div>

              <div className="panel">

                <p className="meta">
                  Threat intelligence results will
                  appear after a file is scanned.
                </p>

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

              </div>

              <div className="panel">

                <p className="meta">
                  No remediation actions available
                  until a threat is detected.
                </p>

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