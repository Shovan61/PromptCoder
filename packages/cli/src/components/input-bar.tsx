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

  const renderer = useRenderer();
  const toast = useToast();

  const { isTopLayer, push, pop, setResponder } = useKeyboardLayer();

  const {
    showCommandMenu,
    commandQuery,
    selectedIndex,
    scrollRef,
    handleContentChange,
    resolveCommand,
    setSelectedIndex,
  } = useCommandMenu();

  // Store the selected command to execute on second Enter
  const pendingCommandRef = useRef<Command | null>(null);

  const handleCommand = useCallback((command: Command | undefined) => {
    const textarea = textareaRef.current;
    if (!textarea || !command) return;

    // Clear the textarea
    textarea.setText("");

    // Store command as pending
    pendingCommandRef.current = command;

    // Insert the command text (e.g., "/exit") into textarea
    textarea.insertText(command.value + " ");

    // Command will be executed on the next Enter press
  }, []);

  const handleTextareaContentChange = useCallback(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const text = textarea.plainText;

    // Clear pending command if user types something else
    if (
      pendingCommandRef.current &&
      text !== pendingCommandRef.current.value + " "
    ) {
      pendingCommandRef.current = null;
    }

    handleContentChange(textarea.plainText);
  }, [handleContentChange]);

  const handleSubmit = useCallback(() => {
    if (disabled) return;

    const textarea = textareaRef.current;
    if (!textarea) return;

    const text = textarea.plainText.trim();

    if (text.length === 0) return;

    // Check if this is a command we need to execute
    if (pendingCommandRef.current && text === pendingCommandRef.current.value) {
      // Execute the pending command
      const command = pendingCommandRef.current;
      if (command.action) {
        command.action({
          exit: () => renderer.destroy(),
          toast,
          navigate: () => null,
        });
      }
      pendingCommandRef.current = null;
      // ✅ Don't call setText() here - the renderer may be destroyed
      return;
    }

    // Normal submit
    onSubmit(text);
    textarea.setText("");
  }, [disabled, onSubmit, renderer, toast]);

  // Wire up textarea submit handler once so it always reads the latest state.
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.onSubmit = () => {
      onSubmitRef.current();
    };
  }, []);

  onSubmitRef.current = () => {
    if (disabled) return;

    if (showCommandMenu) {
      const command = resolveCommand(selectedIndex);
      handleCommand(command);
      return;
    }

    handleSubmit();
  };

  const handleCommandExecute = useCallback(
    (index: number) => {
      const command = resolveCommand(index);
      handleCommand(command);
    },
    [resolveCommand, handleCommand],
  );

  // Register the base layer responder for ctrl+c dismissal
  useEffect(() => {
    setResponder("base", () => {
      if (disabled) return false;
      const textarea = textareaRef.current;
      if (textarea && textarea.plainText.length > 0) {
        textarea.setText("");
        return true;
      }

      return false;
    });
  }, []);

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
                query={commandQuery}
                selectedIndex={selectedIndex}
                scrollRef={scrollRef}
                onSelect={setSelectedIndex}
                onExecute={handleCommandExecute}
              />
            </box>
          </>
        )}
        <textarea
          ref={textareaRef}
          focused={disabled}
          placeholder={`Ask anything..... "Fix a bug in the database"`}
          keyBindings={TEXTAREA_KEY_BINDINGS}
          onContentChange={handleTextareaContentChange}
        />
        <StatusBar />
      </box>
    </box>
  );
}
