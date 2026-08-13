import { TextAttributes } from "@opentui/core";
// import { useTheme } from "../providers/theme";
// import { usePromptConfig } from "../providers/prompt-config";
// import { Mode } from "@nightcode/shared";

export function StatusBar() {
  //   const { mode, model } = usePromptConfig();
  //   const { colors } = useTheme();

  return (
    <box flexDirection="row" gap={1}>
      <text
        //   fg={mode === Mode.PLAN ? colors.planMode : colors.primary}
        fg={"#0D0D12"}
      >
        {/* {mode === Mode.PLAN ? "Plan" : "Build"} */}
        Build
      </text>

      <text
        attributes={TextAttributes.DIM}
        //    fg={colors.dimSeparator}
      >
        ›
      </text>
      <text>{/* {model} */}Gemini 2.5 Flash-Lite</text>
    </box>
  );
}
