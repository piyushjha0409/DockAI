"use client"

import { useState, useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { ArrowRight, Play, Pause, RotateCcw } from "lucide-react"

export default function DemoVisualizer() {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const [rotation, setRotation] = useState(0)

  const steps = [
    { title: "Data Import", description: "Importing molecular structure data" },
    { title: "Analysis", description: "Analyzing binding sites and interactions" },
    { title: "Visualization", description: "Generating 3D visualizations" },
    { title: "Report Generation", description: "Creating comprehensive reports" },
    { title: "Blockchain Storage", description: "Securing data on Solana blockchain" },
  ]

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    canvas.width = 500
    canvas.height = 500

    const drawMolecule = () => {
      if (!ctx) return

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      // Center of the canvas
      const centerX = canvas.width / 2
      const centerY = canvas.height / 2

      // Draw the molecule
      ctx.save()
      ctx.translate(centerX, centerY)
      ctx.rotate((rotation * Math.PI) / 180)

      // Draw atoms
      const atoms = [
        { x: 0, y: 0, radius: 20, color: "#00ffaa" },
        { x: -60, y: -60, radius: 15, color: "#ff3e66" },
        { x: 60, y: -60, radius: 15, color: "#3e66ff" },
        { x: 60, y: 60, radius: 15, color: "#ff3e66" },
        { x: -60, y: 60, radius: 15, color: "#3e66ff" },
      ]

      // Draw bonds (lines between atoms)
      ctx.strokeStyle = "rgba(255, 255, 255, 0.5)"
      ctx.lineWidth = 3

      for (let i = 1; i < atoms.length; i++) {
        ctx.beginPath()
        ctx.moveTo(0, 0)
        ctx.lineTo(atoms[i].x, atoms[i].y)
        ctx.stroke()
      }

      // Draw atoms
      atoms.forEach((atom) => {
        // Glow effect
        const gradient = ctx.createRadialGradient(atom.x, atom.y, 0, atom.x, atom.y, atom.radius * 2)
        gradient.addColorStop(0, atom.color)
        gradient.addColorStop(1, "transparent")

        ctx.fillStyle = gradient
        ctx.beginPath()
        ctx.arc(atom.x, atom.y, atom.radius * 1.5, 0, Math.PI * 2)
        ctx.fill()

        // Solid atom
        ctx.fillStyle = atom.color
        ctx.beginPath()
        ctx.arc(atom.x, atom.y, atom.radius, 0, Math.PI * 2)
        ctx.fill()

        // Highlight
        ctx.fillStyle = "rgba(255, 255, 255, 0.8)"
        ctx.beginPath()
        ctx.arc(atom.x - atom.radius / 3, atom.y - atom.radius / 3, atom.radius / 4, 0, Math.PI * 2)
        ctx.fill()
      })

      ctx.restore()
    }

    const animate = () => {
      setRotation((prev) => (prev + 0.2) % 360)
      drawMolecule()
      animationRef.current = requestAnimationFrame(animate)
    }

    if (isPlaying) {
      animationRef.current = requestAnimationFrame(animate)
    } else {
      drawMolecule()
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isPlaying, rotation])

  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setCurrentStep((prev) => (prev + 1) % steps.length)
      }, 3000)

      return () => clearInterval(interval)
    }
  }, [isPlaying, steps.length])

  const handleReset = () => {
    setIsPlaying(false)
    setCurrentStep(0)
    setRotation(0)
  }

  return (
    <div className="bg-gray-900/30 rounded-xl p-6 border border-gray-800 max-w-4xl mx-auto">
      <div className="grid md:grid-cols-2 gap-8">
        <div className="flex flex-col justify-center">
          <h3 className="text-2xl font-bold mb-6">Interactive Molecular Visualization</h3>

          <div className="space-y-6">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                className={`flex items-start gap-4 p-4 rounded-lg transition-colors duration-300 ${
                  currentStep === index ? "bg-emerald-900/30 border border-emerald-800/50" : ""
                }`}
                initial={{ opacity: 0.7, x: -10 }}
                animate={{
                  opacity: currentStep === index ? 1 : 0.7,
                  x: currentStep === index ? 0 : -10,
                }}
                transition={{ duration: 0.3 }}
              >
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                    currentStep === index ? "bg-emerald-500 text-black" : "bg-gray-800 text-gray-400"
                  }`}
                >
                  {currentStep > index ? <ArrowRight className="h-4 w-4" /> : index + 1}
                </div>
                <div>
                  <h4 className="font-medium text-lg">{step.title}</h4>
                  <p className="text-gray-400 mt-1">{step.description}</p>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="flex gap-4 mt-8">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-md transition-colors duration-300"
            >
              {isPlaying ? (
                <>
                  <Pause className="h-4 w-4" />
                  Pause
                </>
              ) : (
                <>
                  <Play className="h-4 w-4" />
                  Play Demo
                </>
              )}
            </button>
            <button
              onClick={handleReset}
              className="flex items-center gap-2 bg-transparent border border-gray-700 hover:border-gray-600 px-4 py-2 rounded-md transition-colors duration-300"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </button>
          </div>
        </div>

        <div className="flex items-center justify-center">
          <div className="relative">
            <canvas ref={canvasRef} className="w-full max-w-[300px] h-[300px] rounded-xl bg-black/50" />
            <div className="absolute inset-0 pointer-events-none rounded-xl bg-gradient-to-br from-transparent to-emerald-900/20" />
          </div>
        </div>
      </div>
    </div>
  )
}

