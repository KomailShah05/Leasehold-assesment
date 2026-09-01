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
        A sentence or two is enough. Please do not include personal details.
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
        value={value}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? 'description-hint description-error' : 'description-hint'}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  )
}

export default DescriptionField
