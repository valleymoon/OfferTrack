import { apiClient } from './client'

export interface TimelineEvent {
  id: number
  application_id: number
  stage: string
  happened_at: string
  note: string
  created_at: string
}

export interface TimelineEventCreate {
  application_id: number
  stage: string
  happened_at: string
  note?: string
}

export type TimelineEventUpdate = Partial<Omit<TimelineEvent, 'id' | 'application_id' | 'created_at'>>

export const eventsApi = {
  list: (applicationId: number) =>
    apiClient
      .get<TimelineEvent[]>('/events', { params: { application_id: applicationId } })
      .then(r => r.data),
  create: (data: TimelineEventCreate) =>
    apiClient.post<TimelineEvent>('/events', data).then(r => r.data),
  update: (id: number, data: TimelineEventUpdate) =>
    apiClient.patch<TimelineEvent>(`/events/${id}`, data).then(r => r.data),
  delete: (id: number) => apiClient.delete(`/events/${id}`).then(() => undefined),
}

export const PRESET_STAGES = [
  '笔试/测评',
  '一面',
  '二面',
  '三面',
  '终面',
  'HR 面',
  'Offer 沟通',
  '入职',
  '被拒',
  '主动放弃',
  '泡池子',
] as const
