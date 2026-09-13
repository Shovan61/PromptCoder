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
import type { TextareaRenderable, ScrollBoxRenderable } from "@opentui/core";
import { useKeyboard, useRenderer } from "@opentui/react";
import { useCommandMenu } from "./command-menu/use-command-menu";
import type { Command } from "./command-menu/types";
import { useToast } from "../providers/toast";
import { useKeyboardLayer } from "../providers/keyboard-layer";
import { useDialog } from "../providers/dialog";

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
  const textareaRef = useRef<TextareaRenderable>(null);
  const onSubmitRef = useRef<() => void>(() => {});
  const mentionScrollRef = useRef<ScrollBoxRenderable>(null);

  // Number of onContentChange events to ignore while we programmatically
  // mutate the textarea (e.g. clearing it after running a command).
  const skipContentChangesRef = useRef(0);

  const renderer = useRenderer();
  const toast = useToast();

  useEffect(() => {
    // This makes the console visible in your terminal
    renderer.console.show();
  }, [renderer]);

  const { isTopLayer, push, pop, setResponder, exitApp } = useKeyboardLayer();

  const {
    showCommandMenu,
    commandQuery,
    selectedIndex,
    scrollRef,
    handleContentChange,
    resolveCommand,
    setSelectedIndex,
  } = useCommandMenu();

  const dialog = useDialog();

  // --- Run a command immediately (one Enter = execute) ---
  const runCommand = useCallback(
    (command: Command | undefined) => {
      const textarea = textareaRef.current;
      if (!textarea || !command) return;

      // Swallow the content-change event triggered by setText("") below
      // so we don't reopen the command menu.
      skipContentChangesRef.current += 1;
      textarea.setText("");

      command.action?.({
        exit: () => exitApp(),
        toast,
        dialog,
        navigate: () => null,
      });
    },
    [renderer, toast, dialog],
  );

  const handleTextareaContentChange = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Ignore programmatic mutations
    if (skipContentChangesRef.current > 0) {
      skipContentChangesRef.current -= 1;
      return;
    }

    handleContentChange(textarea.plainText);
  }, [handleContentChange]);

  const handleSubmit = useCallback(() => {
    if (disabled) return;

    const textarea = textareaRef.current;
    if (!textarea) return;

    const text = textarea.plainText.trim();
    if (text.length === 0) return;

    // Normal (non-command) submit
    onSubmit(text);
    skipContentChangesRef.current += 1;
    textarea.setText("");
  }, [disabled, onSubmit]);

  // Wire up the textarea submit handler once so it always reads latest state.
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.onSubmit = () => {
      onSubmitRef.current();
    };
  }, []);

  onSubmitRef.current = () => {
    if (disabled) return;

    // If the command menu is open, run the highlighted command immediately.
    if (showCommandMenu) {
      const command = resolveCommand(selectedIndex);
      runCommand(command);
      return;
    }

    handleSubmit();
  };

  const handleCommandExecute = useCallback(
    (index: number) => {
      const command = resolveCommand(index);
      runCommand(command);
    },
    [resolveCommand, runCommand],
  );

  // Register the base layer responder for ctrl+c dismissal
  useEffect(() => {
    setResponder("base", () => {
      if (disabled) return false;
      const textarea = textareaRef.current;
      if (textarea && textarea.plainText.length > 0) {
        skipContentChangesRef.current += 1;
        textarea.setText("");
        return true;
      }

      return false;
    });
  }, [disabled, setResponder]);

  return (
    <box
      border={["left"]}
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
        {showCommandMenu && (
          <box
            position="absolute"
            bottom="100%"
            left={0}
            width="100%"
            backgroundColor={"#1A1A24"}
            zIndex={10}
          >
            <CommandMenu
              query={commandQuery}
              selectedIndex={selectedIndex}
              scrollRef={scrollRef}
              onSelect={setSelectedIndex}
              onExecute={handleCommandExecute}
            />
          </box>
        )}
        <textarea
          ref={textareaRef}
          focused={!disabled && (isTopLayer("base") || isTopLayer("command"))}
          placeholder={`Ask anything..... "Fix a bug in the database"`}
          keyBindings={TEXTAREA_KEY_BINDINGS}
          onContentChange={handleTextareaContentChange}
        />
        <StatusBar />
      </box>
    </box>
  );
}
