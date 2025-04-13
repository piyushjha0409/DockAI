"use client";

import React, { useEffect, useRef, useState } from "react";

// Add declaration for 3dmol module
interface SphereOptions {
  center: { x: number; y: number; z: number };
  radius: number;
  color: string;
}

interface CylinderOptions {
  start: { x: number; y: number; z: number };
  end: { x: number; y: number; z: number };
  radius: number;
  color: string;
}

interface Viewer3D {
  addSphere: (options: SphereOptions) => void;
  addCylinder: (options: CylinderOptions) => void;
  zoomTo: () => void;
  render: () => void;
  clear: () => void;
}

// Define interfaces for our data model
interface Atom {
  id: number;
  element: string;
  x: number;
  y: number;
  z: number;
}

interface Bond {
  atom1: number;
  atom2: number;
}

interface Model {
  model_id: number;
  binding_affinity: number;
  atoms: Atom[];
  bonds: Bond[];
}

interface ModelData {
  models: Model[];
  summary: {
    best_binding_affinity: number;
    model_count: number;
  };
}

interface Mol3DViewerProps {
  modelData: ModelData;
  activeModel: number;
  containerRef: React.RefObject<HTMLDivElement | null>;
}

// Dynamically import 3Dmol.js to avoid SSR issues
const Mol3DViewer: React.FC<Mol3DViewerProps> = ({
  modelData,
  activeModel,
  containerRef,
}) => {
  // This component will load 3Dmol only on the client side
  useEffect(() => {
    let viewer: Viewer3D | null = null;
    let $3Dmol: {
      createViewer: (
        element: HTMLElement,
        options: { backgroundColor: string; antialias: boolean }
      ) => Viewer3D;
    } | null = null;

    // Dynamically import 3Dmol when the component mounts
    import("3dmol").then((mol) => {
      $3Dmol = mol.default || mol;

      if (!modelData || !containerRef.current || !$3Dmol) return;

      // Make sure any existing 3Dmol canvases are removed before creating a new one
      const existingCanvases = containerRef.current.querySelectorAll('canvas');
      existingCanvases.forEach(canvas => canvas.remove());

      // Initialize the 3Dmol viewer with explicit container positioning
      viewer = $3Dmol.createViewer(containerRef.current, {
        backgroundColor: "white",
        antialias: true,
      });

      // Ensure the viewer canvas has proper positioning
      if (containerRef.current.querySelector('canvas')) {
        const canvas = containerRef.current.querySelector('canvas');
        if (canvas) {
          canvas.style.position = 'relative';
          canvas.style.width = '100%';
          canvas.style.height = '100%';
        }
      }

      const currentModel = modelData.models[activeModel];

      // Add atoms to the viewer
      currentModel.atoms.forEach((atom: Atom) => {
        if (viewer) {
          viewer.addSphere({
            center: { x: atom.x, y: atom.y, z: atom.z },
            radius: 0.5, // Radius in Angstroms
            color: getElementColor(atom.element),
          });
        }
      });
      // Add bonds to the viewer
      currentModel.bonds.forEach((bond: Bond) => {
        const atom1 = currentModel.atoms.find((a) => a.id === bond.atom1);
        const atom2 = currentModel.atoms.find((a) => a.id === bond.atom2);

        if (atom1 && atom2 && viewer) {
          viewer.addCylinder({
            start: { x: atom1.x, y: atom1.y, z: atom1.z },
            end: { x: atom2.x, y: atom2.y, z: atom2.z },
            radius: 0.2,
            color: "gray",
          });
        }
      });

      // Zoom to fit the model
      if (viewer) {
        viewer.zoomTo();
        viewer.render();
      }
    });

    // Clean up on unmount
    return () => {
      if (viewer) {
        viewer.clear();
      }
    };
  }, [modelData, activeModel, containerRef]);

  return null; // This component doesn't render anything itself
};

const getElementColor = (element: string): string => {
  // Basic element color mapping
  const colors: Record<string, string> = {
    C: "gray",
    N: "blue",
    O: "red",
    H: "white",
    S: "yellow",
    P: "orange",
    // Add more elements as needed
  };

  return colors[element] || "pink";
};

