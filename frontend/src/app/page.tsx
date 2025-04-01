"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowRight, Boxes, FileText } from "lucide-react";
import Link from "next/link";
import { useEffect } from "react";

const HomePage = () => {
  useEffect(() => {
    document.title = "MolecularViz - AI Docking Report Generator";

    const mainContent = document.getElementById("home-page");
    if (mainContent) {
      mainContent.classList.add("opacity-0");
      setTimeout(() => {
        mainContent.classList.remove("opacity-0");
        mainContent.classList.add("animate-fade-in");
      }, 100);
    }

    return () => {
      if (mainContent) {
        mainContent.classList.remove("animate-fade-in");
      }
    };
  }, []);

  return (
    <div
      id="home-page"
      className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-slate-50 to-white px-4 py-12 transition-opacity duration-500"
    >
      <div className="w-full max-w-4xl mx-auto text-center">
        <div className="mb-6 inline-block">
          <div className="rounded-full bg-blue-500/10 p-3 animate-float">
            <Boxes size={32} className="text-blue-600" strokeWidth={1.5} />
          </div>
        </div>

        <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-gray-900 mb-4 tracking-tight">
          AI-Powered Molecular Docking Reports
        </h1>

        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Generate comprehensive visualizations and analysis reports from your
          molecular docking files with our advanced AI platform.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <Link href="/upload">
            <Button className="h-12 px-8 text-base bg-blue-600 hover:bg-blue-700 text-white shadow-soft flex items-center group hover:cursor-pointer">
              <span>Upload your file</span>
              <ArrowRight
                className="ml-1 group-hover:translate-x-1 transition-transform duration-200"
                size={18}
              />
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => (
            <Card
              key={index}
              className="border-0 shadow-smooth overflow-hidden bg-white/80 backdrop-blur-sm hover:shadow-md transition-shadow duration-300"
            >
              <CardContent className="p-6">
                <div className="rounded-full bg-blue-500/5 p-3 w-12 h-12 flex items-center justify-center mx-auto mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-medium text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

const features = [
  {
    title: "Comprehensive Reports",
    description:
      "AI-generated reports detailing docking scores, binding efficiencies, and potential drug efficacy.",
    icon: <FileText size={24} className="text-blue-600" strokeWidth={1.5} />,
  },
  {
    title: "3D Visualizations",
    description:
      "Advanced visualization tools to represent molecular interactions and binding positions.",
    icon: <Boxes size={24} className="text-blue-600" strokeWidth={1.5} />,
  },
];

export default HomePage;
