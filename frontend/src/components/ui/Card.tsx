import { HTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hover?: boolean;
  padding?: "none" | "sm" | "md" | "lg";
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ className, hover = false, padding = "md", children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={clsx(
          "bg-white rounded-xl border border-gray-200 shadow-sm",
          {
            "hover:shadow-md hover:border-gray-300 transition-shadow": hover,
            "": padding === "none",
            "p-3 sm:p-4": padding === "sm",
            "p-4 sm:p-6": padding === "md",
            "p-6 sm:p-8": padding === "lg",
          },
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);

Card.displayName = "Card";

export default Card;
