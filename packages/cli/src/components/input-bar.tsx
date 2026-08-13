import { StatusBar } from "./status-bar";

type Props = {
  onSubmit: (text: string) => void;
  disabled?: boolean;
};

export function InputBar({ onSubmit, disabled = false }: Props) {
  return (
    <box>
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
        />
        <StatusBar />
      </box>
    </box>
  );
}
