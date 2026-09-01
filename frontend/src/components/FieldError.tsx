import type { Ref } from 'react'

type Props = {
  id: string
  children: string
  ref?: Ref<HTMLParagraphElement>
}

/**
 * One error message, tied to the control it is about.
 *
 * Never signalled by colour alone: the text is bold and sits directly above
 * its control, and the caller links it with aria-describedby.
 *
 * Deliberately not role="alert". Focus is moved here instead, which announces
 * it once. Doing both would announce the same message twice.
 */
const FieldError = ({ id, children, ref }: Props) => (
  <p className="field-error" id={id} ref={ref} tabIndex={-1}>
    {children}
  </p>
)

export default FieldError
