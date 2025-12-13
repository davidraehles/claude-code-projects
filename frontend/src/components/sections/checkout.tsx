'use client'

import { Container } from '../ui/container'
import { Button } from '../ui/button'

const deliveryApps = [
  { name: 'Knuspr', integrated: true },
  { name: 'Instacart', integrated: false },
  { name: 'Amazon Fresh', integrated: false },
  { name: 'Walmart+', integrated: false },
  { name: 'DoorDash', integrated: false },
]

export function Checkout() {
  return (
    <section id="checkout" className="py-20 md:py-32 lg:py-40 bg-neutral-50">
      <Container>
        {/* Section Label */}
        <div className="text-center mb-8">
          <span className="label inline-block px-6 py-2 bg-primary-100 text-primary-700 rounded-full text-sm font-semibold uppercase tracking-wider">
            ORDER
          </span>
        </div>

        {/* Headline */}
        <div className="text-center mb-16">
          <h2 className="heading-section text-4xl md:text-5xl lg:text-6xl mb-6 text-secondary-800 font-black">
            Straight to your cart.
          </h2>
          <p className="body-large text-xl md:text-2xl text-neutral-600 max-w-2xl mx-auto">
            One tap to your favorite delivery app. Checkout in seconds.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-16 items-center mb-20">
          {/* Delivery Partners */}
          <div>
            <h3 className="text-2xl font-bold text-secondary-800 mb-8">Choose Your Store</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {deliveryApps.map((app, index) => (
                <div
                  key={index}
                  className={`group p-4 md:p-6 border-2 rounded-2xl hover:scale-105 transition-all duration-300 cursor-pointer shadow-sm relative ${
                    app.integrated
                      ? 'border-primary-400 bg-primary-50 shadow-primary/20'
                      : 'border-neutral-200 bg-white hover:border-primary-400 hover:shadow-primary/20'
                  }`}
                >
                  {app.integrated && (
                    <span className="absolute -top-2 -right-2 bg-primary-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg">
                      Integrated
                    </span>
                  )}
                  <div className={`h-12 w-full rounded-lg flex items-center justify-center ${
                    app.integrated
                      ? 'bg-gradient-to-br from-primary-100 to-primary-200'
                      : 'bg-gradient-to-br from-neutral-200 to-neutral-300 group-hover:from-primary-100'
                  }`}>
                    <span className={`font-semibold text-sm uppercase tracking-wide ${
                      app.integrated ? 'text-primary-700' : 'text-neutral-700'
                    }`}>
                      {app.name}
                    </span>
                  </div>
                  {app.integrated && (
                    <p className="text-xs text-primary-600 mt-2 text-center font-medium">
                      One-click cart fill
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Phone Mockup with Cart */}
          <div className="relative mx-auto lg:ml-auto max-w-sm">
            <div className="relative bg-gradient-to-b from-neutral-200 to-neutral-300 rounded-3xl p-4 shadow-2xl max-w-xs mx-auto">
              {/* Screen */}
              <div className="bg-white rounded-2xl p-6 h-96 flex flex-col">
                {/* Cart Header */}
                <div className="flex items-center justify-between mb-6">
                  <h4 className="text-xl font-bold text-secondary-800">🛒 Your Cart</h4>
                  <div className="text-2xl">23 items</div>
                </div>

                {/* Items Preview */}
                <div className="space-y-3 mb-8 flex-1 overflow-hidden">
                  <div className="flex items-center gap-4 p-3 bg-accent-50 rounded-xl">
                    <div className="w-12 h-12 bg-gradient-to-br from-accent-400 to-accent-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">🍅</div>
                    <div className="flex-1">
                      <p className="font-semibold text-secondary-800">Cherry Tomatoes</p>
                      <p className="text-sm text-neutral-500">2 lbs</p>
                    </div>
                    <span className="font-mono font-bold text-lg text-accent-600">$4.99</span>
                  </div>
                  <div className="flex items-center gap-4 p-3 bg-primary-50 rounded-xl">
                    <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">🧄</div>
                    <div className="flex-1">
                      <p className="font-semibold text-secondary-800">Garlic</p>
                      <p className="text-sm text-neutral-500">5 cloves</p>
                    </div>
                    <span className="font-mono font-bold text-lg text-primary-600">$1.29</span>
                  </div>
                </div>

                {/* Total & CTA */}
                <div className="border-t pt-4">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-lg font-semibold text-secondary-800">Total</span>
                    <span className="text-2xl font-black text-secondary-800">$78.47</span>
                  </div>
                  <Button className="w-full bg-gradient-to-r from-primary-500 to-orange-500 text-white font-bold py-4 text-lg shadow-xl hover:shadow-primary/50">
                    Checkout Now →
                  </Button>
                </div>
              </div>

              {/* Phone bezel */}
              <div className="absolute inset-0 bg-black/20 rounded-2xl -inset-1" />
              <div className="absolute top-4 left-1/2 transform -translate-x-1/2 w-24 h-24 bg-white/50 rounded-full shadow-lg" />
            </div>
          </div>
        </div>
      </Container>
    </section>
  )
}
