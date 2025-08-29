import React from "react";

export const Navbar = () => {
  return (
    <div className="">
      <div className="navbar text-black flex py-4 px-10 bg-[#04b304] justify-between items-center mx-auto">
        {/* Left: Logo / Brand */}

        <div className="max-w-5xl">
          <h1 className="text-xl font-semibold">EcoBasket</h1>
        </div>

        {/* Right: Navigation Links */}
        <div className="flex space-x-6 text-sm font-medium">
          <a
            href="/"
            className="hover:text-white transition-colors duration-200"
          >
            Home
          </a>
          <a
            href="/about"
            className="hover:text-white transition-colors duration-200"
          >
            About
          </a>
        </div>
      </div>

      <div className="py-10 md:px-0 px-10 flex flex-col md:flex-row gap-8 items-center mx-auto max-w-6xl justify-center">
        {/* Left: Text Section */}
        <div>
          <p className="text-3xl font-semibold mb-4">
            Upload receipt → Get carbon footprint
          </p>
          <p className="text-base opacity-90 max-w-2xl">
            CarbonDrop scans your purchase receipt using OCR, matches each item
            with a greenhouse gas emissions dataset, and calculates the total
            carbon footprint of your shopping. The results are then visualized
            in an interactive dashboard to help you understand and reduce your
            environmental impact.
          </p>
        </div>

        {/* Right: Image/Preview Section */}
        <div className="flex justify-center">
          <img
            src="https://media.istockphoto.com/id/1614043557/photo/net-zero-concept-and-carbon-neutral-natural-environment-climate-neutral-long-term-emissions.webp?a=1&b=1&s=612x612&w=0&k=20&c=z_YRKV87jSA669-i4Xa6cPu1p-i3lbGdX2RmitHVP84="
            alt="Receipt preview"
            className="rounded w-100 h-auto object-contain p-10"
          />
        </div>
      </div>
    </div>
  );
};
