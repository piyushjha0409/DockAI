"use client";

import FileUploader from "@/components/FileUploader";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowLeft, Boxes, FileText } from "lucide-react";
import Link from "next/link";
import { useEffect } from "react";

const UploadPage = () => {
  // Apply fade-in animation to the entire page
  useEffect(() => {
    document.title = "Upload PDB Files - MolecularViz";

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
      <div className="w-full max-w-3xl mx-auto">
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
            Upload your file
          </h1>
          <p className="text-gray-600 max-w-xl mx-auto">
            Upload your molecular docking file to generate comprehensive reports
            and visualizations. Our AI will analyze binding positions,
            interactions, and efficacy.
          </p>
        </div>

        <Card className="border-0 shadow-smooth overflow-hidden bg-white/80 backdrop-blur-sm">
          <CardContent className="p-6 sm:p-8">
            <FileUploader
              maxSizeMB={100}
              allowedFileTypes={[
                ".pdb",
                "chemical/x-pdb",
                "application/octet-stream",
              ]}
            />
          </CardContent>
        </Card>

        <div className="mt-8 text-center space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
            <div className="bg-blue-50 rounded-lg p-4 flex items-start space-x-3">
              <div className="text-blue-600 mt-1">
                <FileText size={20} />
              </div>
              <div>
                <h3 className="font-medium text-blue-800">Docking Reports</h3>
                <p className="text-sm text-blue-700/80">
                  Receive detailed analysis of binding scores, interactions, and
                  predicted efficacy
                </p>
              </div>
            </div>

            <div className="bg-blue-50 rounded-lg p-4 flex items-start space-x-3">
              <div className="text-blue-600 mt-1">
                <Boxes size={20} />
              </div>
              <div>
                <h3 className="font-medium text-blue-800">3D Visualizations</h3>
                <p className="text-sm text-blue-700/80">
                  Interactive 3D models of molecular interactions and binding
                  positions
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
