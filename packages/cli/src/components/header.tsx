export function Header() {
  return (
    <box
      justifyContent="center"
      alignItems="center"
      paddingY={1.5}
      backgroundColor="#0A0A1A"
    >
      <box flexDirection="column" alignItems="center" gap={0.2}>
        <box flexDirection="row" gap={0.2} alignItems="center">
          <box>
            <ascii-font font="block" text="Prompt" />
          </box>
          <box paddingX={0.2}>
            <text>•</text>
          </box>
          <box>
            <ascii-font font="tiny" text="Coder" />
          </box>
        </box>

        <box
          flexDirection="row"
          gap={0.5}
          alignItems="center"
          paddingX={1}
          paddingY={0.1}
        >
          <box>
            <text>✦</text>
          </box>
          <box>
            <text>Intelligent Code Assistant</text>
          </box>
          <box>
            <text>✦</text>
          </box>
        </box>
      </box>
    </box>
  );
}
