type Props = {
  id: string;
  children: string;
};

/**
 * One error message, tied to the control it is about.
 *
 * Never signalled by colour alone: the text is bold and sits directly above
 * its control, and the caller links it with aria-describedby.
 */
const FieldError = ({ id, children }: Props) => (
  <p className="field-error" id={id}>
    {children}
  </p>
);

export default FieldError;
