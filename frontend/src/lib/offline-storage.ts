/**
 * IndexedDB wrapper for offline storage of waitlist entries.
 * Provides queue management for offline-first waitlist functionality.
 */

import type { WaitlistQueuedEntry } from "./types"

const DB_NAME = "GoCartOfflineDB"
const DB_VERSION = 1
const STORE_NAME = "waitlistQueue"

interface QueuedEntryWithId extends WaitlistQueuedEntry {
  id?: IDBValidKey
}

/**
 * Initialize IndexedDB database
 */
function openDatabase(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    if (typeof window === "undefined" || !("indexedDB" in window)) {
      reject(new Error("IndexedDB not supported"))
      return
    }

    const request = indexedDB.open(DB_NAME, DB_VERSION)

    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)

    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result

      // Create object store if it doesn't exist
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        const objectStore = db.createObjectStore(STORE_NAME, {
          keyPath: "id",
          autoIncrement: true,
        })

        // Create indexes for querying
        objectStore.createIndex("timestamp", "timestamp", { unique: false })
        objectStore.createIndex("email", "email", { unique: false })
      }
    }
  })
}

/**
 * Add a waitlist entry to the offline queue
 */
export async function addToQueue(
  email: string,
  metadata?: Record<string, unknown>
): Promise<void> {
  const db = await openDatabase()

  const entry: WaitlistQueuedEntry = {
    email,
    metadata,
    timestamp: Date.now(),
    retryCount: 0,
  }

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], "readwrite")
    const objectStore = transaction.objectStore(STORE_NAME)
    const request = objectStore.add(entry)

    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)

    transaction.oncomplete = () => db.close()
  })
}

/**
 * Get all entries in the queue
 */
export async function getQueue(): Promise<QueuedEntryWithId[]> {
  const db = await openDatabase()

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], "readonly")
    const objectStore = transaction.objectStore(STORE_NAME)
    const request = objectStore.getAll()

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)

    transaction.oncomplete = () => db.close()
  })
}

/**
 * Remove an entry from the queue by ID
 */
export async function removeFromQueue(id: IDBValidKey): Promise<void> {
  const db = await openDatabase()

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], "readwrite")
    const objectStore = transaction.objectStore(STORE_NAME)
    const request = objectStore.delete(id)

    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)

    transaction.oncomplete = () => db.close()
  })
}

/**
 * Update retry count for a queued entry
 */
export async function incrementRetryCount(id: IDBValidKey): Promise<void> {
  const db = await openDatabase()

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], "readwrite")
    const objectStore = transaction.objectStore(STORE_NAME)
    const getRequest = objectStore.get(id)

    getRequest.onsuccess = () => {
      const entry = getRequest.result as QueuedEntryWithId
      if (entry) {
        entry.retryCount = (entry.retryCount || 0) + 1
        const updateRequest = objectStore.put(entry)

        updateRequest.onsuccess = () => resolve()
        updateRequest.onerror = () => reject(updateRequest.error)
      } else {
        reject(new Error("Entry not found"))
      }
    }

    getRequest.onerror = () => reject(getRequest.error)

    transaction.oncomplete = () => db.close()
  })
}

/**
 * Clear all entries from the queue
 */
export async function clearQueue(): Promise<void> {
  const db = await openDatabase()

  return new Promise((resolve, reject) => {
    const transaction = db.transaction([STORE_NAME], "readwrite")
    const objectStore = transaction.objectStore(STORE_NAME)
    const request = objectStore.clear()

    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)

    transaction.oncomplete = () => db.close()
  })
}

/**
 * Check if there are any pending entries in the queue
 */
export async function hasQueuedEntries(): Promise<boolean> {
  const queue = await getQueue()
  return queue.length > 0
}

/**
 * Get count of queued entries
 */
export async function getQueueCount(): Promise<number> {
  const queue = await getQueue()
  return queue.length
}
