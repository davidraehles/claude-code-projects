'use client'

import { useState } from 'react'
import { motion, useMotionValue, useTransform } from 'framer-motion'
import { Container } from '../ui/container'

const playlists = [
  {
    title: 'Week of Comfort Food',
    count: '7 meals',
    images: [
      'https://images.unsplash.com/photo-1541599468178-c4e6b41b0e8c?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1551782450-17144f9cee63?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1593560708920-61dd98c604ca?w=80&h=80&fit=crop'
    ]
  },
  {
    title: 'Quick Weeknights',
    count: '5 dinners',
    images: [
      'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1551218808-94e220e084d2?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1603360946369-dc9bb6258143?w=80&h=80&fit=crop'
    ]
  },
  {
    title: 'Veggie Forward',
    count: '7 meals',
    images: [
      'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1473093295043-cdd51249e6e9?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1567306301408-9e20e196e91d?w=80&h=80&fit=crop'
    ]
  },
  {
    title: 'Batch Cooking',
    count: 'Prep 3x',
    images: [
      'https://images.unsplash.com/photo-1556909114-f6e7ad7d3133?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1541596471337-2c8c0c8e6f9f?w=80&h=80&fit=crop',
      'https://images.unsplash.com/photo-1562440499-64e7f358f9d3?w=80&h=80&fit=crop'
    ]
  }
]

export function Planning() {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null)

  return (
    <section id="planning" className="py-20 md:py-32 lg:py-40 bg-gradient-to-b from-secondary-800 via-secondary-900 to-[#2D1F3D] relative overflow-hidden">
      <Container className="relative z-10">
        {/* Section Label */}
        <motion.div
          className="text-center mb-8"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6 }}
        >
          <span className="label inline-block px-6 py-2 bg-white/10 backdrop-blur-sm text-white/80 rounded-full text-sm font-semibold uppercase tracking-wider border border-white/20">
            PLAN
          </span>
        </motion.div>

        {/* Headline */}
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.3 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h2 className="heading-section text-4xl md:text-5xl lg:text-6xl mb-6 text-white font-black">
            Meal planning that feels like making a playlist.
          </h2>
          <p className="body-large text-xl md:text-2xl text-white/90 max-w-2xl mx-auto">
            Drag, drop, done. Your week, your way.
          </p>
        </motion.div>

        {/* Playlist Cards */}
        <div className="flex flex-wrap gap-6 lg:gap-8 justify-center lg:justify-start overflow-x-auto lg:overflow-visible pb-8 lg:pb-0 scrollbar-hide">
          {playlists.map((playlist, index) => (
            <PlaylistCard
              key={index}
              playlist={playlist}
              index={index}
              isDragged={draggedIndex === index}
              onDragStart={() => setDraggedIndex(index)}
              onDragEnd={() => setDraggedIndex(null)}
            />
          ))}
        </div>
      </Container>
    </section>
  )
}

// Separate component for individual playlist cards with drag functionality
function PlaylistCard({
  playlist,
  index,
  isDragged,
  onDragStart,
  onDragEnd,
}: {
  playlist: typeof playlists[0]
  index: number
  isDragged: boolean
  onDragStart: () => void
  onDragEnd: () => void
}) {
  const x = useMotionValue(0)
  const y = useMotionValue(0)

  // Transform values for drag feedback
  const rotateX = useTransform(y, [-100, 100], [10, -10])
  const rotateY = useTransform(x, [-100, 100], [-10, 10])

  return (
    <motion.div
      className="playlist-card min-w-[280px] lg:min-w-[320px] flex-shrink-0 backdrop-blur-xl bg-white/10 border border-white/20 rounded-3xl p-8 shadow-2xl cursor-grab active:cursor-grabbing"
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{
        duration: 0.6,
        delay: index * 0.1,
        type: 'spring',
        stiffness: 100,
        damping: 20,
      }}
      drag
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={0.2}
      dragTransition={{ bounceStiffness: 600, bounceDamping: 20 }}
      onDragStart={onDragStart}
      onDragEnd={onDragEnd}
      style={{
        x,
        y,
        rotateX,
        rotateY,
        zIndex: isDragged ? 50 : 1,
      }}
      whileHover={{
        scale: 1.05,
        backgroundColor: 'rgba(255, 255, 255, 0.2)',
        transition: { duration: 0.3 },
      }}
      whileTap={{ scale: 0.95 }}
    >
      <div className="playlist-card__grid grid grid-cols-2 gap-3 mb-6 pointer-events-none">
        {playlist.images.map((img, i) => (
          <motion.div
            key={i}
            className="w-full aspect-square rounded-xl overflow-hidden bg-gradient-to-br from-neutral-300 to-neutral-400"
            style={{
              backgroundImage: `url(${img})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
            }}
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.1 + i * 0.05 }}
          />
        ))}
      </div>
      <h3 className="playlist-card__title text-xl md:text-2xl font-semibold text-white mb-2 pointer-events-none">
        {playlist.title}
      </h3>
      <p className="playlist-card__count text-white/70 text-sm font-medium pointer-events-none">
        {playlist.count}
      </p>
    </motion.div>
  )
}
