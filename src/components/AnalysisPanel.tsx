import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";
import { AlertCircle, Code, FileJson, Layers } from "lucide-react";

interface AnalysisPanelProps {
  analysis?: {
    codeType?: string;
    structure?: {
      elements: number;
      functions: number;
      variables: number;
    };
    insights?: string[];
    completionSuggestions?: string[];
  };
  isLoading?: boolean;
}

const AnalysisPanel = ({
  analysis = {
    codeType: "HTML/JavaScript",
    structure: {
      elements: 5,
      functions: 2,
      variables: 3,
    },
    insights: [
      "Missing closing tags for div elements",
      "Incomplete function implementation",
      "Undefined variable reference",
    ],
    completionSuggestions: [
      "Add closing tags",
      "Complete function body",
      "Define missing variables",
    ],
  },
  isLoading = false,
}: AnalysisPanelProps) => {
  return (
    <Card className="w-full h-full bg-gray-950 text-white overflow-auto border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <FileJson size={18} />
            Code Analysis
          </span>
          {analysis.codeType && (
            <Badge variant="secondary" className="text-xs">
              {analysis.codeType}
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center h-64 text-muted-foreground">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
            <p>Analyzing code context...</p>
          </div>
        ) : (
          <>
            <div className="space-y-2">
              <h3 className="text-sm font-medium flex items-center gap-2">
                <Layers size={16} />
                Structure Analysis
              </h3>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="bg-gray-800 p-2 rounded-md">
                  <p className="text-lg font-semibold">
                    {analysis.structure?.elements || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Elements</p>
                </div>
                <div className="bg-gray-800 p-2 rounded-md">
                  <p className="text-lg font-semibold">
                    {analysis.structure?.functions || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Functions</p>
                </div>
                <div className="bg-gray-800 p-2 rounded-md">
                  <p className="text-lg font-semibold">
                    {analysis.structure?.variables || 0}
                  </p>
                  <p className="text-xs text-muted-foreground">Variables</p>
                </div>
              </div>
            </div>

            <Separator />

            <div className="space-y-2">
              <h3 className="text-sm font-medium flex items-center gap-2">
                <AlertCircle size={16} />
                Key Insights
              </h3>
              <ul className="space-y-1 text-sm">
                {analysis.insights?.map((insight, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-muted-foreground">•</span>
                    <span>{insight}</span>
                  </li>
                )) || (
                  <p className="text-muted-foreground text-sm">
                    No insights available
                  </p>
                )}
              </ul>
            </div>

            <Separator />

            <div className="space-y-2">
              <h3 className="text-sm font-medium flex items-center gap-2">
                <Code size={16} />
                Completion Suggestions
              </h3>
              <ul className="space-y-1 text-sm">
                {analysis.completionSuggestions?.map((suggestion, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-muted-foreground">•</span>
                    <span>{suggestion}</span>
                  </li>
                )) || (
                  <p className="text-muted-foreground text-sm">
                    No suggestions available
                  </p>
                )}
              </ul>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default AnalysisPanel;
