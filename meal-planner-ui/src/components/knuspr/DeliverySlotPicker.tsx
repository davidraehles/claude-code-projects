'use client';

import React, { useMemo, useState } from 'react';
import { Calendar, Clock, DollarSign, AlertCircle, Check } from 'lucide-react';

export interface DeliverySlot {
  slot_id: string;
  date: string;
  time_window: string;
  price: number;
  available?: boolean;
}

interface DeliverySlotPickerProps {
  slots: DeliverySlot[];
  selected?: string;
  onSelect: (slot: DeliverySlot) => void;
  isLoading?: boolean;
  timePreference?: 'morning' | 'afternoon' | 'evening' | 'any';
}

const timeSlots = {
  morning: { label: '🌅 Morning', range: '08:00-12:00', icon: '☀️' },
  afternoon: { label: '🌤️ Afternoon', range: '12:00-18:00', icon: '🌤️' },
  evening: { label: '🌙 Evening', range: '18:00-21:00', icon: '🌙' },
};

const getTimeCategory = (timeWindow: string): 'morning' | 'afternoon' | 'evening' | 'unknown' => {
  const [start] = timeWindow.split('-');
  const hour = parseInt(start.split(':')[0], 10);

  if (hour >= 8 && hour < 12) return 'morning';
  if (hour >= 12 && hour < 18) return 'afternoon';
  if (hour >= 18 && hour < 21) return 'evening';
  return 'unknown';
};

export const DeliverySlotPicker: React.FC<DeliverySlotPickerProps> = ({
  slots,
  selected,
  onSelect,
  isLoading = false,
  timePreference = 'any',
}) => {
  const [hoveredSlot, setHoveredSlot] = useState<string | null>(null);

  // Group slots by date
  const slotsByDate = useMemo(() => {
    const grouped: Record<string, DeliverySlot[]> = {};

    slots.forEach((slot) => {
      const date = new Date(slot.date).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });

      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(slot);
    });

    return grouped;
  }, [slots]);

  // Sort dates
  const sortedDates = useMemo(() => {
    return Object.keys(slotsByDate).sort(
      (a, b) => new Date(a).getTime() - new Date(b).getTime()
    );
  }, [slotsByDate]);

  // Highlight preferred time slots
  const getSlotPriority = (slot: DeliverySlot): number => {
    if (timePreference === 'any') return 0;

    const category = getTimeCategory(slot.time_window);
    if (category === timePreference) return 2; // Highest priority
    if (category !== 'unknown') return 1; // Medium priority
    return 0;
  };

  const getCheapestSlot = (): DeliverySlot | null => {
    if (slots.length === 0) return null;
    return slots.reduce((min, slot) => (slot.price < min.price ? slot : min));
  };

  const getEarliestSlot = (): DeliverySlot | null => {
    if (slots.length === 0) return null;
    return slots[0];
  };

  if (isLoading) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8">
        <div className="flex items-center justify-center gap-3">
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-200 border-t-blue-600" />
          <span className="text-gray-600">Loading delivery slots...</span>
        </div>
      </div>
    );
  }

  if (slots.length === 0) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-6">
        <div className="flex items-start gap-4">
          <AlertCircle className="h-6 w-6 flex-shrink-0 text-amber-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-amber-900">No Delivery Slots Available</h3>
            <p className="mt-2 text-amber-800">
              There are no available delivery slots in the next 7 days. Please try again later.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const cheapestSlot = getCheapestSlot();
  const earliestSlot = getEarliestSlot();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Select Delivery</h3>
          <p className="text-sm text-gray-600">Choose your preferred delivery slot</p>
        </div>
        <div className="flex gap-2 text-xs font-medium">
          {timePreference !== 'any' && (
            <span className="rounded-full bg-blue-100 text-blue-700 px-3 py-1">
              {timeSlots[timePreference as keyof typeof timeSlots]?.label}
            </span>
          )}
        </div>
      </div>

      <div className="space-y-6">
        {sortedDates.map((date) => (
          <div key={date} className="space-y-3">
            <h4 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
              <Calendar className="inline h-4 w-4 mr-2" />
              {date}
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {slotsByDate[date].map((slot) => {
                const isSelected = selected === slot.slot_id;
                const isHovered = hoveredSlot === slot.slot_id;
                const priority = getSlotPriority(slot);
                const timeCategory = getTimeCategory(slot.time_window);
                const isCheapest = cheapestSlot?.slot_id === slot.slot_id;
                const isEarliest = earliestSlot?.slot_id === slot.slot_id;

                return (
                  <button
                    key={slot.slot_id}
                    onClick={() => onSelect(slot)}
                    onMouseEnter={() => setHoveredSlot(slot.slot_id)}
                    onMouseLeave={() => setHoveredSlot(null)}
                    className={`relative rounded-lg border-2 p-4 text-left transition-all ${
                      isSelected
                        ? 'border-blue-600 bg-blue-50 shadow-md'
                        : isHovered
                          ? 'border-gray-300 bg-gray-50 shadow-sm'
                          : priority === 2
                            ? 'border-green-300 bg-green-50'
                            : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    {/* Selection Indicator */}
                    {isSelected && (
                      <div className="absolute top-2 right-2">
                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-blue-600">
                          <Check className="h-4 w-4 text-white" />
                        </div>
                      </div>
                    )}

                    {/* Badges */}
                    <div className="mb-2 flex gap-2 flex-wrap">
                      {isCheapest && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 text-amber-700 text-xs font-semibold px-2 py-1">
                          <DollarSign className="h-3 w-3" />
                          Cheapest
                        </span>
                      )}
                      {isEarliest && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-purple-100 text-purple-700 text-xs font-semibold px-2 py-1">
                          <Clock className="h-3 w-3" />
                          Earliest
                        </span>
                      )}
                      {priority === 2 && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-green-100 text-green-700 text-xs font-semibold px-2 py-1">
                          ✓ Matches Preference
                        </span>
                      )}
                    </div>

                    {/* Time Window */}
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl">
                        {timeSlots[timeCategory as keyof typeof timeSlots]?.icon || '🕐'}
                      </span>
                      <div>
                        <p className="font-semibold text-gray-900">{slot.time_window}</p>
                        <p className="text-xs text-gray-500">
                          {timeCategory === 'unknown'
                            ? 'Custom time'
                            : timeSlots[timeCategory as keyof typeof timeSlots]?.label}
                        </p>
                      </div>
                    </div>

                    {/* Price */}
                    <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                      <span className="text-sm text-gray-600">Delivery Fee</span>
                      <span className="text-lg font-bold text-gray-900">
                        €{slot.price.toFixed(2)}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Info Box */}
      <div className="rounded-lg bg-blue-50 border border-blue-200 p-4">
        <p className="text-sm text-blue-900">
          <span className="font-semibold">💡 Tip:</span> Early morning and late evening slots often
          have lower delivery fees. Check all options to find the best value!
        </p>
      </div>
    </div>
  );
};

export default DeliverySlotPicker;
