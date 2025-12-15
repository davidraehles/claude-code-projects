import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";
import { forwardRef, ButtonHTMLAttributes } from "react";
import { Slot } from "@radix-ui/react-slot";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md3-xl text-sm font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-38 active:scale-95",
  {
    variants: {
      variant: {
        primary: "bg-primary text-white shadow-md3-2 hover:shadow-md3-3 hover:bg-primary-700 active:bg-primary-800",
        secondary: "bg-secondary-100 text-secondary-900 border-2 border-secondary-300 hover:bg-secondary-200 hover:border-primary active:bg-secondary-300",
        outlined: "bg-transparent text-primary border-2 border-primary hover:bg-primary-50 active:bg-primary-100",
        ghost: "bg-transparent text-secondary-900 hover:bg-secondary-100 active:bg-secondary-200",
        elevated: "bg-white text-primary shadow-md3-2 hover:shadow-md3-4 hover:bg-primary-50",
        tonal: "bg-primary-100 text-primary-700 hover:bg-primary-200 hover:shadow-md3-1 active:bg-primary-300",
      },
      size: {
        sm: "h-10 px-4 py-2 text-xs",
        default: "h-12 px-6 py-3 text-sm",
        lg: "h-14 px-8 py-3.5 text-base",
        icon: "h-12 w-12 p-0",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
