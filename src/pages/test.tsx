import React from 'react';
import Head from 'next/head';

const OnlineVeterinaryOffice: React.FC = () => {
  const containerStyle: React.CSSProperties = {
    margin: 0,
    padding: 0,
    fontFamily: 'Arial, sans-serif',
    backgroundColor: '#f9f9f9',
  };

  const innerContainerStyle: React.CSSProperties = {
    maxWidth: '600px',
    margin: '40px auto',
    padding: '20px',
    backgroundColor: '#ffffff',
    borderRadius: '6px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
  };

  const titleStyle: React.CSSProperties = {
    color: '#333',
    textAlign: 'center',
    marginBottom: '20px',
  };

  const illustrationsStyle: React.CSSProperties = {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: '20px',
    marginBottom: '20px',
  };

  const svgStyle: React.CSSProperties = {
    width: '180px',
    height: 'auto',
    border: '1px solid #ccc',
    borderRadius: '5px',
    backgroundColor: '#fff',
  };

  const inputStyle: React.CSSProperties = {
    width: '70%',
    padding: '10px',
    marginRight: '10px',
    borderRadius: '5px',
    border: '1px solid #ccc',
    fontSize: '14px',
  };

  const buttonStyle: React.CSSProperties = {
    padding: '10px 20px',
    border: 'none',
    borderRadius: '5px',
    backgroundColor: '#4CAF50',
    color: '#fff',
    fontSize: '14px',
    cursor: 'pointer',
  };

  const resultsStyle: React.CSSProperties = {
    marginTop: '20px',
    backgroundColor: '#fafafa',
    padding: '15px',
    borderRadius: '5px',
    border: '1px solid #ddd',
  };

  return (
    <>
      <Head>
        <title>Online Veterinary Office</title>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <div style={containerStyle}>
        <div style={innerContainerStyle}>
          <h1 style={titleStyle}>Online Veterinary Office</h1>

          {/* Блок с иллюстрациями */}
          <div style={illustrationsStyle}>
            {/* Иллюстрация 1 */}
            <svg style={svgStyle} version="1.1" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
              {/* Background */}
              <rect width="400" height="300" fill="#d3eaf2" />
              {/* House */}
              <rect x="140" y="100" width="120" height="80" fill="#ffd766" stroke="#444" strokeWidth="2" />
              <polygon points="140,100 200,60 260,100" fill="#a66e3a" />
              {/* Vet */}
              <circle cx="80" cy="80" r="20" fill="#f3d9c2" />
              <rect x="70" y="100" width="20" height="40" fill="#ffffff" />
              <rect x="66" y="100" width="28" height="10" fill="#ffffff" />
              <line x1="70" y1="140" x2="70" y2="150" stroke="#000" strokeWidth="2" />
              <line x1="90" y1="140" x2="90" y2="150" stroke="#000" strokeWidth="2" />
              <line x1="66" y1="110" x2="55" y2="100" stroke="#000" strokeWidth="2" />
              <line x1="94" y1="110" x2="105" y2="100" stroke="#000" strokeWidth="2" />
              {/* Dog */}
              <circle cx="220" cy="170" r="20" fill="#ffffff" stroke="#444" strokeWidth="2" />
              <circle cx="220" cy="195" r="15" fill="#ffffff" stroke="#444" strokeWidth="2" />
              <circle cx="215" cy="168" r="4" fill="#000" />
              <ellipse cx="225" cy="168" rx="2" ry="4" fill="#000" transform="rotate(20 225 168)" />
              <line x1="220" y1="185" x2="220" y2="205" stroke="#444" strokeWidth="2" />
              <line x1="230" y1="185" x2="230" y2="205" stroke="#444" strokeWidth="2" />
              <line x1="210" y1="200" x2="210" y2="215" stroke="#444" strokeWidth="2" />
              <line x1="220" y1="200" x2="220" y2="215" stroke="#444" strokeWidth="2" />
              {/* Cat */}
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
            <svg style={svgStyle} version="1.1" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
              {/* Background */}
              <rect width="400" height="300" fill="#f0e6f6" />
              {/* House */}
              <rect x="120" y="90" width="160" height="90" fill="#ffae42" stroke="#444" strokeWidth="2" />
              <polygon points="120,90 200,40 280,90" fill="#c76e3a" />
              {/* Vet */}
              <circle cx="70" cy="70" r="20" fill="#f3d9c2" />
              <rect x="60" y="90" width="20" height="40" fill="#ffffff" />
              <rect x="56" y="90" width="28" height="10" fill="#ffffff" />
              <line x1="60" y1="130" x2="60" y2="140" stroke="#000" strokeWidth="2" />
              <line x1="80" y1="130" x2="80" y2="140" stroke="#000" strokeWidth="2" />
              <line x1="56" y1="100" x2="45" y2="110" stroke="#000" strokeWidth="2" />
              <line x1="84" y1="100" x2="95" y2="90" stroke="#000" strokeWidth="2" />
              {/* Dog */}
              <circle cx="230" cy="180" r="20" fill="#ffc" stroke="#444" strokeWidth="2" />
              <circle cx="230" cy="205" r="15" fill="#ffc" stroke="#444" strokeWidth="2" />
              <circle cx="225" cy="178" r="4" fill="#000" />
              <ellipse cx="235" cy="178" rx="2" ry="4" fill="#000" transform="rotate(20 235 178)" />
              <line x1="230" y1="195" x2="230" y2="215" stroke="#444" strokeWidth="2" />
              <line x1="240" y1="195" x2="240" y2="215" stroke="#444" strokeWidth="2" />
              <line x1="220" y1="210" x2="220" y2="225" stroke="#444" strokeWidth="2" />
              <line x1="230" y1="210" x2="230" y2="225" stroke="#444" strokeWidth="2" />
              {/* Cat */}
              <circle cx="280" cy="180" r="15" fill="#333" stroke="#444" strokeWidth="2" />
              <polygon points="275,167 270,160 280,165" fill="#444" />
              <polygon points="285,167 290,160 280,165" fill="#444" />
              <circle cx="280" cy="200" r="12" fill="#333" stroke="#444" strokeWidth="2" />
              <line x1="280" y1="188" x2="280" y2="195" stroke="#000" strokeWidth="2" />
              <line x1="275" y1="190" x2="285" y2="190" stroke="#000" strokeWidth="2" />
              <line x1="275" y1="205" x2="275" y2="215" stroke="#444" strokeWidth="2" />
              <line x1="285" y1="205" x2="285" y2="215" stroke="#444" strokeWidth="2" />
              <line x1="292" y1="200" x2="300" y2="195" stroke="#444" strokeWidth="2" />
            </svg>

            {/* Иллюстрация 3 */}
            <svg style={svgStyle} version="1.1" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
              {/* Background */}
              <rect width="400" height="300" fill="#e6f7d4" />
              {/* House */}
              <rect x="130" y="110" width="140" height="70" fill="#ffe680" stroke="#444" strokeWidth="2" />
              <polygon points="130,110 200,70 270,110" fill="#9e6b3a" />
              {/* Vet */}
              <circle cx="90" cy="90" r="20" fill="#f3d9c2" />
              <rect x="80" y="110" width="20" height="40" fill="#ffffff" />
              <rect x="76" y="110" width="28" height="10" fill="#ffffff" />
              <line x1="80" y1="150" x2="80" y2="160" stroke="#000" strokeWidth="2" />
              <line x1="100" y1="150" x2="100" y2="160" stroke="#000" strokeWidth="2" />
              <line x1="76" y1="120" x2="65" y2="115" stroke="#000" strokeWidth="2" />
              <line x1="104" y1="120" x2="115" y2="125" stroke="#000" strokeWidth="2" />
              {/* Dog */}
              <circle cx="210" cy="170" r="20" fill="#d2a679" stroke="#444" strokeWidth="2" />
              
