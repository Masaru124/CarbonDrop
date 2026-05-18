import { cn } from "../lib/cn";

export default function Input({
  label,
  error,
  className,
  id,
  ...props
}) {
  return (
    <div className="space-y-1.5">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-300">
          {label}
        </label>
      )}
      <input
        id={id}
        className={cn(
          "w-full px-4 py-2.5 rounded-lg bg-gray-800 border text-white placeholder-gray-500 transition duration-200 focus:outline-none focus:ring-2 focus:ring-green-500/50",
          error ? "border-red-500 focus:ring-red-500/50" : "border-gray-700 focus:border-green-500",
          className,
        )}
        {...props}
      />
      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  );
}
