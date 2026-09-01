import { useFocusWhen } from '../hooks/useFocusWhen'
import FieldError from './FieldError'

type Props = {
  value: string
  error?: string | null
  onChange: (value: string) => void
}

/** The free-text alternative to picking a scenario. */
const DescriptionField = ({ value, error, onChange }: Props) => {
  const errorRef = useFocusWhen<HTMLParagraphElement>(Boolean(error))

  return (
    <div className="field">
      <label htmlFor="description">Or describe the problem in your own words</label>
      <p className="hint" id="description-hint">
        A sentence or two is enough. There is no need to include your name, address or contact
        details, and we do not keep what you write.
      </p>
      {error && (
        <FieldError id="description-error" ref={errorRef}>
          {error}
        </FieldError>
      )}
      <textarea
        id="description"
        name="description"
        rows={4}
        // What someone types here is about their home and may name people or
        // places. autoComplete="off" keeps the browser from storing it in form
        // history, where it would outlive the request the way nothing else in
        // this prototype does.
        autoComplete="off"
        spellCheck={false}
        value={value}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? 'description-hint description-error' : 'description-hint'}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  )
}

export default DescriptionField
