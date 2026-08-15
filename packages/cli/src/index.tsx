import { createCliRenderer, ConsolePosition } from "@opentui/core";
import { createRoot } from "@opentui/react";
import { Header } from "./components/header";
import { InputBar } from "./components/input-bar";

function App() {
  return (
    <box
      backgroundColor="#0D0D12"
      width={"100%"}
      height={"100%"}
      gap={2}
      alignItems="center"
      justifyContent="center"
    >
      <Header />
      <box width={"100%"} maxWidth={78} paddingX={2}>
        <InputBar onSubmit={() => {}} />
      </box>
    </box>
  );
}

const renderer = await createCliRenderer({
  consoleOptions: {
    position: ConsolePosition.BOTTOM, // TOP, LEFT, RIGHT
    sizePercent: 30,
    colorInfo: "#00FFFF",
    colorWarn: "#FFFF00",
    colorError: "#FF0000",
    startInDebugMode: false // Show file/line info
  },
  // Auto-open on error in dev mode
  openConsoleOnError: true
})
createRoot(renderer).render(<App />);
