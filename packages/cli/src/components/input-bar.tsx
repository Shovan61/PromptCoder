import { EmptyBorder } from "./border";
import { StatusBar } from "./status-bar";
import type { KeyBinding } from "@opentui/core";

type Props = {
  onSubmit: (text: string) => void;
  disabled?: boolean;
};

export const TEXTAREA_KEY_BINDINGS: KeyBinding[] = [
  { name: "return", action: "submit" },
  { name: "enter", action: "submit" },
  { name: "return", shift: true, action: "newline" },
  { name: "enter", shift: true, action: "newline" },
];

export function InputBar({ onSubmit, disabled = false }: Props) {
  return (
    <box
      border={["left"]}
      //   borderColor={mode === Mode.BUILD ? colors.primary : colors.planMode}
      customBorderChars={{
        ...EmptyBorder,
        vertical: "┃",
        bottomLeft: "╹",
      }}
      borderColor={"cyan"}
      width="100%"
    >
      <box
        position="relative"
        justifyContent="center"
        paddingX={2}
        paddingY={1}
        backgroundColor={"#4c4c6b"}
        width="100%"
        gap={1}
      >
        <textarea
          focused={disabled}
          placeholder={`Ask anything..... "Fix a bug in the database"`}
        keyBindings={TEXTAREA_KEY_BINDINGS}
        />
        <StatusBar />
      </box>
    </box>
  );
}
