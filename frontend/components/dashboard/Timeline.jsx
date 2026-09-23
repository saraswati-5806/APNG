"use client";

export default function Timeline() {
  const events = [
    {
      title: "APNG uploaded",
      description:
        "animated-image.apng was uploaded",
      time: "10:42 PM",
    },
    {
      title: "User authenticated",
      description:
        "Authentication completed successfully",
      time: "10:31 PM",
    },
    {
      title: "Gateway request approved",
      description:
        "Request passed security checks",
      time: "10:18 PM",
    },
    {
      title: "Security scan completed",
      description:
        "No critical issues detected",
      time: "09:55 PM",
    },
  ];

  return (
    <section className="timeline-card">
      <h2>Activity Timeline</h2>

      <div className="timeline">
        {events.map((event, index) => (
          <div
            className="timeline-item"
            key={index}
          >
            <div className="timeline-dot"></div>

            <div className="timeline-content">
              <div className="timeline-top">
                <strong>
                  {event.title}
                </strong>

                <span>
                  {event.time}
                </span>
              </div>

              <p>
                {event.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}