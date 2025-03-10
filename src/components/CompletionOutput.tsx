import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Button } from "./ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "./ui/tooltip";
import { Copy, Download, RefreshCw } from "lucide-react";

interface CompletionOutputProps {
  completedCode?: string;
  originalCode?: string;
  selectedStyle?: "minimal" | "verbose" | "commented";
  onCopy?: () => void;
  onDownload?: () => void;
  onRefresh?: () => void;
}

const CompletionOutput = ({
  completedCode = `// Example completed code\nfunction calculateTotal(items) {\n  return items.reduce((total, item) => {\n    return total + (item.price * item.quantity);\n  }, 0);\n}\n\n// Usage example\nconst cart = [\n  { name: 'Product 1', price: 10, quantity: 2 },\n  { name: 'Product 2', price: 15, quantity: 1 }\n];\n\nconst total = calculateTotal(cart);\nconsole.log("Total: $" + total);`,
  originalCode = `// Incomplete code\nfunction calculateTotal(items) {\n  // TODO: Implement calculation\n}\n\n// Usage example\nconst cart = [\n  { name: 'Product 1', price: 10, quantity: 2 },\n  { name: 'Product 2', price: 15, quantity: 1 }\n];`,
  selectedStyle = "minimal",
  onCopy = () => console.log("Code copied"),
  onDownload = () => console.log("Code downloaded"),
  onRefresh = () => console.log("Refresh requested"),
}: CompletionOutputProps) => {
  const [activeTab, setActiveTab] = useState<"completed" | "diff">("completed");

  // Function to highlight the differences between original and completed code
  const renderDiffView = () => {
    // This is a simplified diff view - in a real implementation, you would use a proper diff library
    const lines = completedCode.split("\n");

    return (
      <pre className="p-4 bg-gray-900 text-gray-200 rounded-md overflow-auto text-sm">
        {lines.map((line, index) => {
          const isNewLine = !originalCode.includes(line);
          return (
            <div
              key={index}
              className={`${isNewLine ? "bg-green-900 text-green-300" : ""} py-1`}
            >
              {isNewLine ? "+ " : "  "}
              {line}
            </div>
          );
        })}
      </pre>
    );
  };

  return (
    <Card className="w-full h-full bg-gray-950 text-white border-gray-700">
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xl font-bold">Completion Output</CardTitle>
        <div className="flex items-center space-x-2">
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" onClick={onCopy}>
                  <Copy className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Copy to clipboard</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" onClick={onDownload}>
                  <Download className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Download code</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>

          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="outline" size="icon" onClick={onRefresh}>
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>Regenerate completion</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
      </CardHeader>

      <CardContent>
        <Tabs defaultValue="completed" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger
              value="completed"
              onClick={() => setActiveTab("completed")}
            >
              Completed Code
            </TabsTrigger>
            <TabsTrigger value="diff" onClick={() => setActiveTab("diff")}>
              Diff View
            </TabsTrigger>
          </TabsList>

          <TabsContent value="completed" className="mt-0">
            <div className="relative">
              <div className="absolute top-2 right-2 bg-gray-800 text-gray-200 text-xs px-2 py-1 rounded-md">
                Style: {selectedStyle}
              </div>
              <pre className="p-4 bg-gray-900 text-gray-200 rounded-md overflow-auto text-sm h-[320px]">
                {completedCode}
              </pre>
            </div>
          </TabsContent>

          <TabsContent value="diff" className="mt-0">
            <div className="h-[320px]">{renderDiffView()}</div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default CompletionOutput;
