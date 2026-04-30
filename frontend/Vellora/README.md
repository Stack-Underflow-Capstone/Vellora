# Frontend Dev Guide to Expo / Running App

## Getting started

1. Install dependencies

   ```bash
   npm install
   ```

2. Start the app

   ```bash
   npx expo start
   ```

In the output, you'll find options to open the app in a

- [development build](https://docs.expo.dev/develop/development-builds/introduction/)
- [Android emulator](https://docs.expo.dev/workflow/android-studio-emulator/)
- [iOS simulator](https://docs.expo.dev/workflow/ios-simulator/)
- [Expo Go](https://expo.dev/go), a limited sandbox for trying out app development with Expo

You can start developing by editing the files inside the **app** directory. This project uses [file-based routing](https://docs.expo.dev/router/introduction).

## Get a fresh project

When you're ready, run:

```bash
npm run reset-project
```

This command will move the starter code to the **app-example** directory and create a blank **app** directory where you can start developing.

## Docs

To learn more about developing your project with Expo, look at the following resources:

- [Expo documentation](https://docs.expo.dev/): Learn fundamentals, or go into advanced topics with our [guides](https://docs.expo.dev/guides).
- [Learn Expo tutorial](https://docs.expo.dev/tutorial/introduction/): Follow a step-by-step tutorial where you'll create a project that runs on Android, iOS, and the web.

## File Structure

```
.
├── .vscode/         # Holds setting configs for VS Code
├── app/
│   ├── _layout.tsx     # Used for specific level of navigation (tab or stack), handles global font loading, splash screen mgmt, and context providers
│   └── tabs/
│       └── index.tsx   # Shows inital screen or home screen
├── assets/             # Stores files, images, static things.
├── components/         # Stores reusable global components
├── constants/          # App Wide Constants (colors, spacing, etc)
├── hooks/              # Custom React Hooks
└── scripts/            # Util Scripts

```

