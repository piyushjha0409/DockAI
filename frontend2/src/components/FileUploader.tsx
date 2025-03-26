import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { AlertCircle, Check, Database, FileDown, Key, Upload, X } from "lucide-react";
import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { toast } from "sonner";
import MoleculeViewer from "./MoleculeViewer";

interface FileUploaderProps {
  maxSizeMB: number;
  allowedFileTypes: string[];
}

const FileUploader: React.FC<FileUploaderProps> = ({
  maxSizeMB,
  allowedFileTypes,
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [cid, setCid] = useState("");
  const [solanaSignature, setSolanaSignature] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);
  const [visualizationData, setVisualizationData] = useState(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [activeModel, setActiveModel] = useState(0);
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  const containerRef = React.useRef<HTMLDivElement>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      // Check if we already have 2 files
      if (files.length + acceptedFiles.length > 2) {
        toast.error("Too many files", {
          description:
            "Please upload exactly one .txt file and one .pdbqt file.",
        });
        return;
      }

      // Validate file types
      const invalidFiles = acceptedFiles.filter(
        (file) =>
          !allowedFileTypes.some((type) =>
            file.name.toLowerCase().endsWith(type)
          )
      );

      if (invalidFiles.length > 0) {
        toast.error("Invalid file type", {
          description: "Please upload only .txt and .pdbqt files.",
        });
        return;
      }

      // Check file sizes
      const oversizedFiles = acceptedFiles.filter(
        (file) => file.size > maxSizeBytes
      );
      if (oversizedFiles.length > 0) {
        toast.error("File too large", {
          description: `Maximum file size is ${maxSizeMB}MB.`,
        });
        return;
      }

      // Combine existing and new files
      const updatedFiles = [...files, ...acceptedFiles];

      // If we already have a txt file and trying to add another txt file
      const txtFiles = updatedFiles.filter((file) =>
        file.name.toLowerCase().endsWith(".txt")
      );
      const pdbqtFiles = updatedFiles.filter((file) =>
        file.name.toLowerCase().endsWith(".pdbqt")
      );

      if (txtFiles.length > 1) {
        toast.error("Duplicate file type", {
          description: "You can only upload one .txt file.",
        });
        return;
      }

      if (pdbqtFiles.length > 1) {
        toast.error("Duplicate file type", {
          description: "You can only upload one .pdbqt file.",
        });
        return;
      }

      setFiles(updatedFiles);
    },
    [files, allowedFileTypes, maxSizeBytes, maxSizeMB]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "text/plain": [".txt"],
      "application/octet-stream": [".pdbqt"],
    },
    maxSize: maxSizeBytes,
  });

  const removeFile = (index: number) => {
    const newFiles = [...files];
    newFiles.splice(index, 1);
    setFiles(newFiles);

    // Clear results if files are removed
    if (newFiles.length === 0) {
      setVisualizationData(null);
      setPdfUrl(null);
    }
  };

  const handleUpload = async () => {
    // Validate that we have exactly one .txt and one .pdbqt file before uploading
    const txtFile = files.find((file) =>
      file.name.toLowerCase().endsWith(".txt")
    );
    const pdbqtFile = files.find((file) =>
      file.name.toLowerCase().endsWith(".pdbqt")
    );

    if (!txtFile || !pdbqtFile) {
      toast.error("Missing required files", {
        description: "Please upload exactly one .txt file and one .pdbqt file.",
      });
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setVisualizationData(null);
    setPdfUrl(null);

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress((prev) => {
        if (prev >= 95) {
          clearInterval(interval);
          return prev;
        }
        return prev + 5;
      });
    }, 300);

    try {
      // Prepare form data
      const formData = new FormData();
      formData.append("result_file", txtFile);
      formData.append("pdbqt_file", pdbqtFile);

      // Send to combined endpoint
      const response = await fetch(
        "http://127.0.0.1:8000/process-docking-data",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }

      const data = await response.json();

      clearInterval(interval);
      setUploadProgress(100);

      if (data.cid) setCid(data.cid);
      if (data.solana_signature) setSolanaSignature(data.solana_signature);

      // Process PDF report
      if (data.pdf_report_base64) {
        const pdfData = new Uint8Array(
          data.pdf_report_base64
            .match(/.{1,2}/g)
            .map((byte: string) => parseInt(byte, 16))
        );
        const blob = new Blob([pdfData], { type: "application/pdf" });
        const url = URL.createObjectURL(blob);
        setPdfUrl(url);
      }

      // Process visualization data
      if (data.visualization_data) {
        setVisualizationData(data.visualization_data);
      }

      toast.success("Processing complete", {
        description: "Your docking results have been processed successfully.",
      });

      // Stay on the same page to display results
      setUploading(false);
    } catch (error) {
      console.error("Upload error:", error);
      clearInterval(interval);
      setUploading(false);

      toast.error("Processing failed", {
        description:
          "There was an error processing your files. Please try again.",
      });
    }
  };

  const getFileTypeEmoji = (fileName: string) => {
    if (fileName.toLowerCase().endsWith(".txt")) return "📄";
    if (fileName.toLowerCase().endsWith(".pdbqt")) return "🧬";
    return "📁";
  };

  const getUploadStatus = () => {
    const hasTxt = files.some((file) =>
      file.name.toLowerCase().endsWith(".txt")
    );
    const hasPdbqt = files.some((file) =>
      file.name.toLowerCase().endsWith(".pdbqt")
    );

    return (
      <div className="mt-4 mb-2">
        <p className="font-medium text-sm mb-2">Required files:</p>
        <div className="flex flex-col gap-2">
          <div className="flex items-center">
            {hasTxt ? (
              <Check size={16} className="text-green-500 mr-2" />
            ) : (
              <AlertCircle size={16} className="text-amber-500 mr-2" />
            )}
            <span
              className={`text-sm ${
                hasTxt ? "text-green-600" : "text-amber-600"
              }`}
            >
              .txt output file {hasTxt ? "(Added)" : "(Required)"}
            </span>
          </div>
          <div className="flex items-center">
            {hasPdbqt ? (
              <Check size={16} className="text-green-500 mr-2" />
            ) : (
              <AlertCircle size={16} className="text-amber-500 mr-2" />
            )}
            <span
              className={`text-sm ${
                hasPdbqt ? "text-green-600" : "text-amber-600"
              }`}
            >
              .pdbqt file {hasPdbqt ? "(Added)" : "(Required)"}
            </span>
          </div>
        </div>
      </div>
    );
  };

  // Results display section
  const renderResults = () => {
    if (!visualizationData && !pdfUrl) return null;

    return (
      <div className="mt-8 space-y-6 bg-white rounded-lg  p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Analysis Results</h2>
        
        {/* Verification and Report section */}
        <div className="flex flex-col lg:flex-row gap-6 mb-6">
          {/* Blockchain verification info */}
          {(cid || solanaSignature) && (
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-100 flex-1">
              <h3 className="text-lg font-medium text-blue-900 mb-2">Blockchain Verification</h3>
              <div className="space-y-2">
                {cid && (
                  <div className="flex items-start">
                    <Database className="h-5 w-5 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-blue-800">IPFS Content ID</p>
                      <p className="text-xs text-blue-700 font-mono break-all">{cid}</p>
                    </div>
                  </div>
                )}
                {solanaSignature && (
                  <div className="flex items-start">
                    <Key className="h-5 w-5 text-blue-500 mr-2 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-blue-800">Solana Signature</p>
                      <p className="text-xs text-blue-700 font-mono break-all">{solanaSignature}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Detailed Report section */}
          {pdfUrl && (
            <div className="bg-green-50 rounded-lg p-4 border border-green-100 flex-1">
              <h3 className="text-lg font-medium text-green-900 mb-2">Detailed Report</h3>
              <p className="text-sm text-green-800 mb-3">Download or view the complete analysis report with detailed metrics.</p>
              <div className="flex flex-wrap gap-2">
                <a
                  href={pdfUrl}
                  download="docking_report.pdf"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  <FileDown className="mr-2 h-4 w-4" />
                  Download PDF Report
                </a>
                <a
                  href={pdfUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  View Report
                </a>
              </div>
            </div>
          )}
        </div>
        
        {visualizationData && (
          <div className="space-y-4">
            <div ref={containerRef} style={{ width: "100%", minHeight: "500px" }}>
              <MoleculeViewer
                modelData={visualizationData}
                activeModel={activeModel}
                containerRef={containerRef}
              />
            </div>
          </div>
        )}

        <Button
          variant="outline"
          onClick={() => {
            setFiles([]);
            setVisualizationData(null);
            setPdfUrl(null);
            setCid("");
            setSolanaSignature("");
          }}
          className="mt-6"
        >
          Process Another Docking Result
        </Button>
      </div>
    );
  };

  return (
    <div className="w-full">
      {!uploading ? (
        <>
          {!visualizationData && !pdfUrl ? (
            <>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 cursor-pointer transition-colors duration-200 ${
                  isDragActive
                    ? "border-blue-400 bg-blue-50"
                    : "border-gray-300 hover:border-blue-300 hover:bg-blue-50/50"
                }`}
              >
                <input {...getInputProps()} />
                <div className="flex flex-col items-center justify-center text-center">
                  <Upload
                    className={`mb-3 ${
                      isDragActive ? "text-blue-500" : "text-gray-400"
                    }`}
                    size={30}
                  />
                  <p className="text-sm font-medium text-gray-700 mb-1">
                    {isDragActive
                      ? "Drop the files here..."
                      : "Drag & drop files here, or click to select"}
                  </p>
                  <p className="text-xs text-gray-500 mb-2">
                    Please upload one .txt file and one .pdbqt file (max{" "}
                    {maxSizeMB}
                    MB each)
                  </p>
                </div>
              </div>

              {getUploadStatus()}

              {files.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">
                    Selected files:
                  </p>
                  <div className="space-y-2">
                    {files.map((file, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between bg-gray-50 p-3 rounded-md"
                      >
                        <div className="flex items-center">
                          <div className="flex-shrink-0 mr-3 text-lg">
                            {getFileTypeEmoji(file.name)}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-700 truncate max-w-[200px]">
                              {file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {(file.size / 1024 / 1024).toFixed(2)} MB
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFile(index)}
                          className="text-gray-400 hover:text-red-500 transition-colors"
                          aria-label="Remove file"
                        >
                          <X size={18} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-6">
                <Button
                  className="w-full"
                  size="lg"
                  onClick={handleUpload}
                  disabled={files.length !== 2}
                >
                  {files.length === 2
                    ? "Process Files"
                    : "Select Required Files"}
                </Button>
              </div>
            </>
          ) : (
            renderResults()
          )}
        </>
      ) : (
        <div className="space-y-4">
          <p className="text-center font-medium text-gray-700">
            Processing files...
          </p>
          <Progress value={uploadProgress} className="h-2" />
          <p className="text-center text-sm text-gray-500">
            {uploadProgress < 100
              ? `Analyzing docking results... ${uploadProgress}%`
              : "Processing complete!"}
          </p>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
