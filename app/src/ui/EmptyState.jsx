import { cn } from "../lib/cn";

export default function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}) {
  return (
    <div className={cn("flex flex-col items-center justify-center py-16 text-center", className)}>
      {icon && <div className="text-4xl mb-4">{icon}</div>}
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      {description && (
        <p className="text-gray-400 max-w-md mb-6">{description}</p>
      )}
      {action}
    </div>
  );
}
