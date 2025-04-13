"use client"

import { useEffect, useRef } from "react"

export default function MoleculeAnimation() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    // Set canvas dimensions
    const setCanvasDimensions = () => {
      canvas.width = window.innerWidth
      canvas.height = window.innerHeight
    }

    setCanvasDimensions()
    window.addEventListener("resize", setCanvasDimensions)

    // Particle class
    class Particle {
      x: number
      y: number
      size: number
      speedX: number
      speedY: number
      color: string
      connections: Particle[]
      isBlockchainNode: boolean

      constructor(x: number, y: number) {
        this.x = x
        this.y = y
        this.size = Math.random() * 3 + 1
        this.speedX = Math.random() * 1 - 0.5
        this.speedY = Math.random() * 1 - 0.5
        // Randomly assign some particles to be "blockchain nodes"
        this.isBlockchainNode = Math.random() < 0.2
        this.color = this.isBlockchainNode ? "#9333ea" : "#00ffaa" // Purple for blockchain nodes
        this.connections = []
      }

      update() {
        this.x += this.speedX
        this.y += this.speedY

        if (this.x < 0 || this.x > canvas.width) {
          this.speedX = -this.speedX
        }
        if (this.y < 0 || this.y > canvas.height) {
          this.speedY = -this.speedY
        }
      }

      draw() {
        if (!ctx) return

        // Different appearance for blockchain nodes
        if (this.isBlockchainNode) {
          ctx.fillStyle = this.color
          ctx.beginPath()
          ctx.rect(this.x - this.size, this.y - this.size, this.size * 2, this.size * 2)
          ctx.fill()

          // Add a glow effect
          const glow = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size * 4)
          glow.addColorStop(0, "rgba(147, 51, 234, 0.5)")
          glow.addColorStop(1, "rgba(147, 51, 234, 0)")

          ctx.fillStyle = glow
          ctx.beginPath()
          ctx.arc(this.x, this.y, this.size * 4, 0, Math.PI * 2)
          ctx.fill()
        } else {
          // Original circular atoms
          ctx.fillStyle = this.color
          ctx.beginPath()
          ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
          ctx.fill()
        }
      }

      connectParticles(particles: Particle[]) {
        this.connections = []
        for (const particle of particles) {
          if (this === particle) continue

          const distance = Math.sqrt(Math.pow(this.x - particle.x, 2) + Math.pow(this.y - particle.y, 2))

          if (distance < 150) {
            this.connections.push(particle)
            if (!ctx) continue

            // Different style for connections involving blockchain nodes
            if (this.isBlockchainNode || particle.isBlockchainNode) {
              ctx.strokeStyle = `rgba(147, 51, 234, ${1 - distance / 150})`
              ctx.lineWidth = 1

              // Dashed line for blockchain connections
              ctx.setLineDash([2, 3])
            } else {
              ctx.strokeStyle = `rgba(0, 255, 170, ${1 - distance / 150})`
              ctx.lineWidth = 0.5
              ctx.setLineDash([])
            }

            ctx.beginPath()
            ctx.moveTo(this.x, this.y)
            ctx.lineTo(particle.x, particle.y)
            ctx.stroke()
            ctx.setLineDash([]) // Reset dash pattern
          }
        }
      }
    }

    // Create particles
    const particleCount = Math.min(50, Math.floor(window.innerWidth / 30))
    const particles: Particle[] = []

    for (let i = 0; i < particleCount; i++) {
      const x = Math.random() * canvas.width
      const y = Math.random() * canvas.height
      particles.push(new Particle(x, y))
    }

    // Animation loop
    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      for (const particle of particles) {
        particle.update()
        particle.draw()
        particle.connectParticles(particles)
      }

      requestAnimationFrame(animate)
    }

    animate()

    return () => {
      window.removeEventListener("resize", setCanvasDimensions)
    }
  }, [])

  return <canvas ref={canvasRef} className="w-full h-full" />
}

