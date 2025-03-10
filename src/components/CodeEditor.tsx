import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "../components/ui/tabs";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../components/ui/tooltip";
import { Copy, Play, RotateCcw } from "lucide-react";

interface CodeEditorProps {
  initialCode?: string;
  language?: "html" | "javascript" | "css";
  onCodeChange?: (code: string) => void;
  onRunCode?: () => void;
}

const CodeEditor = ({
  initialCode = "<!-- Enter your HTML/JS code here -->\n<div>\n  \n</div>\n\n<script>\n  // Your JavaScript code\n  \n</script>",
  language = "html",
  onCodeChange = () => {},
  onRunCode = () => {},
}: CodeEditorProps) => {
  const [code, setCode] = useState(initialCode);
  const [activeTab, setActiveTab] = useState<string>(language);

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newCode = e.target.value;
    setCode(newCode);
    onCodeChange(newCode);
  };

  const handleCopyCode = () => {
    navigator.clipboard.writeText(code);
    // In a real implementation, this would trigger a notification
  };

  const handleResetCode = () => {
    setCode(initialCode);
    onCodeChange(initialCode);
  };

  return (
    <Card className="w-full h-full bg-gray-950 text-white shadow-md border-gray-700">
      <CardHeader className="pb-2">
        <div className="flex justify-between items-center">
          <CardTitle className="text-lg font-medium">Code Editor</CardTitle>
          <div className="flex space-x-2">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopyCode}
                    className="h-8 w-8 p-0"
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Copy code</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleResetCode}
                    className="h-8 w-8 p-0"
                  >
                    <RotateCcw className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Reset code</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="default"
                    size="sm"
                    onClick={onRunCode}
                    className="h-8 w-8 p-0"
                  >
                    <Play className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Run completion</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>

        <Tabs
          defaultValue={activeTab}
          onValueChange={setActiveTab}
          className="w-full"
        >
          <TabsList className="grid grid-cols-3 w-60">
            <TabsTrigger value="html">HTML</TabsTrigger>
            <TabsTrigger value="javascript">JavaScript</TabsTrigger>
            <TabsTrigger value="css">CSS</TabsTrigger>
          </TabsList>
        </Tabs>
      </CardHeader>

      <CardContent>
        <div className="relative w-full h-[350px] border border-gray-700 rounded-md overflow-hidden bg-gray-900">
          <textarea
            value={code}
            onChange={handleCodeChange}
            className="w-full h-full p-4 font-mono text-sm text-gray-200 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-900"
            placeholder="Enter your code here..."
            spellCheck="false"
          />
          <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
            {/* This would be where syntax highlighting would be implemented */}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default CodeEditor;
