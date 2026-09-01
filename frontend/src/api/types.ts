/** The shapes the triage API returns. Mirrors backend/triage/views.py. */

export type RouteOption = {
  id: string
  label: string
  legalTerm: string
}

export type NotSureOption = {
  id: string
  label: string
}

export type RoutesResponse = {
  routes: RouteOption[]
  notSureOption: NotSureOption
}

export type Guidance = {
  title: string
  summary: string
  leaseUrl: string
}

export type AnswerOption = {
  id: string
  label: string
}

export type TriageQuestion = {
  id: string
  text: string
  answers: AnswerOption[]
}

/**
 * One discriminated union rather than a bag of nullable fields: the UI switches
 * on `status` and the compiler makes sure every case is handled.
 */
export type TriageResponse =
  | {
      status: 'question'
      route: RouteOption
      inferred: boolean
      question: TriageQuestion
    }
  | { status: 'outcome'; route: RouteOption; guidance: Guidance }
  | {
      status: 'fallback'
      title: string
      message: string
      guidance: Guidance | null
    }

export type TriageRequest = {
  scenario?: string
  description?: string
  answerId?: string
}
