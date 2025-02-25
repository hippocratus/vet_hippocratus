"use client";

import React, { useState } from "react";
import { searchVetInfo } from "@/utils/api";

export default function TestPage() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    try {
      const result = await searchVetInfo(query);
      setResponse(result);
    } catch (error) {
      console.error("Error fetching data:", error);
      setResponse("Failed to retrieve data.");
    }
    setLoading(false);
  };

  // -------- СТИЛИ (inline-styles) --------
  const outerContainerStyle: React.CSSProperties = {
    minHeight: "100vh",
    // Градиентный фон (слева-направо)
    background: "linear-gradient(to right, #b2f0e3, #fde2e4)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "30px",
    boxSizing: "border-box",
  };

  const cardStyle: React.CSSProperties = {
    width: "100%",
    maxWidth: "800px",
    backgroundColor: "#fff",
    borderRadius: "20px",
    boxShadow: "0 8px 20px rgba(0, 0, 0, 0.1)",
    padding: "40px",
    boxSizing: "border-box",
  };

  const titleStyle: React.CSSProperties = {
    textAlign: "center",
    fontSize: "2.2rem",
    fontWeight: 700,
    margin: 0,
    marginBottom: "10px",
    color: "#333",
  };

  const subtitleStyle: React.CSSProperties = {
    textAlign: "center",
    fontSize: "1.1rem",
    color: "#666",
    margin: 0,
    marginBottom: "30px",
  };

  const illustrationsContainerStyle: React.CSSProperties = {
    display: "flex",
    flexWrap: "wrap",
    gap: "20px",
    justifyContent: "center",
    marginBottom: "30px",
  };

  const svgStyle: React.CSSProperties = {
    width: "180px",
    height: "auto",
    backgroundColor: "#fff",
    borderRadius: "8px",
    boxShadow: "0 3px 8px rgba(0,0,0,0.1)",
  };

  const searchContainerStyle: React.CSSProperties = {
    display: "flex",
    flexWrap: "wrap",
    gap: "10px",
    marginBottom: "30px",
    justifyContent: "center",
  };

  const inputStyle: React.CSSProperties = {
    flex: "1 1 auto",
    minWidth: "200px",
    padding: "12px 16px",
    fontSize: "1rem",
    border: "1px solid #ccc",
    borderRadius: "8px",
    outline: "none",
  };

  const buttonStyle: React.CSSProperties = {
    padding: "12px 20px",
    fontSize: "1rem",
    border: "none",
    borderRadius: "8px",
    background: "linear-gradient(to right, #36c, #6cf)",
    color: "#fff",
    cursor: "pointer",
    boxShadow: "0 3px 8px rgba(0,0,0,0.15)",
  };

  const resultContainerStyle: React.CSSProperties = {
    backgroundColor: "#f8f8f8",
    padding: "20px",
    borderRadius: "8px",
    boxShadow: "inset 0 2px 6px rgba(0,0,0,0.05)",
  };

  const resultTitleStyle: React.CSSProperties = {
    fontSize: "1.2rem",
    margin: 0,
    marginBottom: "10px",
    color: "#333",
  };

  const resultTextStyle: React.CSSProperties = {
    margin: 0,
    whiteSpace: "pre-wrap",
    color: "#555",
    fontSize: "1rem",
  };

  // -------- РЕНДЕР КОМПОНЕНТА --------
  return (
    <div style={outerContainerStyle}>
      <div style={cardStyle}>
        <h1 style={titleStyle}>Veterinary Information Portal</h1>
        <p style={subtitleStyle}>
          Discover comprehensive veterinary information at your fingertips.
        </p>

        {/* Иллюстрации */}
        <div style={illustrationsContainerStyle}>
          {/* Иллюстрация 1 */}
          <svg style={svgStyle} viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#d3eaf2" />
            <rect x="140" y="100" width="120" height="80" fill="#ffd766" stroke="#444" strokeWidth="2" />
            <polygon points="140,100 200,60 260,100" fill="#a66e3a" />
            <circle cx="80" cy="80" r="20" fill="#f3d9c2" />
            <rect x="70" y="100" width="20" height="40" fill="#ffffff" />
            <rect x="66" y="100" width="28" height="10" fill="#ffffff" />
            <line x1="70" y1="140" x2="70" y2="150" stroke="#000" strokeWidth="2" />
            <line x1="90" y1="140" x2="90" y2="150" stroke="#000" strokeWidth="2" />
            <line x1="66" y1="110" x2="55" y2="100" stroke="#000" strokeWidth="2" />
            <line x1="94" y1="110" x2="105" y2="100" stroke="#000" strokeWidth="2" />
            <circle cx="220" cy="170" r="20" fill="#ffffff" stroke="#444" strokeWidth="2" />
            <circle cx="220" cy="195" r="15" fill="#ffffff" stroke="#444" strokeWidth="2" />
            <circle cx="215" cy="168" r="4" fill="#000" />
            <ellipse cx="225" cy="168" rx="2" ry="4" fill="#000" transform="rotate(20 225 168)" />
            <line x1="220" y1="185" x2="220" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="230" y1="185" x2="230" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="210" y1="200" x2="210" y2="215" stroke="#444" strokeWidth="2" />
            <line x1="220" y1="200" x2="220" y2="215" stroke="#444" strokeWidth="2" />
            <circle cx="270" cy="170" r="15" fill="#666" stroke="#444" strokeWidth="2" />
            <polygon points="265,157 260,150 270,155" fill="#444" />
            <polygon points="275,157 280,150 270,155" fill="#444" />
            <circle cx="270" cy="190" r="12" fill="#666" stroke="#444" strokeWidth="2" />
            <line x1="270" y1="178" x2="270" y2="185" stroke="#000" strokeWidth="2" />
            <line x1="265" y1="180" x2="275" y2="180" stroke="#000" strokeWidth="2" />
            <line x1="265" y1="195" x2="265" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="275" y1="195" x2="275" y2="205" stroke="#444" strokeWidth="2" />
            <line x1="282" y1="190" x2="290" y2="185" stroke="#444" strokeWidth="2" />
          </svg>

          {/* Иллюстрация 2 */}
          <svg style={svgStyle} viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="300" fill="#f0e6f6" />
            <rect x="120" y="90" width="160" height="90" fill="#ffae42" stroke="#444" strokeWidth="2" />
            <polygon points="120,90 200,40 280,90" fill="#c76e3a" />
            <circle cx="70" cy="70" r="20" fill="#f3d9c2" />
            <rect x="60" y="90" width="20" height="40" fill="#ffffff" />
            <rect x="56" y="90" width="28" height="10" fill="#ffffff" />
            <line x1="60" y1="130" x2="60" y2="140" stroke="#000" strokeWidth="2" />
            <line x1="80" y1="130" x2="80" y2="140" stroke="#000" strokeWidth="2" />
            <line x1="56" y1="100" x2="45" y2="110" stroke="#000" strokeWidth="2" />
            <line x1="84" y1="100" x2="95" y2="90" stroke="#000" strokeWidth="2" />
            <circle cx="230" cy="180" r="20" fill="#ffc" stroke="#444" strokeWidth="2" />
            <circle cx="230" cy="205" r="15" fill="#ffc" stroke="#444" strokeWidth="2" />
            <circle cx="225" cy="178" r="4" fill="#000" />
            <ellipse cx="235" cy="178" rx="2" ry="4" fill="#000" transform="rotate(20 235 178)" />
            <line x1="230" y1="195" x2="230" y2="215" stroke="#444" strokeWidth="2" />
            <line x1="240" y1="195" x2="240" y2="215" stroke="#444" strokeWidth="2" />
            <line x1="220" y1="210" x2="220" y2="225" stroke="#444" strokeWidth="2" />
            <line x1="230" y1="210" x2="230" y2="225" stroke="#444" strokeWidth="2" />
            <circle cx="280" cy="180" r="15" fill="#333" stroke="#444" strokeWidth="2" />
            <polygon points="275,167 270,160 280,165" fill="#444" />
            <polygon points="285,167 290,160 280,165" fill="#444" />
            <circle cx="280" cy="200" r="12" fill="#333" stroke="#444" strokeWidth="2" />
            <line x1="280" y1="188" x2="280" y2="195" stroke="#000" strokeWidth="2" />
            <line x1="275" y1="190" x
