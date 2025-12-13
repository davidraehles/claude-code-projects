/**
 * Service Worker for Go, Cart! Waitlist
 * Provides background sync functionality for offline waitlist submissions
 */

const CACHE_NAME = 'go-cart-v1'
const API_URL = self.location.origin.includes('localhost')
  ? 'http://localhost:8000'
  : 'https://api.gocart.app' // Update with your production API URL

// Install event - cache essential assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...')

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Service Worker] Caching app shell')
      return cache.addAll([
        '/',
        '/offline.html', // Create this page for offline fallback
      ]).catch((error) => {
        console.error('[Service Worker] Cache failed:', error)
      })
    })
  )

  // Force the waiting service worker to become the active service worker
  self.skipWaiting()
})

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...')

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    }).then(() => {
      console.log('[Service Worker] Activated')
      return self.clients.claim()
    })
  )
})

// Background Sync event - process queued waitlist entries
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Sync event:', event.tag)

  if (event.tag === 'sync-waitlist') {
    event.waitUntil(syncWaitlistQueue())
  }
})

/**
 * Sync queued waitlist entries with the server
 */
async function syncWaitlistQueue() {
  console.log('[Service Worker] Syncing waitlist queue...')

  try {
    // Open IndexedDB
    const db = await openDatabase()
    const entries = await getAllQueuedEntries(db)

    console.log(`[Service Worker] Found ${entries.length} queued entries`)

    // Process each entry
    const results = await Promise.allSettled(
      entries.map((entry) => processQueuedEntry(entry, db))
    )

    const successful = results.filter((r) => r.status === 'fulfilled').length
    const failed = results.filter((r) => r.status === 'rejected').length

    console.log(`[Service Worker] Sync complete: ${successful} successful, ${failed} failed`)

    // Notify clients about sync completion
    await notifyClients({
      type: 'WAITLIST_SYNC_COMPLETE',
      successful,
      failed,
    })

    return results
  } catch (error) {
    console.error('[Service Worker] Sync failed:', error)
    throw error
  }
}

/**
 * Process a single queued entry
 */
async function processQueuedEntry(entry, db) {
  const MAX_RETRIES = 3

  try {
    // Attempt to submit to API
    const response = await fetch(`${API_URL}/api/v1/waitlist`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: entry.email,
        metadata: entry.metadata,
      }),
    })

    if (response.ok) {
      // Success - remove from queue
      console.log(`[Service Worker] Successfully synced: ${entry.email}`)
      await removeQueuedEntry(db, entry.id)
      return { success: true, email: entry.email }
    } else if (response.status === 400) {
      // Client error (e.g., already registered) - remove from queue
      console.warn(`[Service Worker] Client error for ${entry.email}, removing from queue`)
      await removeQueuedEntry(db, entry.id)
      return { success: false, email: entry.email, reason: 'client_error' }
    } else {
      // Server error - retry
      throw new Error(`Server error: ${response.status}`)
    }
  } catch (error) {
    console.error(`[Service Worker] Failed to sync ${entry.email}:`, error)

    // Increment retry count
    const newRetryCount = (entry.retryCount || 0) + 1

    if (newRetryCount >= MAX_RETRIES) {
      // Max retries reached - remove from queue
      console.warn(`[Service Worker] Max retries reached for ${entry.email}, removing from queue`)
      await removeQueuedEntry(db, entry.id)
    } else {
      // Update retry count
      await updateRetryCount(db, entry.id, newRetryCount)
    }

    throw error
  }
}

/**
 * IndexedDB helper functions
 */

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('GoCartOfflineDB', 1)

    request.onerror = () => reject(request.error)
    request.onsuccess = () => resolve(request.result)

    request.onupgradeneeded = (event) => {
      const db = event.target.result

      if (!db.objectStoreNames.contains('waitlistQueue')) {
        const objectStore = db.createObjectStore('waitlistQueue', {
          keyPath: 'id',
          autoIncrement: true,
        })

        objectStore.createIndex('timestamp', 'timestamp', { unique: false })
        objectStore.createIndex('email', 'email', { unique: false })
      }
    }
  })
}

function getAllQueuedEntries(db) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['waitlistQueue'], 'readonly')
    const objectStore = transaction.objectStore('waitlistQueue')
    const request = objectStore.getAll()

    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

function removeQueuedEntry(db, id) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['waitlistQueue'], 'readwrite')
    const objectStore = transaction.objectStore('waitlistQueue')
    const request = objectStore.delete(id)

    request.onsuccess = () => resolve()
    request.onerror = () => reject(request.error)
  })
}

function updateRetryCount(db, id, retryCount) {
  return new Promise((resolve, reject) => {
    const transaction = db.transaction(['waitlistQueue'], 'readwrite')
    const objectStore = transaction.objectStore('waitlistQueue')
    const getRequest = objectStore.get(id)

    getRequest.onsuccess = () => {
      const entry = getRequest.result
      if (entry) {
        entry.retryCount = retryCount
        const updateRequest = objectStore.put(entry)

        updateRequest.onsuccess = () => resolve()
        updateRequest.onerror = () => reject(updateRequest.error)
      } else {
        reject(new Error('Entry not found'))
      }
    }

    getRequest.onerror = () => reject(getRequest.error)
  })
}

/**
 * Notify all clients about events
 */
async function notifyClients(message) {
  const clients = await self.clients.matchAll({ includeUncontrolled: true })

  clients.forEach((client) => {
    client.postMessage(message)
  })
}

// Fetch event - network-first strategy for API calls, cache-first for assets
self.addEventListener('fetch', (event) => {
  const { request } = event

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return
  }

  // API requests - network first
  if (request.url.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .catch(() => {
          // Return a custom offline response for API requests
          return new Response(
            JSON.stringify({ error: 'You are offline' }),
            {
              status: 503,
              headers: { 'Content-Type': 'application/json' }
            }
          )
        })
    )
    return
  }

  // Static assets - cache first
  event.respondWith(
    caches.match(request).then((response) => {
      return response || fetch(request).catch(() => {
        // Return offline page if available
        return caches.match('/offline.html')
      })
    })
  )
})

// Message event - handle messages from clients
self.addEventListener('message', (event) => {
  console.log('[Service Worker] Message received:', event.data)

  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }

  if (event.data.type === 'SYNC_NOW') {
    // Trigger sync immediately
    syncWaitlistQueue().catch((error) => {
      console.error('[Service Worker] Manual sync failed:', error)
    })
  }
})
