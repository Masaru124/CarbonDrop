import WhatIfSimulator from "./WhatIfSimulator";

export default function Simulator() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">What-if Simulator</h1>
      <p className="text-gray-600 mb-6">
        Explore different scenarios to see how small changes in your lifestyle can impact your carbon footprint.
      </p>
      <WhatIfSimulator />
    </div>
  );
}
