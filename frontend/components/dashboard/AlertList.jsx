"use client";

export default function AlertList() {
  const alerts = [
    {
      title: "APNG upload activity detected",
      detail: "New file uploaded successfully",
      time: "2 min ago",
      type: "info",
    },
    {
      title: "Access request verified",
      detail: "User authentication completed",
      time: "12 min ago",
      type: "success",
    },
    {
      title: "Unusual request blocked",
      detail: "Request rejected by gateway",
      time: "28 min ago",
      type: "warning",
    },
  ];

  return (
    <section className="alert-card">
      <div className="alert-heading">
        <h2>Security Alerts</h2>

        <span className="alert-count">
          {alerts.length}
        </span>
      </div>

      <div>
        {alerts.map((alert, index) => (
          <div
            className="alert-item"
            key={index}
          >
            <div
              className={`alert-icon ${alert.type}`}
            >
              {alert.type === "success"
                ? "✓"
                : alert.type === "warning"
                ? "!"
                : "i"}
            </div>

            <div className="alert-content">
              <strong>
                {alert.title}
              </strong>

              <p>
                {alert.detail}
              </p>

              <span>
                {alert.time}
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}