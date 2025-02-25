import React from "react";
import Head from "next/head";

const OnlineVeterinaryOffice: React.FC = () => {
  const containerStyle: React.CSSProperties = {
    margin: 0,
    padding: 0,
    fontFamily: "Arial, sans-serif",
    backgroundColor: "#f9f9f9",
  };

  const innerContainerStyle: React.CSSProperties = {
    maxWidth: "600px",
    margin: "40px auto",
    padding: "20px",
    backgroundColor: "#ffffff",
    borderRadius: "6px",
    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
  };

  const titleStyle: React.CSSProperties = {
    color: "#333",
    textAlign: "center",
    marginBottom: "20px",
  };

  const illustrationsStyle: React.CSSProperties = {
    display: "flex",
    flexWrap: "wrap",
    justifyContent: "center",
    gap: "20px",
    marginBottom: "20px",
  };

  const svgStyle: React.CSSProperties = {
    width: "180px",
    height: "auto",
    border: "1px solid #ccc",
    borderRadius: "5px",
    backgroundColor: "#fff",
  };

  const inputStyle: React.CSSProperties = {
    width: "70%",
    padding: "10px",
    marginRight: "10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
    fontSize: "14px",
  };

  const buttonStyle: React.CSSProperties = {
    padding: "10px 20px",
    border: "none",
    borderRadius: "5px",
    backgroundColor: "#4CAF50",
    color: "#fff",
    fontSize: "14px",
    cursor: "pointer",
  };

  const resultsStyle: React.CSSProperties = {
    marginTop: "20px",
    backgroundColor: "#fafafa",
    padding: "15px",
    borderRadius: "5px",
    border: "1px solid #ddd",
  };

  return (
    <div>
      <Head>
        <title>Online Veterinary Office</title>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div style={containerStyle}>
        <div style={innerContainerStyle}>
          <h1 style={titleStyle}>Online Veterinary Office</h1>
          <div style={illustrationsStyle}>
            {/* Illustration 1 */}
            <svg
              style={svgStyle}
              version="1.1"
              viewBox="0 0 400 300"
              xmlns="http://www.w3.org/2000/svg"
            >
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
              <circle cx="220" cy="170" r="20" fil
