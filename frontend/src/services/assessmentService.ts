import type { AssessmentRequest, AssessmentResponse, ModelsStatusResponse } from '../types/assessment'
import { getJson, postJson } from './apiClient'

export function submitAssessment(request: AssessmentRequest): Promise<AssessmentResponse> {
  return postJson<AssessmentResponse>('/api/assessment/predict', request)
}

export function fetchModelsStatus(): Promise<ModelsStatusResponse> {
  return getJson<ModelsStatusResponse>('/api/models/status')
}
