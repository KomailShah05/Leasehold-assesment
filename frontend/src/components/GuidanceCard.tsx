import type { Guidance } from "../api/types";

type Props = {
  guidance: Guidance;
};

/**
 * A possible next step, in wording an editor wrote.
 *
 * The summary is rendered as text, never as markup, and the link goes out to
 * LEASE so the authoritative guidance stays theirs.
 */
const GuidanceCard = ({ guidance }: Props) => (
  <>
    <h2>{guidance.title}</h2>
    <p>{guidance.summary}</p>
    <p>
      <a href={guidance.leaseUrl} rel="noreferrer noopener" target="_blank">
        Read the full guidance on the LEASE website (opens in a new tab)
      </a>
    </p>
  </>
);

export default GuidanceCard;