const MoleculeViewer: React.FC<Mol3DViewerProps> = ({ modelData }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [activeModel, setActiveModel] = useState<number>(0);
  const [showGrid, setShowGrid] = useState<boolean>(false);
  // Create an array of refs for each model container in grid view
  const modelRefsArray = useRef<(HTMLDivElement | null)[]>([]);

  // Initialize the refs array when models change
  useEffect(() => {
    if (modelData && modelData.models) {
      modelRefsArray.current = Array(modelData.models.length).fill(null);
    }
  }, [modelData]);

  // Calculate the binding energy range
  const minEnergy = Math.min(...modelData.models.map(m => m.binding_affinity));
  const maxEnergy = Math.max(...modelData.models.map(m => m.binding_affinity));
  
  // Function to get color based on binding energy (green for best/lowest, red for worst/highest)
  const getEnergyColor = (energy: number) => {
    if (minEnergy === maxEnergy) return "#4ade80"; // Green if all same
    
    // Normalize between 0 and 1 (0 being the best/lowest energy, 1 being the worst/highest)
    const normalized = (energy - minEnergy) / (maxEnergy - minEnergy);
    
    // Interpolate between green (best) and amber (worst)
    const r = Math.round(normalized * 239 + (1 - normalized) * 74);
    const g = Math.round(normalized * 68 + (1 - normalized) * 222);
    const b = Math.round(normalized * 68 + (1 - normalized) * 128);
    
    return `rgb(${r}, ${g}, ${b})`;
  };

  const toggleView = () => {
    setShowGrid(!showGrid);
  };

  if (!modelData) {
    return <div className="p-4 text-center">No model data available</div>;
  }

  return (
    <div className="molecule-viewer bg-white rounded-lg">
      <div className="viewer-header mb-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-xl font-semibold">
            Molecular Docking Results
          </h3>
          <Button 
            onClick={toggleView} 
            variant="outline" 
            size="sm"
            className="text-xs px-2 py-1"
          >
            {showGrid ? "Single View" : "Grid View"}
          </Button>
        </div>
        
        <div className="mt-2 bg-blue-50 p-3 rounded-md">
          <p className="text-sm font-medium">
            Best binding energy: <span className="text-green-600 font-bold">{modelData.summary.best_binding_affinity} kcal/mol</span>
          </p>
          <p className="text-sm">
            Total models: {modelData.summary.model_count}
          </p>
        </div>
      </div>

      {showGrid ? (
        // Grid view - all models
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modelData.models.map((model, index) => (
            <div 
              key={model.model_id} 
              className="model-card border rounded-lg overflow-hidden hover:shadow-md transition-shadow"
              onClick={() => setActiveModel(index)}
            >
              <div 
                className="p-2 text-white font-medium text-sm" 
                style={{ backgroundColor: getEnergyColor(model.binding_affinity) }}
              >
                Model {model.model_id} | {model.binding_affinity} kcal/mol
              </div>
              <div
                className="molecule-container relative"
                style={{ height: "200px" }}
              >
                <div 
                  ref={el => { modelRefsArray.current[index] = el; }}
                  className="absolute inset-0"
                >
                  {/* Render all models in grid view, not just the active one */}
                  <Mol3DViewer
                    modelData={modelData}
                    activeModel={index}
                    containerRef={{ current: modelRefsArray.current[index] }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        // Single selected model view
        <div className="single-model-view">
          <div className="flex flex-wrap gap-2 mb-3">
            {modelData.models.map((model, index) => (
              <button
                key={model.model_id}
                className={`px-3 py-1 text-sm rounded-full transition-colors ${
                  activeModel === index
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 hover:bg-gray-300 text-gray-800"
                }`}
                onClick={() => setActiveModel(index)}
              >
                Model {model.model_id}
              </button>
            ))}
          </div>
          
          <div className="border border-gray-200 rounded-lg overflow-hidden">
            <div 
              className="p-2 text-white font-medium"
              style={{ backgroundColor: getEnergyColor(modelData.models[activeModel].binding_affinity) }}
            >
              Binding Energy: {modelData.models[activeModel].binding_affinity} kcal/mol
            </div>
            <div
              ref={containerRef}
              className="molecule-container relative"
              style={{ height: "400px" }}
            >
              <Mol3DViewer
                modelData={modelData}
                activeModel={activeModel}
                containerRef={containerRef}
              />
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-gray-50 rounded-lg text-sm">
            <p>Atoms: {modelData.models[activeModel].atoms.length}</p>
            <p>Bonds: {modelData.models[activeModel].bonds.length}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper component for Button since it was used but not imported
const Button: React.FC<{
  onClick?: () => void;
  variant?: 'default' | 'outline';
  size?: 'default' | 'sm';
  className?: string;
  children: React.ReactNode;
}> = ({ onClick, variant = 'default', size = 'default', className = '', children }) => {
  const baseClasses = "rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500";
  const variantClasses = variant === 'outline' 
    ? "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50" 
    : "bg-blue-600 text-white hover:bg-blue-700";
  const sizeClasses = size === 'sm' ? "px-3 py-1 text-sm" : "px-4 py-2";
  
  return (
    <button
      onClick={onClick}
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`}
    >
      {children}
    </button>
  );
};

export default MoleculeViewer;
