import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MealPlannerAI - AI-Powered Meal Planning",
  description: "Generate personalized weekly meal plans with smart recipes, automatic grocery lists, and nutrition tracking. Save time, eat better, and reduce food waste.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
