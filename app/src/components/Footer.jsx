import React from "react";

const Footer = () => {
  return (
    <footer className="bg-black text-white py-10 w-full">
      <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Brand / Description */}
        <div>
          <h1 className="text-2xl font-semibold mb-3">EcoBasket</h1>
          <p className="text-sm opacity-80">
            Track and understand the carbon footprint of your purchases.
            Empowering sustainable choices with technology.
          </p>
        </div>

        {/* Navigation Links */}
        <div className="flex flex-col space-y-2">
          <h2 className="text-lg font-semibold mb-2">Quick Links</h2>
          <a href="/" className="hover:text-green-400">
            Home
          </a>
          <a href="/about" className="hover:text-green-400">
            About
          </a>
          <a href="/contact" className="hover:text-green-400">
            Contact
          </a>
        </div>

        {/* Socials */}
        <div>
          <h2 className="text-lg font-semibold mb-2">Connect</h2>
        </div>
      </div>

      {/* Bottom note */}
      <div className="mt-10 text-center text-sm opacity-70">
        © {new Date().getFullYear()} EcoBasket · Built with free tools ·
        Tesseract OCR required for backend.
      </div>
    </footer>
  );
};

export default Footer;
