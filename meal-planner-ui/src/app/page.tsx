'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card'

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const closeMobileMenu = () => setMobileMenuOpen(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md fixed w-full z-50 border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-2xl sm:text-3xl">🍽️</span>
              <span className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                MealPlannerAI
              </span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="#features" className="text-gray-600 hover:text-blue-600 transition-colors">
                Features
              </Link>
              <Link href="#how-it-works" className="text-gray-600 hover:text-blue-600 transition-colors">
                How It Works
              </Link>
              <Link href="#pricing" className="text-gray-600 hover:text-blue-600 transition-colors">
                Pricing
              </Link>
              <Link href="/login">
                <Button variant="ghost" size="sm">
                  Login
                </Button>
              </Link>
              <Link href="/signup">
                <Button variant="primary" size="sm">
                  Get Started Free
                </Button>
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-gray-600 hover:text-gray-900"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>

          {/* Mobile Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden mt-4 pb-4 space-y-3">
              <Link
                href="#features"
                onClick={closeMobileMenu}
                className="block py-2 px-4 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Features
              </Link>
              <Link
                href="#how-it-works"
                onClick={closeMobileMenu}
                className="block py-2 px-4 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                How It Works
              </Link>
              <Link
                href="#pricing"
                onClick={closeMobileMenu}
                className="block py-2 px-4 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Pricing
              </Link>
              <Link href="/login" onClick={closeMobileMenu} className="block">
                <Button variant="ghost" className="w-full">
                  Login
                </Button>
              </Link>
              <Link href="/signup" onClick={closeMobileMenu} className="block">
                <Button variant="primary" className="w-full">
                  Get Started Free
                </Button>
              </Link>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-24 sm:pt-32 pb-16 sm:pb-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-gray-900 mb-6 leading-tight">
              AI-Powered Meal Planning<br />
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                in Minutes
              </span>
            </h1>
            <p className="text-lg sm:text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
              Generate personalized weekly meal plans with smart recipes, automatic grocery lists,
              and nutrition tracking. Save time, eat better, and reduce food waste.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/signup">
                <Button variant="primary" size="lg">
                  Start Free Trial
                </Button>
              </Link>
              <Link href="#how-it-works">
                <Button variant="outline" size="lg">
                  See How It Works
                </Button>
              </Link>
            </div>
            <p className="text-sm text-gray-500 mt-4">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 sm:py-20 px-4 bg-white">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for Better Meal Planning
            </h2>
            <p className="text-lg sm:text-xl text-gray-600">
              Powered by AI to make healthy eating effortless
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card hover>
              <CardHeader>
                <div className="text-4xl mb-4">🎯</div>
                <CardTitle>Smart Filters</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Dietary restrictions, allergies, cuisine preferences, and nutrition goals
                  automatically applied to every meal plan.
                </CardDescription>
              </CardContent>
            </Card>

            <Card hover>
              <CardHeader>
                <div className="text-4xl mb-4">🔄</div>
                <CardTitle>Automatic Variety</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  AI ensures you never eat the same thing twice in a week.
                  Balanced cuisines and ingredients for maximum enjoyment.
                </CardDescription>
              </CardContent>
            </Card>

            <Card hover>
              <CardHeader>
                <div className="text-4xl mb-4">💰</div>
                <CardTitle>Budget Tracking</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Set your weekly budget and get meal plans optimized for cost.
                  Track spending and save money on groceries.
                </CardDescription>
              </CardContent>
            </Card>

            <Card hover>
              <CardHeader>
                <div className="text-4xl mb-4">🛒</div>
                <CardTitle>One-Click Groceries</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Automatic grocery lists with smart consolidation.
                  Export to your favorite shopping app or print for the store.
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-16 sm:py-20 px-4 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg sm:text-xl text-gray-600">
              Get your personalized meal plan in 4 simple steps
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                step: '1',
                title: 'Set Preferences',
                description: 'Tell us your dietary restrictions, cuisine preferences, and nutrition goals',
              },
              {
                step: '2',
                title: 'Import Recipes',
                description: 'Add recipes from the web or use our library of 10,000+ recipes',
              },
              {
                step: '3',
                title: 'Generate Plan',
                description: 'AI creates an optimized weekly meal plan in seconds',
              },
              {
                step: '4',
                title: 'Shop & Cook',
                description: 'Get your grocery list and start cooking delicious meals',
              },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                  {item.step}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-16 sm:py-20 px-4 bg-white">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-lg sm:text-xl text-gray-600">
              Choose the plan that works for you
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Free Tier */}
            <Card>
              <CardHeader>
                <CardTitle>Free</CardTitle>
                <div className="text-4xl font-bold text-gray-900 mt-4">
                  $0
                  <span className="text-lg font-normal text-gray-600">/month</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">5 meal plans per month</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Basic recipe library</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Grocery lists</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Email support</span>
                  </li>
                </ul>
                <Link href="/signup" className="block">
                  <Button variant="outline" className="w-full">
                    Get Started
                  </Button>
                </Link>
              </CardContent>
            </Card>

            {/* Pro Tier */}
            <Card className="border-2 border-blue-600 relative">
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
                  MOST POPULAR
                </span>
              </div>
              <CardHeader>
                <CardTitle>Pro</CardTitle>
                <div className="text-4xl font-bold text-gray-900 mt-4">
                  $9
                  <span className="text-lg font-normal text-gray-600">/month</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Unlimited meal plans</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Import from any website</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Advanced nutrition tracking</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Budget optimization</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Priority support</span>
                  </li>
                </ul>
                <Link href="/signup" className="block">
                  <Button variant="primary" className="w-full">
                    Start Free Trial
                  </Button>
                </Link>
              </CardContent>
            </Card>

            {/* Premium Tier */}
            <Card>
              <CardHeader>
                <CardTitle>Premium</CardTitle>
                <div className="text-4xl font-bold text-gray-900 mt-4">
                  $19
                  <span className="text-lg font-normal text-gray-600">/month</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 mb-6">
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Everything in Pro</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Family meal plans (4+ people)</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">Custom recipe collections</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">API access</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    <span className="text-gray-600">White-label options</span>
                  </li>
                </ul>
                <Link href="/signup" className="block">
                  <Button variant="secondary" className="w-full">
                    Get Premium
                  </Button>
                </Link>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 sm:py-20 px-4 bg-gray-50">
        <div className="container mx-auto max-w-4xl">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              Frequently Asked Questions
            </h2>
          </div>

          <div className="space-y-6">
            {[
              {
                q: 'How does the AI meal planner work?',
                a: 'Our AI analyzes your dietary preferences, nutrition goals, and recipe library to generate optimized weekly meal plans. It uses constraint optimization to ensure variety, balanced nutrition, and budget adherence.',
              },
              {
                q: 'Can I import my own recipes?',
                a: 'Yes! Pro and Premium users can import recipes from any website URL. Our AI automatically extracts ingredients, instructions, and nutrition information.',
              },
              {
                q: 'What dietary restrictions are supported?',
                a: 'We support vegetarian, vegan, gluten-free, dairy-free, keto, paleo, and many more. You can also specify custom allergies and excluded ingredients.',
              },
              {
                q: 'How does the grocery list work?',
                a: 'After generating a meal plan, we automatically consolidate all ingredients into a categorized grocery list. You can check off items as you shop or export to your favorite app.',
              },
              {
                q: 'Can I customize the meal plans?',
                a: 'Absolutely! You can swap out recipes, adjust servings, or regenerate specific days. The AI adapts to your changes and maintains nutritional balance.',
              },
              {
                q: 'Is there a mobile app?',
                a: 'Our web app is fully mobile-responsive and works great on phones and tablets. Native iOS and Android apps are coming soon!',
              },
            ].map((faq, idx) => (
              <Card key={idx}>
                <CardHeader>
                  <CardTitle className="text-lg">{faq.q}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription className="text-base">{faq.a}</CardDescription>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 sm:py-20 px-4 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to Transform Your Meal Planning?
          </h2>
          <p className="text-lg sm:text-xl text-blue-100 mb-8">
            Join thousands of users saving time and eating better with AI-powered meal plans
          </p>
          <Link href="/signup">
            <Button variant="secondary" size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
              Start Your Free Trial
            </Button>
          </Link>
          <p className="text-sm text-blue-100 mt-4">
            No credit card required • 14-day free trial
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <span className="text-3xl">🍽️</span>
                <span className="text-xl font-bold text-white">MealPlannerAI</span>
              </div>
              <p className="text-sm">
                AI-powered meal planning made simple and delicious.
              </p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="#features" className="hover:text-white transition-colors">Features</Link></li>
                <li><Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="/recipes" className="hover:text-white transition-colors">Recipes</Link></li>
                <li><Link href="/blog" className="hover:text-white transition-colors">Blog</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
                <li><Link href="/careers" className="hover:text-white transition-colors">Careers</Link></li>
                <li><Link href="/press" className="hover:text-white transition-colors">Press</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Legal</h3>
              <ul className="space-y-2 text-sm">
                <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link></li>
                <li><Link href="/terms" className="hover:text-white transition-colors">Terms</Link></li>
                <li><Link href="/security" className="hover:text-white transition-colors">Security</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-sm text-center">
            <p>&copy; 2025 MealPlannerAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
