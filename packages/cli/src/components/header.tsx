export function Header() {
  return (
    <box justifyContent="center" alignItems="center">
      <box flexDirection="row" justifyContent="center" gap={0.2} alignItems="center">
        <ascii-font font="block" text="Prompt"  />
        <ascii-font font="tiny" text="Coder" />
      </box>
    </box>
  );
};