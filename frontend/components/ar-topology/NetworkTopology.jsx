"use client";

export default function NetworkTopology() {
  const nodes = [
    {
      id: "user",
      label: "User",
      x: 80,
      y: 130,
    },
    {
      id: "gateway",
      label: "APNG Gateway",
      x: 260,
      y: 130,
    },
    {
      id: "service",
      label: "APNG Service",
      x: 470,
      y: 70,
    },
    {
      id: "storage",
      label: "Storage",
      x: 470,
      y: 190,
    },
  ];

  return (
    <section className="network-card">
      <div className="network-header">
        <div>
          <h2>Network Topology</h2>

          <p>
            APNG application access overview
          </p>
        </div>

        <span className="network-status">
          ● Protected
        </span>
      </div>

      <div className="network">
        <svg
          viewBox="0 0 560 260"
          width="100%"
          height="260"
        >
          <line
            x1="115"
            y1="130"
            x2="225"
            y2="130"
            className="network-line"
          />

          <line
            x1="295"
            y1="120"
            x2="435"
            y2="75"
            className="network-line"
          />

          <line
            x1="295"
            y1="140"
            x2="435"
            y2="185"
            className="network-line"
          />

          {nodes.map((node) => (
            <g key={node.id}>
              <circle
                cx={node.x}
                cy={node.y}
                r="32"
                className="network-node"
              />

              <text
                x={node.x}
                y={node.y + 5}
                textAnchor="middle"
                className="node-text"
              >
                {node.id === "gateway"
                  ? "GATEWAY"
                  : node.label}
              </text>

              <text
                x={node.x}
                y={node.y + 55}
                textAnchor="middle"
                className="node-label"
              >
                {node.label}
              </text>
            </g>
          ))}
        </svg>
      </div>
    </section>
  );
}