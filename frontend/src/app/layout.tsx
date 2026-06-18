import "./globals.css";

export const metadata = {
  title: "Shiksha Sahayak – AI Teaching Assistant",
  description: "JULI-E: An AI-powered teaching assistant with 3D avatar, voice interaction, and hands-free mode for modern classrooms.",
  icons: {
    icon: "/icon.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
