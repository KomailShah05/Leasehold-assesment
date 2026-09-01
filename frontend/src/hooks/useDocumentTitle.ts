import { useEffect } from 'react'

const SERVICE_NAME = 'Leasehold enquiry triage'

/**
 * Keeps the page title in step with what is on screen.
 *
 * The journey replaces the content without changing the URL, so without this
 * the title says the same thing throughout. That matters most to people who
 * rely on the title for orientation: screen reader users often hear it when
 * returning to a tab, and it is what browser history and tab switching show.
 */
export const useDocumentTitle = (step: string | null) => {
  useEffect(() => {
    document.title = step ? `${step} - ${SERVICE_NAME}` : SERVICE_NAME
  }, [step])
}
