import React from "react";
import { Button } from "./ui/button";
import { Loader2 } from "lucide-react";

interface ActionButtonsProps {
  onComplete?: () => void;
  onCopy?: () => void;
  onDownload?: () => void;
  onReset?: () => void;
  isProcessing?: boolean;
}

const ActionButtons = ({
  onComplete = () => {},
  onCopy = () => {},
  onDownload = () => {},
  onReset = () => {},
  isProcessing = false,
}: ActionButtonsProps) => {
  return (
    <div className="flex flex-col gap-4 w-full bg-gray-950 text-white p-4 rounded-md border border-gray-700 shadow-sm">
      <Button
        onClick={onComplete}
        disabled={isProcessing}
        className="w-full bg-blue-600 hover:bg-blue-700"
      >
        {isProcessing ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Processing...
          </>
        ) : (
          "Complete Code"
        )}
      </Button>

      <div className="grid grid-cols-3 gap-2">
        <Button
          onClick={onCopy}
          variant="outline"
          disabled={isProcessing}
          className="w-full"
        >
          Copy
        </Button>
        <Button
          onClick={onDownload}
          variant="outline"
          disabled={isProcessing}
          className="w-full"
        >
          Download
        </Button>
        <Button
          onClick={onReset}
          variant="outline"
          disabled={isProcessing}
          className="w-full"
        >
          Reset
        </Button>
      </div>
    </div>
  );
};

export default ActionButtons;
