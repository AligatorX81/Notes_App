# Building the Android APK

## Prerequisites

1. Install Android Studio: https://developer.android.com/studio
2. Install Java Development Kit (JDK) 11 or newer
3. Set up Android SDK and environment variables

## Steps to build the APK

1. Build the web app and sync with Android:
   ```
   npm run build:android
   ```

2. Open the Android project in Android Studio:
   ```
   npm run open:android
   ```

3. In Android Studio:
   - Wait for Gradle sync to complete
   - Go to Build > Build Bundle(s) / APK(s) > Build APK(s)
   - The APK will be generated in `android/app/build/outputs/apk/debug/app-debug.apk`

## Creating a signed release APK

1. In Android Studio, go to Build > Generate Signed Bundle / APK
2. Select APK and click Next
3. Create a new keystore or use an existing one
4. Fill in the required information and click Next
5. Select release build variant and click Finish
6. The signed APK will be in `android/app/build/outputs/apk/release/app-release.apk`

## Troubleshooting

- If you encounter build errors, check that your Android SDK is properly configured
- Make sure you have the correct JDK version installed
- Check that all required Android SDK components are installed through the SDK Manager in Android Studio
