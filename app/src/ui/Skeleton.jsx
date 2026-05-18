import { cn } from "../lib/cn";

export default function Skeleton({ className, ...props }) {
  return (
    <div
      className={cn("animate-pulse bg-gray-800 rounded-lg", className)}
      {...props}
    />
  );
}
