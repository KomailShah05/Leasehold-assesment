import { useFocusWhen } from '../hooks/useFocusWhen'
import type { TriageResponse } from '../api/types'
import GuidanceCard from './GuidanceCard'

type Props = {
  result: Extract<TriageResponse, { status: 'outcome' | 'fallback' }>
  onRestart: () => void
}

/**
 * The end of the journey, for both a matched outcome and the fallback.
 *
 * Both are framed the same way on purpose: a possible next step and a route to
 * a person. The prototype signposts, so nothing here is phrased as advice.
 */
const ResultStep = ({ result, onRestart }: Props) => {
  // This is the answer they came for, so start them at the top of it rather
  // than leaving focus on the button that produced it.
  const headingRef = useFocusWhen<HTMLHeadingElement>(true)
  const isFallback = result.status === 'fallback'

  return (
    <div>
      {result.status === 'fallback' && (
        <>
          <h2 ref={headingRef} tabIndex={-1}>
            {result.title}
          </h2>
          <p>{result.message}</p>
        </>
      )}

      {result.guidance ? (
        // On a fallback the heading above already has focus, so the guidance
        // heading below it must not also claim it.
        <GuidanceCard guidance={result.guidance} headingRef={isFallback ? undefined : headingRef} />
      ) : (
        <p>You can contact LEASE for free initial advice about your situation.</p>
      )}

      <p className="not-advice">
        This is general information to help you find the right guidance. It is not legal advice
        about your own situation.
      </p>

      <button type="button" onClick={onRestart}>
        Start again
      </button>
    </div>
  )
}

export default ResultStep
