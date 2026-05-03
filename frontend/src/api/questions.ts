import { apiClient } from './client'

export interface InterviewQuestion {
  id: number
  event_id: number
  question: string
  my_answer: string
  reflection: string
  tags: string
  created_at: string
}

export interface InterviewQuestionCreate {
  event_id: number
  question: string
  my_answer?: string
  reflection?: string
  tags?: string
}

export type InterviewQuestionUpdate = Partial<
  Omit<InterviewQuestion, 'id' | 'event_id' | 'created_at'>
>

export const questionsApi = {
  list: (eventId: number) =>
    apiClient
      .get<InterviewQuestion[]>('/questions', { params: { event_id: eventId } })
      .then(r => r.data),
  create: (data: InterviewQuestionCreate) =>
    apiClient.post<InterviewQuestion>('/questions', data).then(r => r.data),
  update: (id: number, data: InterviewQuestionUpdate) =>
    apiClient.patch<InterviewQuestion>(`/questions/${id}`, data).then(r => r.data),
  delete: (id: number) => apiClient.delete(`/questions/${id}`).then(() => undefined),
}

const NON_INTERVIEW_STAGES = new Set([
  'Offer 沟通',
  '入职',
  '被拒',
  '主动放弃',
  '泡池子',
])

export function isInterviewLikeStage(stage: string): boolean {
  return !NON_INTERVIEW_STAGES.has(stage)
}
