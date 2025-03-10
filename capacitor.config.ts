import { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "com.htmljscompletion.app",
  appName: "HTML/JS Code Completion Tool",
  webDir: "dist",
  server: {
    androidScheme: "https",
  },
};

export default config;
