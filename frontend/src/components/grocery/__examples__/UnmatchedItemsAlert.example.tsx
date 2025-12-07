/**
 * Example usage of UnmatchedItemsAlert component
 *
 * This file demonstrates different scenarios for the component.
 * Can be used with Storybook or as a reference for implementation.
 */

import React from 'react'
import { UnmatchedItemsAlert } from '../UnmatchedItemsAlert'

export function UnmatchedItemsAlertExamples() {
  return (
    <div className="space-y-8 p-8 bg-gray-100">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        UnmatchedItemsAlert Component Examples
      </h1>

      {/* Example 1: Multiple Items */}
      <section>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Example 1: Multiple Unmatched Items
        </h2>
        <UnmatchedItemsAlert
          items={[
            'Saffron threads (premium quality)',
            'Kaffir lime leaves',
            'Black garlic paste',
            'Sumac powder',
            'Miso paste (white)'
          ]}
          cartId={1}
        />
      </section>

      {/* Example 2: Single Item */}
      <section>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Example 2: Single Unmatched Item
        </h2>
        <UnmatchedItemsAlert
          items={['Truffle oil (extra virgin)']}
          cartId={2}
        />
      </section>

      {/* Example 3: Common Items */}
      <section>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Example 3: Common But Unavailable Items
        </h2>
        <UnmatchedItemsAlert
          items={[
            'Fresh basil',
            'Organic eggs',
            'Greek yogurt'
          ]}
          cartId={3}
        />
      </section>

      {/* Example 4: Long Item Names */}
      <section>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Example 4: Items with Long Names
        </h2>
        <UnmatchedItemsAlert
          items={[
            'Extra virgin cold-pressed organic olive oil from Greece (500ml glass bottle)',
            'Gluten-free certified ancient grain pasta made with quinoa and amaranth'
          ]}
          cartId={4}
        />
      </section>

      {/* Example 5: Many Items */}
      <section>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Example 5: Many Unmatched Items (8 items)
        </h2>
        <UnmatchedItemsAlert
          items={[
            'Saffron threads',
            'Kaffir lime leaves',
            'Black garlic',
            'Sumac powder',
            'Miso paste',
            'Gochugaru (Korean chili flakes)',
            'Galangal root',
            'Fresh curry leaves'
          ]}
          cartId={5}
        />
      </section>

      {/* Example 6: With Custom Class */}
      <section>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Example 6: With Custom Styling
        </h2>
        <UnmatchedItemsAlert
          items={['Exotic spice blend', 'Specialty cheese']}
          cartId={6}
          className="shadow-xl"
        />
      </section>

      {/* Usage Instructions */}
      <section className="bg-white rounded-lg p-6 border border-gray-200">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          Usage Instructions
        </h2>
        <div className="prose prose-sm max-w-none">
          <h3>Basic Usage</h3>
          <pre className="bg-gray-100 p-4 rounded overflow-x-auto">
{`import { UnmatchedItemsAlert } from '@/components/grocery/UnmatchedItemsAlert'

function GroceryCartPage() {
  const cart = useGroceryCart(cartId)

  return (
    <div>
      {/* Other content */}

      {cart.unmatched_items?.length > 0 && (
        <UnmatchedItemsAlert
          items={cart.unmatched_items}
          cartId={cart.id}
        />
      )}

      {/* Rest of cart */}
    </div>
  )
}`}
          </pre>

          <h3>Props</h3>
          <ul>
            <li><strong>items</strong> (required): Array of unmatched item names</li>
            <li><strong>cartId</strong> (required): Unique cart identifier for localStorage</li>
            <li><strong>className</strong> (optional): Additional CSS classes</li>
          </ul>

          <h3>Features</h3>
          <ul>
            <li>Collapsible/expandable item list</li>
            <li>Individual item dismissal with persistence</li>
            <li>Full alert dismissal</li>
            <li>Direct search links to Knuspr</li>
            <li>Responsive design (mobile and desktop)</li>
            <li>Full accessibility support (ARIA, keyboard navigation)</li>
            <li>localStorage persistence across sessions</li>
          </ul>

          <h3>User Interactions</h3>
          <ul>
            <li><strong>Expand/Collapse:</strong> Click &quot;Show Items&quot; or &quot;Hide Items&quot; button</li>
            <li><strong>Search Item:</strong> Click &quot;Search&quot; button next to item</li>
            <li><strong>Dismiss Item:</strong> Click X button next to item</li>
            <li><strong>Dismiss Alert:</strong> Click X button in top-right corner</li>
            <li><strong>Browse Knuspr:</strong> Click &quot;Browse Knuspr&quot; link in footer</li>
          </ul>

          <h3>localStorage Keys</h3>
          <ul>
            <li><code>unmatched-items-dismissed-{'{cartId}'}</code>: Array of dismissed item names</li>
            <li><code>unmatched-alert-dismissed-{'{cartId}'}</code>: Boolean for alert dismissal</li>
          </ul>
        </div>
      </section>
    </div>
  )
}

export default UnmatchedItemsAlertExamples
