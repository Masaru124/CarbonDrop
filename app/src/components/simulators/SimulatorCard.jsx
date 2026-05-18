export default function SimulatorCard({ title, icon, children }) {
  return (
    <div className="group bg-gray-900/60 backdrop-blur-sm border border-gray-800 rounded-xl p-5 hover:border-green-700/50 transition-all duration-300">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xl">{icon}</span>
        <h3 className="font-semibold text-green-400">{title}</h3>
      </div>
      <div className="space-y-3">{children}</div>
    </div>
  );
}

export function SimInput({ label, value, onChange, ...props }) {
  return (
    <div>
      <label className="block text-xs text-gray-400 mb-1.5 uppercase tracking-wider">{label}</label>
      <input
        value={value}
        onChange={onChange}
        className="w-full px-3 py-2 rounded-lg bg-gray-800/80 text-white border border-gray-700 focus:border-green-500 focus:outline-none focus:ring-1 focus:ring-green-500/50 transition text-sm"
        {...props}
      />
    </div>
  );
}

export function SimButton({ onClick, disabled, loading, children }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className="w-full mt-2 bg-green-600 hover:bg-green-500 text-white py-2.5 px-4 rounded-lg font-medium text-sm transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
    >
      {loading ? (
        <span className="flex items-center justify-center gap-2">
          <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Calculating...
        </span>
      ) : (
        children
      )}
    </button>
  );
}

export function SimResult({ children }) {
  return (
    <div className="mt-3 p-3.5 bg-green-950/60 border border-green-800 rounded-lg animate-fade-in">
      {children}
    </div>
  );
}
