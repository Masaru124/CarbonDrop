import React, { useState, useEffect } from "react";
// import Upload from "./components/Upload";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import History from "./components/History";

export default function App() {
  return (
    <>
      <Navbar />
      {/* <Upload /> */}
      <History />
      <Footer />
    </>
  );
}
