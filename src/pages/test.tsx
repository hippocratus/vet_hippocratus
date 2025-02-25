import React, { Fragment } from "react";
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
    <Fragment>
      <Head>
        <title>Online Veterinary Office</title>
        <meta charSet="utf
