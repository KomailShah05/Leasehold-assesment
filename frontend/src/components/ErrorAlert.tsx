type Props = {
  message: string;
  busy: boolean;
  onRetry?: (() => void) | undefined;
};

/**
 * A failure the person can act on.
 *
 * role="alert" so it is announced when it appears, rather than only being
 * noticed by someone looking at that part of the page. A retry is offered only
 * when the caller judges that trying again might work.
 */
const ErrorAlert = ({ message, busy, onRetry }: Props) => (
  <div className="error" role="alert">
    <p>{message}</p>
    {onRetry && (
      <button type="button" onClick={onRetry} disabled={busy}>
        {busy ? "Trying again…" : "Try again"}
      </button>
    )}
  </div>
);

export default ErrorAlert;
