import type { Ref } from 'react'
import type { Guidance } from '../api/types'

type Props = {
  guidance: Guidance
  headingRef?: Ref<HTMLHeadingElement>
}

/**
 * A possible next step, in wording an editor wrote.
 *
 * The summary is rendered as text, never as markup, and the link goes out to
 * LEASE so the authoritative guidance stays theirs. The link says it opens a
 * new tab, because a tab opening unannounced is disorienting.
 */
const GuidanceCard = ({ guidance, headingRef }: Props) => (
  <>
    <h2 ref={headingRef} tabIndex={headingRef ? -1 : undefined}>
      {guidance.title}
    </h2>
    <p>{guidance.summary}</p>
    <p>
      <a href={guidance.leaseUrl} rel="noreferrer noopener" target="_blank">
        Read the full guidance on the LEASE website (opens in a new tab)
      </a>
    </p>
  </>
)

export default GuidanceCard
