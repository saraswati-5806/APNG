"use client";

import KPICards from "./KPICards";
import AlertList from "./AlertList";
import Timeline from "./Timeline";
import NetworkTopology from "../ar-topology/NetworkTopology";

export default function Dashboard() {
  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <p className="dashboard-eyebrow">
            APNG SECURITY PLATFORM
          </p>

          <h1>
            Dashboard
          </h1>

          <p className="dashboard-subtitle">
            Monitor APNG activity, access and
            security events.
          </p>
        </div>

        <div className="system-status">
          <span></span>
          System Online
        </div>
      </div>

      <KPICards />

      <div className="dashboard-grid">
        <NetworkTopology />

        <AlertList />
      </div>

      <Timeline />
    </div>
  );
}