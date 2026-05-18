import { cn } from "../lib/cn";

const variants = {
  success: "bg-green-900/50 text-green-400 border-green-700",
  error: "bg-red-900/50 text-red-400 border-red-700",
  neutral: "bg-gray-800 text-gray-400 border-gray-700",
};

export default function Badge({ children, variant = "neutral", className }) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border",
        variants[variant],
        className,
      )}
    >
      {children}
    </span>
  );
}
