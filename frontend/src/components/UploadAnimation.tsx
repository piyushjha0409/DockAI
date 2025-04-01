import { Boxes, Check, X } from "lucide-react";
import React from "react";

interface UploadAnimationProps {
  status: "idle" | "uploading" | "success" | "error";
}

const UploadAnimation: React.FC<UploadAnimationProps> = ({ status }) => {
  return (
    <div className="relative h-32 w-32 flex items-center justify-center">
      {status === "idle" && (
        <div className="animate-float text-blue-600">
          <Boxes size={64} strokeWidth={1.5} />
        </div>
      )}

      {status === "uploading" && (
        <div className="relative">
          <div className="h-32 w-32 rounded-full border-4 border-gray-200 opacity-25"></div>
          <div className="absolute top-0 left-0 h-32 w-32 rounded-full border-4 border-t-blue-600 animate-spin"></div>
          <div className="absolute top-0 left-0 h-32 w-32 flex items-center justify-center">
            <Boxes
              size={40}
              strokeWidth={1.5}
              className="text-blue-600 animate-pulse"
            />
          </div>
        </div>
      )}

      {status === "success" && (
        <div className="h-32 w-32 rounded-full bg-green-50 flex items-center justify-center animate-slide-up">
          <Check size={64} strokeWidth={1.5} className="text-green-500" />
        </div>
      )}

      {status === "error" && (
        <div className="h-32 w-32 rounded-full bg-red-50 flex items-center justify-center animate-slide-up">
          <X size={64} strokeWidth={1.5} className="text-red-500" />
        </div>
      )}
    </div>
  );
};

export default UploadAnimation;
