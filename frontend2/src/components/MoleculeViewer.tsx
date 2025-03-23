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

  const handleModelChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setActiveModel(parseInt(event.target.value));
  };

  if (!modelData) {
    return <div className="p-4 text-center">No model data available</div>;
  }

  return (
    <div className="molecule-viewer bg-white rounded-lg shadow-md p-6">
      <div className="viewer-controls mb-4">
        <h3 className="text-xl font-semibold mb-2">
          Binding Affinity: {modelData.models[activeModel]?.binding_affinity}{" "}
          kcal/mol
        </h3>
        <div className="flex items-center">
          <label className="flex items-center mr-4">
            <span className="mr-2">Select Model:</span>
            <select
              value={activeModel}
              onChange={handleModelChange}
              className="border border-gray-300 rounded px-2 py-1"
            >
              {modelData.models.map((model, index) => (
                <option key={model.model_id} value={index}>
                  Model {model.model_id} ({model.binding_affinity} kcal/mol)
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      <div
        ref={containerRef}
        className="molecule-container border border-gray-200 rounded relative"
        style={{ 
          width: "100%", 
          height: "400px", 
          position: "relative", 
          overflow: "hidden" 
        }}
      >
        <Mol3DViewer
          modelData={modelData}
          activeModel={activeModel}
          containerRef={containerRef}
        />
      </div>

      <div className="binding-info mt-4 p-4 bg-gray-50 rounded">
        <h4 className="text-lg font-medium mb-2">Summary</h4>
        <p>
          Best binding energy: {modelData.summary.best_binding_affinity}{" "}
          kcal/mol
        </p>
        <p>Number of models: {modelData.summary.model_count}</p>
      </div>
    </div>
  );
};

export default MoleculeViewer;
