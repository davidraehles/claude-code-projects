'use client';

import React, { useMemo } from 'react';
import {
  ShoppingCart,
  Package,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Truck,
  CheckCircle,
} from 'lucide-react';
import { formatEUR } from '@/lib/formatCurrency';

export interface CartItem {
  name: string;
  quantity: number;
  unit: string;
  price: number;
  category?: string;
  product_id?: string;
  available?: boolean;
}

export interface CartItemsBySection {
  [section: string]: CartItem[];
}

export interface DeliverySlot {
  slot_id: string;
  date: string;
  time_window: string;
  price: number;
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

const sectionIcons: Record<string, React.ReactNode> = {
  dairy: '🥛',
  produce: '🥕',
  meat: '🍗',
  fish: '🐟',
  grains: '🌾',
  frozen: '❄️',
  oils_vinegar: '🫒',
  canned_goods: '🥫',
  other: '📦',
};

export const CartPreview: React.FC<CartPreviewProps> = ({
  data,
  onCheckout,
  isLoading = false,
  error = null,
}) => {
  const [expandedSections, setExpandedSections] = React.useState<Set<string>>(
    new Set(Object.keys(data.items_by_section))
  );

  // Calculate subtotal and delivery
  const subtotal = useMemo(() => {
    return Object.values(data.items_by_section)
      .flat()
      .reduce((sum, item) => sum + item.price * item.quantity, 0);
  }, [data.items_by_section]);

  const deliveryPrice = data.delivery_slot?.price || 0;
  const total = subtotal + deliveryPrice;

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6">
        <div className="flex items-start gap-4">
          <AlertCircle className="h-6 w-6 flex-shrink-0 text-red-600 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-red-900">Cart Generation Failed</h3>
            <p className="mt-2 text-red-800">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8">
        <div className="flex items-center justify-center gap-3">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" />
          <span className="text-gray-600">Generating your shopping cart...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Cart Header */}
      <div className="rounded-lg border border-gray-200 bg-gradient-to-br from-blue-50 to-indigo-50 p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <ShoppingCart className="h-8 w-8 text-blue-600" />
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Your Shopping Cart</h2>
              <p className="text-sm text-gray-600 mt-1">
                {data.item_count} items • Ready for checkout
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-gray-900">{formatEUR(total)}</p>
            <p className="text-xs text-gray-500 mt-1">Total with delivery</p>
          </div>
        </div>
      </div>

      {/* Delivery Slot Info */}
      {data.delivery_slot && (
        <div className="rounded-lg border border-green-200 bg-green-50 p-4">
          <div className="flex items-center gap-3">
            <CheckCircle className="h-5 w-5 text-green-600" />
            <div className="flex-1">
              <p className="font-semibold text-green-900">Delivery Scheduled</p>
              <p className="text-sm text-green-700">
                <Truck className="inline h-4 w-4 mr-1" />
                {new Date(data.delivery_slot.date).toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  year: 'numeric',
                })}{' '}
                • {data.delivery_slot.time_window} ({formatEUR(data.delivery_slot.price)})
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Items by Section */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-gray-900">Items by Section</h3>

        {Object.entries(data.items_by_section).map(([section, items]) => (
          <div
            key={section}
            className="rounded-lg border border-gray-200 bg-white overflow-hidden hover:shadow-sm transition-shadow"
          >
            {/* Section Header */}
            <button
              onClick={() => toggleSection(section)}
              className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{sectionIcons[section] || '📦'}</span>
                <div className="text-left">
                  <p className="font-semibold text-gray-900 capitalize">
                    {section.replace('_', ' ')}
                  </p>
                  <p className="text-sm text-gray-500">{items.length} item(s)</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-gray-900">
                  {formatEUR(items
                    .reduce((sum, item) => sum + item.price * item.quantity, 0))}
                </span>
                {expandedSections.has(section) ? (
                  <ChevronUp className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                )}
              </div>
            </button>

            {/* Items List */}
            {expandedSections.has(section) && (
              <div className="border-t border-gray-200 divide-y">
                {items.map((item, idx) => (
                  <div
                    key={`${section}-${item.product_id || idx}`}
                    className="px-4 py-3 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          {item.name}
                        </p>
                        <p className="text-sm text-gray-500">
                          {item.quantity} {item.unit}
                          {item.quantity > 1 ? '' : ''}
                        </p>
                      </div>
                      <div className="text-right flex-shrink-0">
                        <p className="font-semibold text-gray-900">
                          {formatEUR(item.price * item.quantity)}
                        </p>
                        <p className="text-xs text-gray-500">
                          {formatEUR(item.price)}/{item.unit}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Unavailable Items */}
      {data.unavailable_items.length > 0 && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-amber-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-semibold text-amber-900">
                {data.unavailable_items.length} Item(s) Not Available
              </p>
              <ul className="mt-2 text-sm text-amber-800 space-y-1">
                {data.unavailable_items.map((item, idx) => (
                  <li key={idx} className="flex items-center gap-2">
                    <span className="text-amber-600">•</span>
                    {item}
                  </li>
                ))}
              </ul>
              <p className="mt-3 text-xs text-amber-700">
                💡 You can add these items manually during checkout or select alternatives.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Price Breakdown */}
      <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Subtotal ({data.item_count} items)</span>
          <span className="font-medium text-gray-900">{formatEUR(subtotal)}</span>
        </div>
        {data.delivery_slot && (
          <div className="flex justify-between items-center pb-3 border-b border-gray-200">
            <span className="text-gray-600">
              <Truck className="inline h-4 w-4 mr-1" />
              Delivery Fee
            </span>
            <span className="font-medium text-gray-900">{formatEUR(deliveryPrice)}</span>
          </div>
        )}
        <div className="flex justify-between items-center pt-3">
          <span className="text-lg font-semibold text-gray-900">Total</span>
          <span className="text-2xl font-bold text-blue-600">{formatEUR(total)}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={onCheckout}
          className="flex-1 inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 transition-colors"
        >
          <ShoppingCart className="h-5 w-5" />
          Continue to Checkout
        </button>
        <a
          href={data.knuspr_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-1 inline-flex items-center justify-center gap-2 rounded-lg border border-gray-300 px-6 py-3 font-semibold text-gray-700 hover:bg-gray-50 transition-colors"
        >
          <Package className="h-5 w-5" />
          View on Knuspr
        </a>
      </div>

      {/* Cart ID for Reference */}
      <div className="text-center text-xs text-gray-500 pt-2">
        Cart ID: <code className="font-mono text-gray-600">{data.cart_id}</code>
      </div>
    </div>
  );
};

export default CartPreview;
