'use client'

import { Container } from '../ui/container'
import { Button } from '../ui/button'
import Link from 'next/link'

export function Footer() {
  return (
    <section className="py-20 md:py-32 bg-gradient-to-t from-primary-500 via-orange-500 to-primary-600 text-white relative overflow-hidden">
      <Container>
        {/* Final CTA */}
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-black mb-8 leading-tight">
            Ready to simplify dinner?
          </h2>

          <Link href="/signup" className="block mb-6">
            <Button className="text-xl lg:text-2xl px-12 lg:px-16 py-8 lg:py-10 font-bold shadow-2xl shadow-white/30 hover:shadow-white/50 w-full max-w-md mx-auto h-auto">
              Get Started Free
            </Button>
          </Link>

          <Link href="/login" className="block">
            <Button className="text-lg px-8 lg:px-12 py-6 lg:py-8 font-semibold border-2 border-white/50 bg-white/10 backdrop-blur-sm hover:bg-white/20 hover:border-white w-full max-w-sm mx-auto h-auto">
              Already have an account? Login
            </Button>
          </Link>

          {/* Trust badges */}
          <div className="flex flex-wrap justify-center gap-8 mt-16 text-sm">
            <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-6 py-3 rounded-2xl">
              <span>🚀</span>
              <span>Built with AI</span>
            </div>
            <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-6 py-3 rounded-2xl">
              <span>⚡</span>
              <span>Lightning Fast</span>
            </div>
            <div className="flex items-center gap-2 bg-white/20 backdrop-blur-sm px-6 py-3 rounded-2xl">
              <span>🛡️</span>
              <span>Privacy First</span>
            </div>
          </div>
        </div>

        {/* Footer Content */}
        <div className="border-t border-white/20 pt-12">
          <div className="grid md:grid-cols-4 gap-8 text-center md:text-left">
            <div>
              <h3 className="text-2xl font-black mb-4">Go, Cart!</h3>
              <p className="text-white/80 mb-4">
                Favorites on repeat. New loves on deck. Groceries on autopilot.
              </p>
              <div className="flex justify-center md:justify-start gap-4">
                <a href="#" className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center hover:bg-white/40 transition-all">📱</a>
                <a href="#" className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center hover:bg-white/40 transition-all">💻</a>
                <a href="#" className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center hover:bg-white/40 transition-all">🐦</a>
              </div>
            </div>

            <div>
              <h4 className="font-semibold mb-6">Product</h4>
              <ul className="space-y-3 text-sm">
                <li><a href="#" className="hover:text-white/80 transition-colors">Curate</a></li>
                <li><a href="#" className="hover:text-white/80 transition-colors">Plan</a></li>
                <li><a href="#" className="hover:text-white/80 transition-colors">Aggregate</a></li>
                <li><a href="#" className="hover:text-white/80 transition-colors">Order</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-6">Company</h4>
              <ul className="space-y-3 text-sm">
                <li><a href="#" className="hover:text-white/80 transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white/80 transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white/80 transition-colors">Press</a></li>
                <li><a href="#" className="hover:text-white/80 transition-colors">Contact</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-6">Legal</h4>
              <ul className="space-y-3 text-sm">
                <li><a href="#" className="hover:text-white/80 transition-colors">Privacy</a></li>
                <li><a href="#" className="hover:text-white/80 transition-colors">Terms</a></li>
                <li><a href="#" className="hover:text-white/80 transition-colors">Security</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-white/10 mt-12 pt-8 text-center text-sm text-white/60">
            <p>&copy; 2025 Go, Cart!. All rights reserved.</p>
          </div>
        </div>
      </Container>
    </section>
  )
}
