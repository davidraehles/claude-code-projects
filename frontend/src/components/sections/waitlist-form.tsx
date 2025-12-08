"use client"

/**
 * Waitlist Form Component
 * Offline-first waitlist signup with email validation and queue management
 */

import { useState, useEffect } from "react"
import { Input } from "@/components/ui/Input"
import { Button } from "@/components/ui/button"
import { api } from "@/lib/api"
import { addToQueue, getQueueCount } from "@/lib/offline-storage"

interface WaitlistFormProps {
  className?: string
  onSuccess?: () => void
}

type FormState = "idle" | "submitting" | "success" | "error" | "offline"

export function WaitlistForm({ className = "", onSuccess }: WaitlistFormProps) {
  const [email, setEmail] = useState("")
  const [state, setState] = useState<FormState>("idle")
  const [errorMessage, setErrorMessage] = useState("")
  const [queueCount, setQueueCount] = useState(0)
  const [isOnline, setIsOnline] = useState(() => navigator.onLine)

  // Check online status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      // Trigger background sync when coming back online
      if ("serviceWorker" in navigator) {
        navigator.serviceWorker.ready.then((registration) => {
          if ("sync" in registration) {
            return (registration as any).sync.register("sync-waitlist")
          }
        }).catch((error) => {
          console.error("Background sync registration failed:", error)
        })
      }
    }

    const handleOffline = () => {
      setIsOnline(false)
    }

    window.addEventListener("online", handleOnline)
    window.addEventListener("offline", handleOffline)

    return () => {
      window.removeEventListener("online", handleOnline)
      window.removeEventListener("offline", handleOffline)
    }
  }, [])

  // Update queue count
  useEffect(() => {
    const updateCount = async () => {
      try {
        const count = await getQueueCount()
        setQueueCount(count)
      } catch (error) {
        console.error("Failed to get queue count:", error)
      }
    }

    updateCount()

    // Listen for sync completion
    const handleMessage = (event: MessageEvent) => {
      if (event.data.type === "WAITLIST_SYNC_COMPLETE") {
        updateCount()
      }
    }

    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.addEventListener("message", handleMessage)
      return () => {
        navigator.serviceWorker.removeEventListener("message", handleMessage)
      }
    }
  }, [])

  // Email validation
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Reset error state
    setErrorMessage("")

    // Validate email
    if (!email) {
      setErrorMessage("Please enter your email address")
      setState("error")
      return
    }

    if (!validateEmail(email)) {
      setErrorMessage("Please enter a valid email address")
      setState("error")
      return
    }

    setState("submitting")

    try {
      if (!isOnline) {
        // Offline - add to queue
        await addToQueue(email, {
          source: "landing_page",
          timestamp: new Date().toISOString(),
        })

        setState("offline")
        setEmail("")

        // Register background sync
        if ("serviceWorker" in navigator) {
          const registration = await navigator.serviceWorker.ready
          if ("sync" in registration) {
            await (registration as any).sync.register("sync-waitlist")
          }
        }

        setTimeout(() => {
          setState("idle")
          onSuccess?.()
        }, 3000)
      } else {
        // Online - submit directly
        await api.joinWaitlist({
          email,
          metadata: {
            source: "landing_page",
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
          },
        })

        setState("success")
        setEmail("")

        setTimeout(() => {
          setState("idle")
          onSuccess?.()
        }, 3000)
      }
    } catch (error) {
      // If online request fails, try to queue it
      if (isOnline) {
        try {
          await addToQueue(email, {
            source: "landing_page",
            timestamp: new Date().toISOString(),
          })

          setState("offline")
          setEmail("")

          // Register background sync
          if ("serviceWorker" in navigator) {
            const registration = await navigator.serviceWorker.ready
            if ("sync" in registration) {
              await (registration as any).sync.register("sync-waitlist")
            }
          }

          setTimeout(() => {
            setState("idle")
          }, 3000)
        } catch (queueError) {
          console.error("Failed to queue entry:", queueError)
          setState("error")

          if (error instanceof Error) {
            if (error.message.includes("already registered") || error.message.includes("400")) {
              setErrorMessage("This email is already on the waitlist")
            } else {
              setErrorMessage(error.message || "Something went wrong. Please try again.")
            }
          } else {
            setErrorMessage("Something went wrong. Please try again.")
          }

          setTimeout(() => {
            setState("idle")
          }, 3000)
        }
      } else {
        console.error("Submit failed:", error)
        setState("error")
        setErrorMessage("Failed to save your request. Please try again.")

        setTimeout(() => {
          setState("idle")
        }, 3000)
      }
    }
  }

  // Get status message
  const getStatusMessage = (): string => {
    switch (state) {
      case "submitting":
        return "Joining waitlist..."
      case "success":
        return "Success! Check your email to verify."
      case "offline":
        return "Saved! We'll submit when you're back online."
      case "error":
        return errorMessage
      default:
        return ""
    }
  }

  // Get status class
  const getStatusClass = (): string => {
    switch (state) {
      case "success":
        return "text-accent-600 bg-accent-50 border-accent-200"
      case "offline":
        return "text-blue-600 bg-blue-50 border-blue-200"
      case "error":
        return "text-red-600 bg-red-50 border-red-200"
      default:
        return ""
    }
  }

  return (
    <div className={className}>
      <form onSubmit={handleSubmit} className="w-full max-w-md mx-auto">
        <div className="flex flex-col sm:flex-row gap-3">
          <Input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={state === "submitting"}
            className="flex-1"
            error={state === "error" ? errorMessage : undefined}
            aria-label="Email address"
            aria-required="true"
            aria-invalid={state === "error"}
          />
          <Button
            type="submit"
            variant="primary"
            size="lg"
            disabled={state === "submitting"}
            className="sm:w-auto w-full"
          >
            {state === "submitting" ? "Joining..." : "Join Waitlist"}
          </Button>
        </div>

        {/* Status message */}
        {state !== "idle" && getStatusMessage() && (
          <div
            className={`mt-4 p-4 rounded-lg border ${getStatusClass()} text-sm font-medium transition-all`}
            role="status"
            aria-live="polite"
          >
            {getStatusMessage()}
          </div>
        )}

        {/* Queue indicator */}
        {queueCount > 0 && (
          <div className="mt-4 p-3 rounded-lg bg-blue-50 border border-blue-200 text-blue-700 text-sm">
            <p>
              {queueCount} {queueCount === 1 ? "entry" : "entries"} waiting to sync
              {!isOnline && " (you're offline)"}
            </p>
          </div>
        )}

        {/* Offline indicator */}
        {!isOnline && queueCount === 0 && (
          <div className="mt-4 p-3 rounded-lg bg-yellow-50 border border-yellow-200 text-yellow-700 text-sm">
            <p>You&#39;re currently offline. Your submission will be saved and sent when you reconnect.</p>
          </div>
        )}
      </form>

      {/* Privacy notice */}
      <p className="text-xs text-neutral-600 text-center mt-4 max-w-md mx-auto">
        We&#39;ll send you a verification email. No spam, ever. You can unsubscribe at any time.
      </p>
    </div>
  )
}
