import { useState } from "react";
import type { NotSureOption, RouteOption } from "../api/types";
import DescriptionField from "./DescriptionField";
import RadioGroup from "./RadioGroup";
import SubmitButton from "./SubmitButton";

type Props = {
  routes: RouteOption[];
  notSureOption: NotSureOption;
  busy: boolean;
  onSubmit: (choice: { scenario?: string; description?: string }) => void;
};

/** Mirrors MAX_DESCRIPTION_LENGTH in backend/triage/views.py. */
const MAX_DESCRIPTION_LENGTH = 2000;

type FieldName = "choice" | "description";
type FieldError = { field: FieldName; message: string };

/**
 * The first step: pick a familiar scenario, or describe the problem instead.
 *
 * "I am not sure" is the fourth radio in the same group, not a link off to the
 * side, so it costs no more effort than the other three.
 */
const ScenarioStep = ({ routes, notSureOption, busy, onSubmit }: Props) => {
  const [scenario, setScenario] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState<FieldError | null>(null);

  const validate = (): FieldError | null => {
    if (scenario) return null;
    if (!description.trim()) {
      return {
        field: "choice",
        message:
          "Choose one of the options, or describe the problem in your own words.",
      };
    }
    if (description.length > MAX_DESCRIPTION_LENGTH) {
      return {
        field: "description",
        message: "Please shorten this to a sentence or two.",
      };
    }
    return null;
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const problem = validate();
    setError(problem);
    // Checking here rather than letting the server answer means the person is
    // told immediately, and an obviously empty form never becomes a request.
    if (problem) return;

    // A chosen scenario wins over typed text, matching what the API does with
    // the same pair, so the person is never told something they did not pick.
    onSubmit(scenario ? { scenario } : { description });
  };

  const messageFor = (field: FieldName) =>
    error?.field === field ? error.message : null;

  const choices = [
    ...routes.map((route) => ({
      id: route.id,
      label: route.label,
      hint: route.legalTerm,
    })),
    { id: notSureOption.id, label: notSureOption.label },
  ];

  return (
    <form onSubmit={handleSubmit} noValidate>
      <RadioGroup
        legend="What is your question about?"
        name="scenario"
        choices={choices}
        value={scenario}
        error={messageFor("choice")}
        onChange={(value) => {
          setScenario(value);
          setError(null);
        }}
      />
      <DescriptionField
        value={description}
        error={messageFor("description")}
        onChange={(value) => {
          setDescription(value);
          setError(null);
        }}
      />
      <SubmitButton busy={busy} />
    </form>
  );
};

export default ScenarioStep;
