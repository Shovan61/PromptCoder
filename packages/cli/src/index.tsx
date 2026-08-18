import { createCliRenderer, TextAttributes } from "@opentui/core";
import { createRoot } from "@opentui/react";
import { Header } from "./components/header";
import { InputBar } from "./components/input-bar";
import { ToastProvider } from "./providers/toast";
import { KeyboardLayerProvider } from "./providers/keyboard-layer";

function App() {
  return (
    <KeyboardLayerProvider>
      <ToastProvider>
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
      </ToastProvider>
    </KeyboardLayerProvider>
  );
}

const renderer = await createCliRenderer({
  exitOnCtrlC: false,
  targetFps: 60,
});

createRoot(renderer).render(<App />);
