'use client';

import React, { useState } from 'react';
import { AlertCircle, Plus, X, Search, Lightbulb } from 'lucide-react';

export interface MissingItemsSuggestionsProps {
  unavailableItems: string[];
  onAddManualItem?: (item: string) => void;
  onDismiss?: () => void;
  cartSubtotal?: number;
  estimatedPrice?: number;
}

interface ManualItem {
  name: string;
  quantity: number;
  unit: string;
  estimatedPrice?: number;
}

const commonUnits = ['pcs', 'g', 'kg', 'ml', 'l', 'can', 'jar', 'bunch', 'package'];

const suggestedAlternatives: Record<string, string[]> = {
  'exotic ingredient': ['Regular substitute', 'Similar item', 'Alternative brand'],
  'rare spice': ['Common spice blend', 'Similar flavoring'],
  'specialty product': ['Standard alternative', 'Regular version'],
};

export const MissingItemsSuggestions: React.FC<MissingItemsSuggestionsProps> = ({
  unavailableItems,
  onAddManualItem,
  onDismiss,
  cartSubtotal = 0,
  estimatedPrice = 0,
}) => {
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [addingItem, setAddingItem] = useState<string | null>(null);
  const [manualItems, setManualItems] = useState<ManualItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');

  const toggleExpanded = (item: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(item)) {
      newExpanded.delete(item);
    } else {
      newExpanded.add(item);
    }
    setExpandedItems(newExpanded);
  };

  const handleAddManualItem = (item: string) => {
    const newItem: ManualItem = {
      name: item,
      quantity: 1,
      unit: 'pcs',
      estimatedPrice: 5.00,
    };

    setManualItems([...manualItems, newItem]);
    setAddingItem(null);

    if (onAddManualItem) {
      onAddManualItem(item);
    }
  };

  const removeManualItem = (idx: number) => {
    setManualItems(manualItems.filter((_, i) => i !== idx));
  };

  const updateManualItem = (idx: number, updates: Partial<ManualItem>) => {
    const updated = [...manualItems];
    updated[idx] = { ...updated[idx], ...updates };
    setManualItems(updated);
  };

  const totalManualItemsPrice = manualItems.reduce(
    (sum, item) => sum + (item.estimatedPrice || 0) * item.quantity,
    0
  );

  const newTotal = cartSubtotal + totalManualItemsPrice;

  if (unavailableItems.length === 0) {
    return null;
  }

  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-6 space-y-4">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="h-6 w-6 flex-shrink-0 text-amber-600 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-amber-900">
              {unavailableItems.length} Item(s) Not Found in Stock
            </h3>
            <p className="text-sm text-amber-800 mt-1">
              These ingredients weren't available in Knuspr. You can manually add alternatives
              or skip them.
            </p>
          </div>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="rounded p-1 hover:bg-amber-100 transition-colors"
            aria-label="Dismiss"
          >
            <X className="h-5 w-5 text-amber-600" />
          </button>
        )}
      </div>

      {/* Unavailable Items List */}
      <div className="space-y-2">
        {unavailableItems.map((item, idx) => (
          <div
            key={`unavailable-${idx}`}
            className="rounded-lg bg-white border border-amber-100 p-3 hover:shadow-sm transition-shadow"
          >
            <button
              onClick={() => toggleExpanded(item)}
              className="w-full flex items-center justify-between"
            >
              <div className="flex items-center gap-3 flex-1 text-left">
                <span className="text-lg">❌</span>
                <div>
                  <p className="font-medium text-gray-900">{item}</p>
                  <p className="text-xs text-gray-500">Out of stock</p>
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setAddingItem(item);
                  setExpandedItems(new Set([...expandedItems, item]));
                }}
                className="inline-flex items-center gap-1 rounded-lg bg-amber-100 hover:bg-amber-200 text-amber-700 px-3 py-1.5 text-sm font-medium transition-colors"
              >
                <Plus className="h-4 w-4" />
                Add Alternative
              </button>
            </button>

            {/* Expansion Panel */}
            {expandedItems.has(item) && (
              <div className="mt-3 pt-3 border-t border-amber-100 space-y-3">
                {/* Suggestions */}
                <div>
                  <p className="text-xs font-semibold text-gray-600 uppercase mb-2">
                    <Lightbulb className="inline h-3 w-3 mr-1" />
                    Suggested Alternatives
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {(suggestedAlternatives[item.toLowerCase()] || [
                      'Similar product',
                      'Alternative brand',
                      'Regular version',
                    ]).map((alt, altIdx) => (
                      <button
                        key={altIdx}
                        onClick={() => handleAddManualItem(alt)}
                        className="inline-flex items-center gap-1 rounded-full bg-green-100 hover:bg-green-200 text-green-700 text-xs font-medium px-3 py-1 transition-colors"
                      >
                        <Plus className="h-3 w-3" />
                        {alt}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Manual Add Form */}
                {addingItem === item && (
                  <div className="rounded-lg bg-amber-100 p-3 space-y-2">
                    <p className="text-xs font-semibold text-amber-900">Add Manual Item</p>
                    <div className="space-y-2">
                      <input
                        type="text"
                        placeholder="Item name"
                        defaultValue={item}
                        className="w-full rounded border border-amber-300 bg-white px-3 py-2 text-sm focus:border-amber-500 focus:outline-none"
                      />
                      <div className="grid grid-cols-3 gap-2">
                        <input
                          type="number"
                          placeholder="Qty"
                          min="0"
                          step="0.5"
                          defaultValue="1"
                          className="rounded border border-amber-300 bg-white px-2 py-1 text-sm focus:border-amber-500 focus:outline-none"
                        />
                        <select className="rounded border border-amber-300 bg-white px-2 py-1 text-sm focus:border-amber-500 focus:outline-none">
                          {commonUnits.map((unit) => (
                            <option key={unit} value={unit}>
                              {unit}
                            </option>
                          ))}
                        </select>
                        <input
                          type="number"
                          placeholder="€ Price"
                          min="0"
                          step="0.01"
                          defaultValue="5.00"
                          className="rounded border border-amber-300 bg-white px-2 py-1 text-sm focus:border-amber-500 focus:outline-none"
                        />
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            handleAddManualItem(item);
                            setAddingItem(null);
                          }}
                          className="flex-1 rounded bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold px-3 py-2 transition-colors"
                        >
                          Add Item
                        </button>
                        <button
                          onClick={() => setAddingItem(null)}
                          className="flex-1 rounded border border-amber-300 hover:bg-amber-100 text-amber-700 text-xs font-semibold px-3 py-2 transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Manually Added Items */}
      {manualItems.length > 0 && (
        <div className="rounded-lg bg-white border border-green-200 p-4 space-y-3">
          <p className="text-sm font-semibold text-green-900">
            ✓ {manualItems.length} Manually Added Item(s)
          </p>
          <div className="space-y-2">
            {manualItems.map((item, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between rounded bg-green-50 p-2"
              >
                <div className="text-sm">
                  <p className="font-medium text-green-900">{item.name}</p>
                  <p className="text-xs text-green-700">
                    {item.quantity} {item.unit}
                    {item.estimatedPrice && ` • €${(item.estimatedPrice * item.quantity).toFixed(2)}`}
                  </p>
                </div>
                <button
                  onClick={() => removeManualItem(idx)}
                  className="rounded p-1 hover:bg-green-200 transition-colors text-green-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Price Impact */}
      {manualItems.length > 0 && (
        <div className="rounded-lg bg-white border border-blue-200 p-3 space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Original Cart</span>
            <span className="font-medium text-gray-900">€{cartSubtotal.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Additional Items</span>
            <span className="font-medium text-gray-900">€{totalManualItemsPrice.toFixed(2)}</span>
          </div>
          <div className="flex justify-between items-center pt-2 border-t border-blue-100">
            <span className="text-sm font-semibold text-gray-900">New Total</span>
            <span className="text-lg font-bold text-blue-600">€{newTotal.toFixed(2)}</span>
          </div>
        </div>
      )}

      {/* Help Text */}
      <div className="rounded bg-blue-50 border border-blue-200 p-3">
        <p className="text-xs text-blue-900">
          <span className="font-semibold">📋 Tip:</span> You can also add or modify items directly
          during checkout on the Knuspr website.
        </p>
      </div>
    </div>
  );
};

export default MissingItemsSuggestions;
