import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Boxes, FileText, X } from "lucide-react";
import React, { useRef, useState } from "react";
import { toast } from "sonner";
import UploadAnimation from "./UploadAnimation";

interface FileUploaderProps {
  maxSizeMB?: number;
  allowedFileTypes?: string[];
}

const FileUploader: React.FC<FileUploaderProps> = ({
  maxSizeMB = 10,
  allowedFileTypes = [".pdb", "chemical/x-pdb", "application/octet-stream"],
}) => {
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [file, setFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadStatus, setUploadStatus] = useState<
    "idle" | "uploading" | "success" | "error"
  >("idle");
  const inputRef = useRef<HTMLInputElement>(null);

  // Convert maxSizeMB to bytes for comparison
  const maxSizeBytes = maxSizeMB * 1024 * 1024;

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateFile = (file: File): boolean => {
    // Check file size
    if (file.size > maxSizeBytes) {
      toast.error(`File too large. Maximum size is ${maxSizeMB}MB.`);
      return false;
    }

    // Check if it's a PDB file (by extension or MIME type)
    const fileType = file.type;
    const fileName = file.name;
    const fileExtension = `.${fileName.split(".").pop()?.toLowerCase()}`;

    if (
      !fileExtension.includes(".pdb") &&
      !allowedFileTypes.includes(fileType)
    ) {
      toast.error(
        "Only .pdb file is supported for molecular docking analysis."
      );
      return false;
    }

    return true;
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
      }
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();

    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      }
    }
  };

  const removeFile = () => {
    setFile(null);
  };

  const handleUpload = () => {
    if (!file) {
      toast.error("Please select a PDB file to upload.");
      return;
    }

    setUploadStatus("uploading");

    // Simulate upload progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += 5;
      setUploadProgress(progress);

      if (progress >= 100) {
        clearInterval(interval);
        setUploadStatus("success");
        toast.success("File processed successfully! Generating reports...");
      }
    }, 200);
  };

  const openFileSelector = () => {
    if (inputRef.current) {
      inputRef.current.click();
    }
  };

  const resetUpload = () => {
    setFile(null);
    setUploadProgress(0);
    setUploadStatus("idle");
  };

  // Format bytes to a human-readable format
  const formatBytes = (bytes: number, decimals = 2) => {
    if (bytes === 0) return "0 Bytes";

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  };

  // Truncate filename if too long
  const truncateFilename = (filename: string, maxLength = 25) => {
    if (filename.length <= maxLength) return filename;

    const extension = filename.split(".").pop();
    const name = filename.substring(0, filename.lastIndexOf("."));

    return `${name.substring(
      0,
      maxLength - extension!.length - 4
    )}...${extension}`;
  };

  return (
    <div className="w-full">
      {uploadStatus === "idle" || uploadStatus === "uploading" ? (
        <>
          {/* File drop area - only show when no file is selected */}
          {!file && (
            <div
              className={`relative h-64 w-full rounded-lg border-2 border-dashed transition-colors duration-300 ease-in-out
              ${dragActive ? "border-blue-500 bg-blue-500/5" : "border-gray-300"}
              bg-transparent
              flex flex-col items-center justify-center p-6 mb-4`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                ref={inputRef}
                type="file"
                onChange={handleChange}
                className="hidden"
                accept=".pdb"
              />

              <div className="flex flex-col items-center justify-center space-y-4 pointer-events-none">
                <div className="text-blue-600 rounded-full p-4 bg-blue-500/5">
                  <Boxes size={36} strokeWidth={1.5} />
                </div>
                <div className="text-center">
                  <p className="text-lg font-medium text-gray-700">
                    Drag & drop file here
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    or click to browse your device
                  </p>
                  <p className="text-xs text-gray-400 mt-2">
                    Supported format: .pdb (Protein Data Bank files)
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    Max size: {maxSizeMB}MB
                  </p>
                </div>
              </div>

              {/* Clickable overlay */}
              <button
                className="absolute inset-0 w-full h-full cursor-pointer focus:outline-none"
                onClick={openFileSelector}
                type="button"
                aria-label="Select files"
              />
            </div>
          )}

          {/* Display selected file */}
          {file && (
            <div className="mb-6">
              <h3 className="text-sm font-medium text-gray-700 mb-3">
                Selected File
              </h3>

              <div className="flex items-center justify-between bg-white p-3 rounded-lg border border-gray-200 shadow-soft group hover:border-gray-300 transition-all duration-200">
                <div className="flex items-center space-x-3">
                  <div className="text-blue-600">
                    <FileText size={24} strokeWidth={1.5} />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      {truncateFilename(file.name)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatBytes(file.size)}
                    </p>
                  </div>
                </div>

                <button
                  onClick={removeFile}
                  className="text-gray-400 hover:text-red-500 transition-colors hover:cursor-pointer"
                  aria-label="Remove file"
                >
                  <X size={18} />
                </button>
              </div>
            </div>
          )}

          {/* Upload button and progress */}
          {uploadStatus === "uploading" ? (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-1">
                <p className="text-sm font-medium text-gray-700">
                  Processing your file...
                </p>
                <p className="text-sm text-gray-500">{uploadProgress}%</p>
              </div>
              <Progress value={uploadProgress} className="h-2 bg-gray-100">
                <div
                  className="h-full bg-blue-600 rounded-full"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </Progress>
            </div>
          ) : (
            file && (
              <Button
                onClick={handleUpload}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              >
                Process file
              </Button>
            )
          )}
        </>
      ) : (
        <div className="flex flex-col items-center justify-center space-y-6 py-10">
          <UploadAnimation status={uploadStatus} />

          <div className="text-center">
            <h3 className="text-2xl font-medium text-gray-800 mb-2">
              {uploadStatus === "success"
                ? "Analysis Complete!"
                : "Processing Failed"}
            </h3>
            <p className="text-gray-500 mb-6">
              {uploadStatus === "success"
                ? "Your PDB file has been processed successfully. Reports are being generated."
                : "There was an error processing your PDB file. Please try again."}
            </p>

            <div className="space-y-3">
              {uploadStatus === "success" && (
                <Button className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white mb-3">
                  View Analysis Reports
                </Button>
              )}

              <Button
                onClick={resetUpload}
                variant={uploadStatus === "success" ? "outline" : "default"}
                className={
                  uploadStatus === "success"
                    ? "w-full sm:w-auto border-gray-300"
                    : "w-full sm:w-auto"
                }
              >
                {uploadStatus === "success" ? "Upload Another File" : "Try Again"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
