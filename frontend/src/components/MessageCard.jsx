export default function MessageCard({ kind, title, children }) {
  return (
    <div className={`message-card message-card--${kind}`} role="status">
      <span className="message-card__mark" aria-hidden="true">
        {kind === "error" ? "!" : kind === "empty" ? "⌕" : "↗"}
      </span>
      <div>
        <strong>{title}</strong>
        {children && <p>{children}</p>}
      </div>
    </div>
  );
}
