import { useState } from "react";
import type { RouteOption, TriageQuestion } from "../api/types";
import RadioGroup from "./RadioGroup";
import SubmitButton from "./SubmitButton";

type Props = {
  route: RouteOption;
  question: TriageQuestion;
  inferred: boolean;
  busy: boolean;
  onAnswer: (answerId: string) => void;
};

/**
 * The single follow-up question.
 *
 * When the route was inferred from someone's own words we say so plainly at
 * the top, rather than presenting our guess as fact. The answer list already
 * contains an option for telling us we were wrong; the API adds it.
 */
const QuestionStep = ({ route, question, inferred, busy, onAnswer }: Props) => {
  const [answerId, setAnswerId] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!answerId) {
      setError("Choose one of the options to carry on.");
      return;
    }
    setError(null);
    onAnswer(answerId);
  };

  return (
    <form onSubmit={handleSubmit} noValidate>
      {inferred && (
        <p className="inferred">
          From what you wrote, this looks like it may be about:{" "}
          <strong>{route.label}</strong>. If that is wrong, you can say so
          below.
        </p>
      )}
      <RadioGroup
        legend={question.text}
        name="answer"
        choices={question.answers}
        value={answerId}
        error={error}
        onChange={(value) => {
          setAnswerId(value);
          setError(null);
        }}
      />
      <SubmitButton busy={busy} />
    </form>
  );
};

export default QuestionStep;
