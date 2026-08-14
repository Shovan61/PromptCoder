import { EmptyBorder } from "./border";
import { CommandMenu } from "./command-menu";
import { StatusBar } from "./status-bar";
import type { KeyBinding } from "@opentui/core";
import {
  useRef,
  useState,
  useCallback,
  useEffect,
  type RefObject,
} from "react";

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
        backgroundColor={"#292937"}
        width="100%"
        gap={1}
      >
        {true && (
          <>
            <box
              position="absolute"
              bottom="100%"
              left={0}
              width="100%"
              backgroundColor={"#1A1A24"}
              zIndex={10}
            >
              <CommandMenu
                query={""}
                // selectedIndex={selectedIndex}
                // scrollRef={scrollRef}
                // onSelect={setSelectedIndex}
                // onExecute={handleCommandExecute}
              />
            </box>
          </>
        )}
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
