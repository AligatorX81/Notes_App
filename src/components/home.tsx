import React, { useState } from "react";
import CodeEditor from "./CodeEditor";
import AnalysisPanel from "./AnalysisPanel";
import CompletionOutput from "./CompletionOutput";
import StyleSelector from "./StyleSelector";
import ActionButtons from "./ActionButtons";
import Notification from "./Notification";

const Home = () => {
  const [code, setCode] = useState<string>(
    "<!-- Enter your HTML/JS code here -->\n<div>\n  \n</div>\n\n<script>\n  // Your JavaScript code\n  \n</script>",
  );
  const [completedCode, setCompletedCode] = useState<string>("");
  const [selectedStyle, setSelectedStyle] = useState<string>("minimal");
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [notification, setNotification] = useState<{
    visible: boolean;
    type: "success" | "error" | "info";
    title: string;
    message: string;
  }>({ visible: false, type: "info", title: "", message: "" });

  const [analysis, setAnalysis] = useState({
    codeType: "HTML/JavaScript",
    structure: {
      elements: 1,
      functions: 0,
      variables: 0,
    },
    insights: ["Incomplete HTML structure", "Empty JavaScript section"],
    completionSuggestions: [
      "Add content to div element",
      "Implement JavaScript functionality",
    ],
  });

  const handleCodeChange = (newCode: string) => {
    setCode(newCode);
    // In a real implementation, this would trigger analysis of the code
  };

  const handleStyleChange = (style: string) => {
    setSelectedStyle(style);
    // In a real implementation, this would regenerate the completion with the new style
  };

  const handleComplete = () => {
    setIsProcessing(true);

    // Simulate API call with timeout
    setTimeout(() => {
      // Example completed code based on style
      let result = "";

      if (selectedStyle === "minimal") {
        result = `<div class="container">\n  <h1>Hello World</h1>\n  <p>This is a completed example.</p>\n</div>\n\n<script>\n  document.addEventListener('DOMContentLoaded', () => {\n    console.log('Page loaded');\n  });\n</script>`;
      } else if (selectedStyle === "verbose") {
        result = `<div class="container">\n  <h1>Hello World</h1>\n  <p>This is a completed example with more details.</p>\n  <button id="actionButton">Click Me</button>\n</div>\n\n<script>\n  document.addEventListener('DOMContentLoaded', () => {\n    console.log('Page loaded');\n    \n    const button = document.getElementById('actionButton');\n    button.addEventListener('click', () => {\n      alert('Button clicked!');\n    });\n  });\n</script>`;
      } else {
        result = `<!-- Main container with styling -->\n<div class="container">\n  <!-- Page heading -->\n  <h1>Hello World</h1>\n  <!-- Paragraph with description -->\n  <p>This is a completed example with comments.</p>\n</div>\n\n<script>\n  // Wait for DOM to be fully loaded before executing code\n  document.addEventListener('DOMContentLoaded', () => {\n    // Log message to console for debugging\n    console.log('Page loaded');\n  });\n</script>`;
      }

      setCompletedCode(result);
      setIsProcessing(false);

      // Show success notification
      setNotification({
        visible: true,
        type: "success",
        title: "Code Completed",
        message: "Your code has been successfully completed!",
      });

      // Update analysis
      setAnalysis({
        codeType: "HTML/JavaScript",
        structure: {
          elements: 3,
          functions: 1,
          variables: selectedStyle === "verbose" ? 1 : 0,
        },
        insights: ["Complete HTML structure", "Event listener implemented"],
        completionSuggestions: [
          "Add CSS styling",
          "Implement additional functionality",
        ],
      });
    }, 1500);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(completedCode);
    setNotification({
      visible: true,
      type: "success",
      title: "Copied!",
      message: "Code copied to clipboard",
    });
  };

  const handleDownload = () => {
    const blob = new Blob([completedCode], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "completed-code.html";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    setNotification({
      visible: true,
      type: "info",
      title: "Downloaded",
      message: "Code downloaded as completed-code.html",
    });
  };

  const handleReset = () => {
    setCode(
      "<!-- Enter your HTML/JS code here -->\n<div>\n  \n</div>\n\n<script>\n  // Your JavaScript code\n  \n</script>",
    );
    setCompletedCode("");
    setSelectedStyle("minimal");
    setAnalysis({
      codeType: "HTML/JavaScript",
      structure: {
        elements: 1,
        functions: 0,
        variables: 0,
      },
      insights: ["Incomplete HTML structure", "Empty JavaScript section"],
      completionSuggestions: [
        "Add content to div element",
        "Implement JavaScript functionality",
      ],
    });

    setNotification({
      visible: true,
      type: "info",
      title: "Reset",
      message: "Editor and results have been reset",
    });
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-white">
            HTML/JS Code Completion Tool
          </h1>
          <p className="text-gray-300 mt-2">
            Enter incomplete HTML and JavaScript code, and let our tool
            intelligently complete it based on context.
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <CodeEditor
              initialCode={code}
              onCodeChange={handleCodeChange}
              onRunCode={handleComplete}
            />
          </div>

          <div className="space-y-6">
            <AnalysisPanel analysis={analysis} isLoading={isProcessing} />

            <StyleSelector
              selectedStyle={selectedStyle}
              onStyleChange={handleStyleChange}
            />

            <ActionButtons
              onComplete={handleComplete}
              onCopy={handleCopy}
              onDownload={handleDownload}
              onReset={handleReset}
              isProcessing={isProcessing}
            />
          </div>
        </div>

        {completedCode && (
          <div className="mt-8">
            <CompletionOutput
              completedCode={completedCode}
              originalCode={code}
              selectedStyle={selectedStyle}
              onCopy={handleCopy}
              onDownload={handleDownload}
              onRefresh={handleComplete}
            />
          </div>
        )}
      </div>

      {notification.visible && (
        <Notification
          type={notification.type}
          title={notification.title}
          message={notification.message}
          visible={notification.visible}
          onClose={() => setNotification({ ...notification, visible: false })}
        />
      )}
    </div>
  );
};

export default Home;
