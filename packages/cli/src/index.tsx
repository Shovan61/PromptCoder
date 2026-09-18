import { createCliRenderer, TextAttributes } from "@opentui/core";
import { createRoot } from "@opentui/react";
import { Header } from "./components/header";
import { InputBar } from "./components/input-bar";
import { ToastProvider } from "./providers/toast";
import { KeyboardLayerProvider } from "./providers/keyboard-layer";
import { DialogProvider } from "./providers/dialog";
import { ThemeProvider } from "./providers/theme";

function App() {
  return (
    <ThemeProvider>
      <KeyboardLayerProvider>
        <DialogProvider>
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
        </DialogProvider>
      </KeyboardLayerProvider>
    </ThemeProvider>
  );
}

const renderer = await createCliRenderer({
  exitOnCtrlC: false,
  targetFps: 60,
});

createRoot(renderer).render(<App />);
