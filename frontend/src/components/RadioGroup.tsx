import FieldError from "./FieldError";

export type Choice = {
  id: string;
  label: string;
  /** A legal phrase or clarification, rendered smaller but inside the label. */
  hint?: string;
};

type Props = {
  legend: string;
  name: string;
  choices: Choice[];
  value: string;
  error?: string | null;
  onChange: (value: string) => void;
};

/**
 * A labelled group of radio buttons.
 *
 * Radios in a fieldset rather than a dropdown, because a dropdown hides its
 * options until you work out you have to open it. Every screen that asks a
 * question uses this, so the markup, hit areas and error wiring cannot drift
 * apart between steps.
 */
const RadioGroup = ({
  legend,
  name,
  choices,
  value,
  error,
  onChange,
}: Props) => {
  const errorId = `${name}-error`;

  return (
    <fieldset aria-describedby={error ? errorId : undefined}>
      <legend>
        <h2>{legend}</h2>
      </legend>

      {error && <FieldError id={errorId}>{error}</FieldError>}

      {choices.map((choice) => (
        <div className="choice" key={choice.id}>
          <input
            type="radio"
            id={`${name}-${choice.id}`}
            name={name}
            value={choice.id}
            checked={value === choice.id}
            onChange={(event) => onChange(event.target.value)}
          />
          <label htmlFor={`${name}-${choice.id}`}>
            {choice.label}
            {/* The hint sits inside the label, not in a tooltip, so a screen
                reader announces it along with the plain wording. The space
                matters: without it the accessible name runs the two phrases
                together as one word. */}
            {choice.hint && (
              <>
                {" "}
                <span className="legal-term">{choice.hint}</span>
              </>
            )}
          </label>
        </div>
      ))}
    </fieldset>
  );
};

export default RadioGroup;
