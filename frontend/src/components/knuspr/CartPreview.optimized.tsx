import React from 'react';
import { ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';

// Re-export types from original
export interface CartItem {
  name: string;
  quantity: number;
  unit: string;
  price: number;
  available: boolean;
  category: string;
}

export interface CartItemsBySection {
  [section: string]: CartItem[];
}

export interface DeliverySlot {
  slot_id: string;
  date: string;
  time_window: string;
  price: number;
  available?: boolean;
}

export interface CartPreviewData {
  cart_id: string;
  knuspr_url: string;
  total_price: number;
  item_count: number;
  delivery_slot?: DeliverySlot | null;
  items_by_section: CartItemsBySection;
  unavailable_items: string[];
  created_at: string;
}

interface CartPreviewProps {
  data: CartPreviewData;
  onCheckout?: () => void;
  isLoading?: boolean;
  error?: string | null;
}

interface SectionExpandedState {
  [section: string]: boolean;
}

// Memoized component to prevent unnecessary re-renders
const CartPreviewComponent: React.FC<CartPreviewProps> = ({
  data,
  onCheckout,
  isLoading = false,
  error = null,
}) => {
  const [expandedSections, setExpandedSections] = React.useState<SectionExpandedState>(
    Object.keys(data.items_by_section).reduce((acc, section) => ({ ...acc, [section]: true }), {})
  );

  const toggleSection = React.useCallback((section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">Generating your shopping cart</h2>
        </div>
        <div className="animate-pulse space-y-3">
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border-2 border-red-200 bg-red-50 p-6 space-y-2">
        <h3 className="font-bold text-red-900">Cart Generation Failed</h3>
        <p className="text-red-800 text-sm">{error}</p>
        <button className="inline-flex items-center gap-2 rounded-lg bg-red-600 hover:bg-red-700 text-white px-4 py-2 font-semibold transition-colors">
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-gray-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Your Shopping Cart</h2>
          <p className="text-sm text-gray-600 mt-1">
            {data.item_count} items • Ready for checkout
          </p>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-blue-600">€{data.total_price.toFixed(2)}</p>
          <p className="text-xs text-gray-500 mt-1">Cart ID: {data.cart_id}</p>
        </div>
      </div>

      {/* Delivery Slot Info */}
      {data.delivery_slot && (
        <div className="rounded-lg bg-blue-50 border border-blue-200 p-4 space-y-2">
          <h3 className="font-semibold text-blue-900">Delivery Scheduled</h3>
          <div className="flex items-center justify-between text-sm">
            <div>
              <p className="text-blue-800">
                📅 {new Date(data.delivery_slot.date).toLocaleDateString()}
              </p>
              <p className="text-blue-700">⏰ {data.delivery_slot.time_window}</p>
            </div>
            <p className="font-semibold text-blue-900">€{data.delivery_slot.price.toFixed(2)}</p>
          </div>
        </div>
      )}

      {/* Cart Items by Section */}
      <div className="space-y-3">
        {Object.entries(data.items_by_section).map(([section, items]) => (
          <div
            key={section}
            className="rounded-lg border border-gray-200 overflow-hidden"
          >
            <button
              onClick={() => toggleSection(section)}
              className="w-full flex items-center justify-between bg-gray-50 hover:bg-gray-100 p-4 transition-colors"
            >
              <div className="flex items-center gap-3 flex-1 text-left">
                <h3 className="font-semibold text-gray-900 capitalize">{section}</h3>
                <span className="text-xs bg-blue-100 text-blue-700 rounded-full px-2 py-1">
                  {items.length} items
                </span>
              </div>
              {expandedSections[section] ? (
                <ChevronUp className="h-5 w-5 text-gray-600" />
              ) : (
                <ChevronDown className="h-5 w-5 text-gray-600" />
              )}
            </button>

            {expandedSections[section] && (
              <div className="space-y-2 p-4 bg-white">
                {items.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{item.name}</p>
                      <p className="text-xs text-gray-500">
                        {item.quantity} {item.unit}
                      </p>
                    </div>
                    <p className="font-semibold text-gray-900">€{item.price.toFixed(2)}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Unavailable Items */}
      {data.unavailable_items.length > 0 && (
        <div className="rounded-lg bg-amber-50 border border-amber-200 p-4 space-y-3">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="font-semibold text-amber-900">
                {data.unavailable_items.length} Item(s) Not Available
              </h3>
              <p className="text-sm text-amber-800 mt-1">
                These items aren't currently available at Knuspr:
              </p>
              <ul className="mt-2 space-y-1">
                {data.unavailable_items.map((item, idx) => (
                  <li key={idx} className="text-sm text-amber-900">
                    • {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Price Breakdown */}
      <div className="rounded-lg bg-gray-50 p-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Subtotal ({data.item_count} items)</span>
          <span className="font-medium text-gray-900">
            €{(data.total_price - (data.delivery_slot?.price || 0)).toFixed(2)}
          </span>
        </div>
        {data.delivery_slot && (
          <div className="flex justify-between text-sm">
            <span className="text-gray-600">Delivery Fee</span>
            <span className="font-medium text-gray-900">€{data.delivery_slot.price.toFixed(2)}</span>
          </div>
        )}
        <div className="border-t border-gray-200 pt-2 flex justify-between">
          <span className="font-semibold text-gray-900">Total</span>
          <span className="font-bold text-lg text-blue-600">€{data.total_price.toFixed(2)}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={onCheckout}
          className="flex-1 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 transition-colors"
        >
          Continue to Checkout
        </button>
        <a
          href={data.knuspr_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 rounded-lg border-2 border-blue-600 hover:bg-blue-50 text-blue-600 font-bold py-3 px-4 transition-colors text-center"
        >
          View on Knuspr
        </a>
      </div>
    </div>
  );
};

export const CartPreviewOptimized = React.memo(
  CartPreviewComponent,
  (prevProps, nextProps) => {
    // Custom comparison for memo to prevent re-renders unless data actually changes
    return (
      prevProps.data === nextProps.data &&
      prevProps.onCheckout === nextProps.onCheckout &&
      prevProps.isLoading === nextProps.isLoading &&
      prevProps.error === nextProps.error
    );
  }
);

CartPreviewOptimized.displayName = 'CartPreview';

export default CartPreviewOptimized;
