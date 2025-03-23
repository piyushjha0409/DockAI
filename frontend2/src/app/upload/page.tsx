"use client";

import FileUploader from "@/components/FileUploader";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowLeft, ChevronDown } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

const UploadPage = () => {
  const [infoExpanded, setInfoExpanded] = useState(false);

  // Apply fade-in animation to the entire page
  useEffect(() => {
    document.title = "Upload Docking Files - MolecularViz";

    const mainContent = document.getElementById("upload-page");
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
      id="upload-page"
      className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-slate-50 to-white px-4 py-12 transition-opacity duration-500"
    >
      <div className="w-full max-w-4xl mx-auto">
        <div className="mb-8 flex items-center">
          <Link
            href="/"
            className="group flex items-center text-gray-500 hover:text-gray-800 transition-colors duration-200"
          >
            <ArrowLeft
              size={18}
              className="mr-2 group-hover:translate-x-[-3px] transition-transform duration-200"
            />
            <span className="text-sm font-medium">Back to Home</span>
          </Link>
        </div>

        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-3">
            Upload Autodock Vina Output Files
          </h1>
          <p className="text-gray-600 max-w-xl mx-auto">
            Please upload two Autodock Vina processed files: a .txt output file and a .pdbqt file
            to generate comprehensive reports and visualizations.
          </p>
        </div>

        <Card className="border-0 shadow-smooth overflow-hidden bg-white/80 backdrop-blur-sm mb-8">
          <CardContent className="p-6 sm:p-8">
            <div className="mb-4 p-4 bg-amber-50 rounded-md text-amber-800 text-sm">
              <div className="flex justify-between items-center">
                <p className="font-medium">⚠️ Important: Pre-processing Required</p>
                <button 
                  onClick={() => setInfoExpanded(!infoExpanded)} 
                  className="text-amber-700 hover:text-amber-900"
                  aria-label={infoExpanded ? "Collapse information" : "Expand information"}
                >
                  <ChevronDown 
                    size={20} 
                    className={`transform transition-transform ${infoExpanded ? "rotate-180" : ""}`} 
                  />
                </button>
              </div>
              <p className="mt-1">
                You must process your ligand and protein files through Autodock Vina before uploading.
                Our system expects the output files (.txt and .pdbqt) from a completed docking operation.
              </p>
              
              {infoExpanded && (
                <div className="mt-3 pt-3 border-t border-amber-200 text-amber-800/90">
                  <h4 className="font-medium mb-2">How to generate required files:</h4>
                  <ol className="list-decimal pl-5 space-y-1">
                    <li>Run Autodock Vina with your protein and ligand files</li>
                    <li>After processing, collect the .txt output file containing binding affinities</li>
                    <li>Collect the corresponding .pdbqt file with the 3D structure information</li>
                    <li>Upload both files here to visualize and analyze results</li>
                  </ol>
                </div>
              )}
            </div>
            
            <FileUploader
              maxSizeMB={100}
              allowedFileTypes={[
                ".txt", 
                ".pdbqt",
                "application/octet-stream",
                "text/plain"
              ]}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default UploadPage;
