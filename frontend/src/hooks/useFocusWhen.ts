import { useEffect, useRef } from 'react'

/**
 * Moves focus to an element when something becomes true.
 *
 * Used for the two moments where leaving focus alone would strand someone: a
 * new step appearing, and a validation error appearing. Without this, a
 * keyboard or screen reader user stays at the bottom of a page whose content
 * has changed above them, with no way to know it happened.
 *
 * The element it is attached to needs tabIndex={-1}, so it can receive focus
 * programmatically without joining the tab order.
 */
export const useFocusWhen = <T extends HTMLElement>(shouldFocus: boolean) => {
  const ref = useRef<T>(null)
  const focusedAlready = useRef(false)

  useEffect(() => {
    // Only on the transition into the state, so a re-render for an unrelated
    // reason does not yank focus back and interrupt someone mid-sentence.
    if (shouldFocus && !focusedAlready.current) {
      ref.current?.focus()
    }
    focusedAlready.current = shouldFocus
  }, [shouldFocus])

  return ref
}
