"use client";

export default function KPICards() {
  const cards = [
    {
      label: "APNG Files",
      value: "128",
      change: "+12%",
    },
    {
      label: "Successful Uploads",
      value: "96.8%",
      change: "+4.2%",
    },
    {
      label: "Active Users",
      value: "42",
      change: "+8",
    },
    {
      label: "Blocked Requests",
      value: "17",
      change: "-6%",
    },
  ];

  return (
    <div className="kpi-grid">
      {cards.map((card) => (
        <div
          className="kpi-card"
          key={card.label}
        >
          <p>
            {card.label}
          </p>

          <div className="kpi-row">
            <h3>
              {card.value}
            </h3>

            <span>
              {card.change}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}