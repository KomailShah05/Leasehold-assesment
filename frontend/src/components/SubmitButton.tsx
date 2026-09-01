type Props = {
  busy: boolean
  children?: string
}

/** The one way to move to the next step, so its busy wording stays consistent. */
const SubmitButton = ({ busy, children = 'Continue' }: Props) => (
  <button type="submit" disabled={busy}>
    {busy ? 'Checking…' : children}
  </button>
)

export default SubmitButton
