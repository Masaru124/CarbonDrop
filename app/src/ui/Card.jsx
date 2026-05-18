import { cn } from "../lib/cn";

export default function Card({ children, className, ...props }) {
  return (
    <div
      className={cn(
        "bg-gray-900 border border-gray-800 rounded-xl p-6 shadow-sm",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}
