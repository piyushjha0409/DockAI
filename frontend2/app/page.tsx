import { MoveRight, Database, FileText, LineChart, Microscope, Dna, Shield, Lock } from "lucide-react"
import Link from "next/link"
import MoleculeAnimation from "@/components/molecule-animation"
import FeatureCard from "@/components/feature-card"
import DemoVisualizer from "@/components/demo-visualizer"

export default function Home() {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <header className="container mx-auto py-6 px-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Dna className="h-8 w-8 text-emerald-500" />
            <span className="text-xl font-bold tracking-tight">DockAI</span>
          </div>
          <nav className="hidden md:flex gap-8">
            {["Features", "Demo", "Research", "Pricing", "Contact"].map((item) => (
              <Link
                key={item}
                href={`#${item.toLowerCase()}`}
                className="text-gray-400 hover:text-emerald-400 transition-colors duration-300"
              >
                {item}
              </Link>
            ))}
          </nav>
          <Link
            href="/upload"
            className="bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-md transition-colors duration-300"
          >
            Try Demo
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 relative overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <MoleculeAnimation />
        </div>
        <div className="relative z-10 max-w-3xl">
          <div className="inline-block px-3 py-1 rounded-full bg-emerald-900/50 text-emerald-400 text-sm font-medium mb-6 border border-emerald-800">
            Advanced Molecular Analysis
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">AI-Powered Molecular Docking Reports</h1>
          <p className="text-xl text-gray-300 mb-8 leading-relaxed">
            Generate comprehensive reports and visualizations of docking results, securely stored on the Solana
            blockchain to prevent tampering. Perfect for research integrity and stakeholder presentations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href="#features"
              className="group bg-emerald-600 hover:bg-emerald-500 px-6 py-3 rounded-md text-center transition-all duration-300 flex items-center justify-center gap-2"
            >
              Explore Features
              <MoveRight className="h-4 w-4 group-hover:translate-x-1 transition-transform duration-300" />
            </Link>
            <Link
              href="#research"
              className="group bg-transparent border border-emerald-600 hover:border-emerald-500 px-6 py-3 rounded-md text-center transition-all duration-300"
            >
              Research Papers
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold mb-4">Key Features</h2>
          <p className="text-gray-400 max-w-2xl mx-auto">
            Our AI agent transforms complex molecular docking data into clear, actionable insights
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <FeatureCard
            icon={<FileText className="h-10 w-10 text-emerald-500" />}
            title="Comprehensive Reports"
            description="Automatic generation of reports detailing the docking scores, binding efficiencies, and potential drug efficacy."
          />
          <FeatureCard
            icon={<LineChart className="h-10 w-10 text-emerald-500" />}
            title="Advanced Visualizations"
            description="Interactive visualization tools to represent molecular interactions and binding positions with stunning clarity."
          />
          <FeatureCard
            icon={<Database className="h-10 w-10 text-purple-500" />}
            title="Blockchain Storage"
            description="All reports are stored on the Solana blockchain, ensuring data integrity and preventing tampering of your valuable research."
            variant="blockchain"
          />
        </div>
      </section>

      {/* Blockchain Security Section */}
      <section className="py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-purple-900/20 via-black to-black"></div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="flex flex-col md:flex-row items-center gap-12">
            <div className="md:w-1/2">
              <div className="inline-block px-3 py-1 rounded-full bg-purple-900/50 text-purple-400 text-sm font-medium mb-6 border border-purple-800">
                Powered by Solana
              </div>
              <h2 className="text-4xl font-bold mb-6">Immutable Report Storage on Solana Blockchain</h2>
              <p className="text-gray-300 mb-8 text-lg">
                We store all generated reports on the Solana blockchain, ensuring your valuable research data can never
                be tampered with or lost.
              </p>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <div className="mt-1 bg-purple-900/30 p-1 rounded-full">
                    <Shield className="h-5 w-5 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-white">Tamper-Proof Reports</h3>
                    <p className="text-gray-400">
                      Once stored on-chain, your molecular docking reports become immutable and verifiable.
                    </p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <div className="mt-1 bg-purple-900/30 p-1 rounded-full">
                    <Lock className="h-5 w-5 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="font-medium text-white">Cryptographic Verification</h3>
                    <p className="text-gray-400">
                      Verify the authenticity of any report with cryptographic proof of its origin and timestamp.
                    </p>
                  </div>
                </li>
              </ul>
            </div>
            <div className="md:w-1/2 relative">
              <div className="relative z-10 bg-gradient-to-br from-gray-900 to-black p-6 rounded-xl border border-gray-800">
                <div className="flex items-center gap-3 mb-4">
                  <div className="h-3 w-3 rounded-full bg-purple-500"></div>
                  <div className="h-3 w-3 rounded-full bg-emerald-500"></div>
                  <div className="h-3 w-3 rounded-full bg-gray-500"></div>
                  <div className="text-sm text-gray-400 ml-2">Solana Transaction</div>
                </div>
                <div className="space-y-3 font-mono text-sm">
                  <div className="bg-black/50 p-3 rounded border border-gray-800">
                    <span className="text-purple-400">Transaction Hash:</span>{" "}
                    <span className="text-gray-300">5UfMmGvAS4ETS...</span>
                  </div>
                  <div className="bg-black/50 p-3 rounded border border-gray-800">
                    <span className="text-purple-400">Report ID:</span>{" "}
                    <span className="text-gray-300">DOCK_RPT_2023_07_15_A</span>
                  </div>
                  <div className="bg-black/50 p-3 rounded border border-gray-800">
                    <span className="text-purple-400">Timestamp:</span>{" "}
                    <span className="text-gray-300">2023-07-15T14:32:17Z</span>
                  </div>
                  <div className="bg-black/50 p-3 rounded border border-gray-800">
                    <span className="text-purple-400">Status:</span> <span className="text-emerald-400">Confirmed</span>
                  </div>
                  <div className="bg-black/50 p-3 rounded border border-gray-800">
                    <span className="text-purple-400">Data Hash:</span>{" "}
                    <span className="text-gray-300">Qm7TgGYF3P...</span>
                  </div>
                </div>
                <div className="mt-4 flex justify-between items-center">
                  <span className="text-xs text-gray-500">Solana Mainnet</span>
                  <span className="text-xs text-emerald-500">Verified ✓</span>
                </div>
              </div>

              {/* Decorative elements */}
              <div className="absolute -top-10 -right-10 w-40 h-40 bg-purple-500/10 rounded-full blur-3xl"></div>
              <div className="absolute -bottom-10 -left-10 w-40 h-40 bg-emerald-500/10 rounded-full blur-3xl"></div>

              {/* Blockchain connection lines */}
              <div className="absolute top-1/2 -right-4 w-8 h-1 bg-gradient-to-r from-purple-500 to-transparent"></div>
              <div className="absolute top-1/3 -left-4 w-8 h-1 bg-gradient-to-l from-purple-500 to-transparent"></div>
              <div className="absolute bottom-1/3 -right-4 w-8 h-1 bg-gradient-to-r from-purple-500 to-transparent"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Visualizer Section */}
      <section id="demo" className="py-20 bg-black/50 relative">
        <div className="absolute inset-0 bg-gradient-to-b from-emerald-900/10 to-black/20 pointer-events-none"></div>
        <div className="container mx-auto px-4 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">See It In Action</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Experience how our AI transforms complex molecular data into clear visualizations
            </p>
          </div>

          <DemoVisualizer />
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="bg-gradient-to-r from-emerald-900/30 to-blue-900/30 rounded-2xl p-8 md:p-12 border border-emerald-800/50 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-1/2 h-full opacity-20">
            <Microscope className="w-full h-full text-emerald-500" />
          </div>
          <div className="relative z-10 max-w-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Ready to transform your molecular research with blockchain security?
            </h2>
            <p className="text-gray-300 mb-8">
              Join leading research institutions already using our AI with Solana blockchain integration to accelerate
              and secure their drug discovery process.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="#contact"
                className="bg-emerald-600 hover:bg-emerald-500 px-6 py-3 rounded-md text-center transition-all duration-300"
              >
                Get Started
              </Link>
              <Link
                href="#pricing"
                className="bg-transparent border border-emerald-600 hover:border-emerald-500 px-6 py-3 rounded-md text-center transition-all duration-300"
              >
                View Pricing
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center gap-2 mb-6 md:mb-0">
              <Dna className="h-6 w-6 text-emerald-500" />
              <span className="text-lg font-bold">DockAI</span>
            </div>
            <div className="flex gap-8 text-sm text-gray-400">
              {["Privacy", "Terms", "Contact", "About"].map((item) => (
                <Link
                  key={item}
                  href={`#${item.toLowerCase()}`}
                  className="hover:text-emerald-400 transition-colors duration-300"
                >
                  {item}
                </Link>
              ))}
            </div>
          </div>
          <div className="mt-8 text-center text-gray-600 text-sm">
            © {new Date().getFullYear()} DockAI. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}

