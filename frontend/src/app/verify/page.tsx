"use client"

/**
 * Email Verification Page
 * Handles waitlist email verification via token
 */

import { useEffect, useState, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { api } from "@/lib/api"
import type { WaitlistEntry } from "@/lib/types"

type VerificationState = "verifying" | "success" | "error" | "invalid"

function VerifyContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [state, setState] = useState<VerificationState>("verifying")
  const [entry, setEntry] = useState<WaitlistEntry | null>(null)
  const [errorMessage, setErrorMessage] = useState("")

  useEffect(() => {
    const verifyToken = async () => {
      const token = searchParams.get("token")

      if (!token) {
        setState("invalid")
        setErrorMessage("No verification token provided")
        return
      }

      try {
        const result = await api.verifyWaitlistEmail({ token })
        setEntry(result)
        setState("success")
      } catch (error) {
        console.error("Verification failed:", error)
        setState("error")

        if (error instanceof Error) {
          if (error.message.includes("404") || error.message.includes("not found")) {
            setErrorMessage("This verification link is invalid or has expired.")
          } else if (error.message.includes("400") || error.message.includes("already verified")) {
            setErrorMessage("This email has already been verified.")
          } else {
            setErrorMessage(error.message || "Verification failed. Please try again.")
          }
        } else {
          setErrorMessage("Verification failed. Please try again.")
        }
      }
    }

    verifyToken()
  }, [searchParams])

  const handleGoHome = () => {
    router.push("/")
  }

  if (state === "verifying") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-100 p-4">
        <div className="max-w-md w-full bg-neutral-0 rounded-2xl shadow-lg p-8 text-center">
          <div className="mb-6">
            <div className="w-16 h-16 mx-auto border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
          </div>
          <h1 className="text-2xl font-display font-bold text-secondary-800 mb-2">
            Verifying your email...
          </h1>
          <p className="text-neutral-600">
            Please wait while we confirm your email address.
          </p>
        </div>
      </div>
    )
  }

  if (state === "invalid") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-100 p-4">
        <div className="max-w-md w-full bg-neutral-0 rounded-2xl shadow-lg p-8 text-center">
          <div className="mb-6">
            <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
              <svg
                className="w-8 h-8 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </div>
          </div>
          <h1 className="text-2xl font-display font-bold text-secondary-800 mb-2">
            Invalid Link
          </h1>
          <p className="text-neutral-600 mb-6">
            {errorMessage}
          </p>
          <Button
            variant="primary"
            size="lg"
            onClick={handleGoHome}
            className="w-full"
          >
            Go to Homepage
          </Button>
        </div>
      </div>
    )
  }

  if (state === "error") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-100 p-4">
        <div className="max-w-md w-full bg-neutral-0 rounded-2xl shadow-lg p-8 text-center">
          <div className="mb-6">
            <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
              <svg
                className="w-8 h-8 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
          </div>
          <h1 className="text-2xl font-display font-bold text-secondary-800 mb-2">
            Verification Failed
          </h1>
          <p className="text-neutral-600 mb-6">
            {errorMessage}
          </p>
          <Button
            variant="primary"
            size="lg"
            onClick={handleGoHome}
            className="w-full"
          >
            Go to Homepage
          </Button>
        </div>
      </div>
    )
  }

  // Success state
  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-100 p-4">
      <div className="max-w-md w-full bg-neutral-0 rounded-2xl shadow-lg p-8 text-center">
        <div className="mb-6">
          <div className="w-16 h-16 mx-auto bg-accent-100 rounded-full flex items-center justify-center">
            <svg
              className="w-8 h-8 text-accent-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
        </div>
        <h1 className="text-2xl font-display font-bold text-secondary-800 mb-2">
          Email Verified!
        </h1>
        <p className="text-neutral-600 mb-6">
          Thanks for confirming your email address. You&#39;re all set on the waitlist!
        </p>

        {entry && entry.position && (
          <div className="mb-6 p-4 bg-accent-50 rounded-lg border border-accent-200">
            <p className="text-sm text-neutral-600 mb-1">Your position</p>
            <p className="text-3xl font-display font-bold text-accent-600">
              #{entry.position}
            </p>
          </div>
        )}

        <div className="space-y-3">
          <p className="text-sm text-neutral-600">
            We&#39;ll notify you when it&#39;s your turn to join Go, Cart!
          </p>
          <Button
            variant="primary"
            size="lg"
            onClick={handleGoHome}
            className="w-full"
          >
            Go to Homepage
          </Button>
        </div>
      </div>
    </div>
  )
}

export default function VerifyPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-neutral-100 p-4">
          <div className="max-w-md w-full bg-neutral-0 rounded-2xl shadow-lg p-8 text-center">
            <div className="mb-6">
              <div className="w-16 h-16 mx-auto border-4 border-primary-500 border-t-transparent rounded-full animate-spin" />
            </div>
            <h1 className="text-2xl font-display font-bold text-secondary-800 mb-2">
              Loading...
            </h1>
          </div>
        </div>
      }
    >
      <VerifyContent />
    </Suspense>
  )
}
