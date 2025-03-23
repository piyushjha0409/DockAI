"use client";

import React, { useRef, useState } from "react";
import MoleculeViewer from "../../components/MoleculeViewer";

export default function DockingVisualizer() {
  const [resultFile, setResultFile] = useState<File | null>(null);
  const [pdbqtFile, setPdbqtFile] = useState<File | null>(null);
  const [visualizationData, setVisualizationData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleResultFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setResultFile(e.target.files[0]);
    }
  };

  const handlePdbqtFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setPdbqtFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: { preventDefault: () => void }) => {
    e.preventDefault();

    if (!resultFile || !pdbqtFile) {
      setError("Please select both result and PDBQT files");
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append("result_file", resultFile);
    formData.append("pdbqt_file", pdbqtFile);

    try {
      const response = await fetch("http://127.0.0.1:8000/visualize-docking", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(
          `Server responded with ${response.status}: ${await response.text()}`
        );
      }

      const data = await response.json();
      setVisualizationData(data);
      setLoading(false);
    } catch (err: unknown) {
      console.error("Error visualizing docking:", err);
      setError(
        err instanceof Error
          ? err.message
          : "An error occurred during visualization"
      );
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">
        Molecular Docking Visualizer
      </h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                AutoDock Result File (.txt):
                <input
                  type="file"
                  accept=".txt"
                  onChange={handleResultFileChange}
                  required
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                PDBQT File:
                <input
                  type="file"
                  accept=".pdbqt"
                  onChange={handlePdbqtFileChange}
                  required
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </label>
            </div>
          </div>

          <div className="flex justify-center">
            <button
              type="submit"
              disabled={loading}
              className={`px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white 
                ${
                  loading
                    ? "bg-indigo-300"
                    : "bg-indigo-600 hover:bg-indigo-700"
                }
                focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
            >
              {loading ? "Processing..." : "Visualize Docking"}
            </button>
          </div>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
      {visualizationData && (
        <MoleculeViewer
          modelData={visualizationData}
          activeModel={0}
          containerRef={containerRef}
        />
      )}
    </div>
  );
}
