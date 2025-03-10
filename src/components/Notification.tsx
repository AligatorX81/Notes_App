import React from "react";
import { useToast } from "@/components/ui/use-toast";
import { Toast, ToastTitle, ToastDescription } from "@/components/ui/toast";
import { CheckCircle, AlertCircle, Info, X } from "lucide-react";

type NotificationType = "success" | "error" | "info";

interface NotificationProps {
  type?: NotificationType;
  title?: string;
  message?: string;
  duration?: number;
  onClose?: () => void;
  visible?: boolean;
}

const Notification = ({
  type = "info",
  title = "Notification",
  message = "This is a notification message",
  duration = 5000,
  onClose = () => {},
  visible = true,
}: NotificationProps) => {
  const { toast } = useToast();
  const [isVisible, setIsVisible] = React.useState(visible);

  React.useEffect(() => {
    setIsVisible(visible);
  }, [visible]);

  React.useEffect(() => {
    if (isVisible) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [isVisible, duration, onClose]);

  const handleClose = () => {
    setIsVisible(false);
    onClose();
  };

  const showToast = () => {
    toast({
      title: title,
      description: message,
      variant: type === "error" ? "destructive" : "default",
    });
  };

  // Icon based on notification type
  const getIcon = () => {
    switch (type) {
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case "info":
      default:
        return <Info className="h-5 w-5 text-blue-500" />;
    }
  };

  // Background color based on notification type
  const getBgColor = () => {
    switch (type) {
      case "success":
        return "bg-green-50 border-green-200";
      case "error":
        return "bg-red-50 border-red-200";
      case "info":
      default:
        return "bg-blue-50 border-blue-200";
    }
  };

  if (!isVisible) return null;

  return (
    <div
      className={`fixed top-4 right-4 z-50 max-w-sm bg-white ${getBgColor()} border rounded-lg shadow-md transition-all duration-300 ease-in-out`}
    >
      <div className="flex items-start p-4">
        <div className="flex-shrink-0">{getIcon()}</div>
        <div className="ml-3 w-0 flex-1">
          <p className="text-sm font-medium text-gray-900">{title}</p>
          <div className="mt-1 text-sm text-gray-500">{message}</div>
        </div>
        <button
          type="button"
          className="ml-4 flex-shrink-0 rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          onClick={handleClose}
        >
          <span className="sr-only">Close</span>
          <X className="h-5 w-5" />
        </button>
      </div>
      <div
        className="absolute bottom-0 left-0 h-1 bg-gray-300 transition-all duration-300"
        style={{ width: `${((duration - 0) / duration) * 100}%` }}
      ></div>
    </div>
  );
};

export default Notification;
