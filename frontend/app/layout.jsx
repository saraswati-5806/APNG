import "./globals.css";

export const metadata = {
  title: "APNG Guardian",
  description: "APNG Security and Management Platform",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}