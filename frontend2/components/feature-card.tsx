"use client"

import { type ReactNode, useState } from "react"
import { motion } from "framer-motion"

interface FeatureCardProps {
  icon: ReactNode
  title: string
  description: string
  variant?: "default" | "blockchain"
}

export default function FeatureCard({ icon, title, description, variant = "default" }: FeatureCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  const gradientColor =
    variant === "blockchain" ? "from-purple-900/20 to-transparent" : "from-emerald-900/20 to-transparent"

  const glowColor = variant === "blockchain" ? "bg-purple-500/10" : "bg-emerald-500/10"

  return (
    <motion.div
      className="bg-gradient-to-br from-gray-900 to-black p-8 rounded-xl border border-gray-800 relative overflow-hidden"
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      whileHover={{ y: -10 }}
      transition={{ duration: 0.3 }}
    >
      <div className="relative z-10">
        <div className="mb-6">{icon}</div>
        <h3 className="text-xl font-bold mb-3">{title}</h3>
        <p className="text-gray-400">{description}</p>
      </div>

      <motion.div
        className={`absolute inset-0 bg-gradient-to-br ${gradientColor}`}
        initial={{ opacity: 0 }}
        animate={{ opacity: isHovered ? 1 : 0 }}
        transition={{ duration: 0.3 }}
      />

      <motion.div
        className={`absolute -bottom-2 -right-2 w-24 h-24 ${glowColor} rounded-full blur-xl`}
        initial={{ scale: 0.8, opacity: 0.5 }}
        animate={{
          scale: isHovered ? 1.2 : 0.8,
          opacity: isHovered ? 0.8 : 0.5,
        }}
        transition={{ duration: 0.4 }}
      />
    </motion.div>
  )
}

