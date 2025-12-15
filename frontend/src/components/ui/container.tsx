"use client"

import { ReactNode } from "react"
import { cn } from "@/lib/utils" // Assume Phase 1 setup includes this, or replace with className template literals if not

interface ContainerProps {
  children: ReactNode
  className?: string
  as?: React.ElementType
}

const Container = ({ children, className, as = "div", ...props }: ContainerProps) => {
  const Comp = as
  return (
    <Comp className={cn("w-full max-w-7xl mx-auto px-6 sm:px-8 lg:px-12", className)} {...props}>
      {children}
    </Comp>
  )
}

export { Container }
