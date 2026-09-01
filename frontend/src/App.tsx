import ErrorAlert from "./components/ErrorAlert";
import QuestionStep from "./components/QuestionStep";
import ResultStep from "./components/ResultStep";
import ScenarioStep from "./components/ScenarioStep";
import { useTriage } from "./hooks/useTriage";

/**
 * Composes the journey. All the behaviour lives in useTriage, so this file
 * only decides which step belongs on screen.
 */
const App = () => {
  const {
    routes,
    result,
    error,
    busy,
    canRetry,
    start,
    answer,
    retry,
    restart,
  } = useTriage();

  return (
    <main>
      <h1>Leasehold enquiry triage</h1>
      <p>
        Answer one or two questions and we will point you to guidance that may
        help. This service gives general information, not legal advice about
        your own situation.
      </p>

      {error && (
        <ErrorAlert
          message={error.message}
          busy={busy}
          // Retrying an "invalid" error would send the same rejected input
          // again, so only offer it where a second attempt could succeed.
          onRetry={error.kind !== "invalid" && canRetry ? retry : undefined}
        />
      )}

      {routes === null && !error && <p>Loading…</p>}

      {routes !== null && result === null && (
        <ScenarioStep
          routes={routes.routes}
          notSureOption={routes.notSureOption}
          busy={busy}
          onSubmit={start}
        />
      )}

      {result?.status === "question" && (
        <QuestionStep
          route={result.route}
          question={result.question}
          inferred={result.inferred}
          busy={busy}
          onAnswer={answer}
        />
      )}

      {(result?.status === "outcome" || result?.status === "fallback") && (
        <ResultStep result={result} onRestart={restart} />
      )}
    </main>
  );
};

export default App;
