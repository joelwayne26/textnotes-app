"use client";

import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";
import { useRouter } from "next/navigation";

export const metadata: Metadata = {
  title: "Notes App — Personal Knowledge Base",
  description: "Modern notes app built with Next.js 14, Flask, and PostgreSQL",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();

  const handleNewNote = () => {
    // Navigate to create a new note (will be handled by notes page)
    // For now, navigate to notes page which has create functionality
    window.location.href = "/notes?new=true";
  };

  return (
    <html lang="en">
      <body className="min-h-screen antialiased bg-gray-50">
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar - includes New Note button */}
          <Sidebar onNewNote={handleNewNote} />
          
          {/* Main Content Area */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Top Header */}
            <Header />
            
            {/* Page Content */}
            <main className="flex-1 overflow-y-auto">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
