import { apiClient } from './client'

export interface Application {
  id: number
  company: string
  position: string
  jd: string
  channel: string
  applied_at: string
  status: string
  note: string
  created_at: string
}

export type ApplicationCreate = Omit<Application, 'id' | 'created_at' | 'status'> & {
  status?: string
}

export type ApplicationUpdate = Partial<Omit<Application, 'id' | 'created_at'>>

export const applicationsApi = {
  list: () => apiClient.get<Application[]>('/applications').then(r => r.data),
  get: (id: number) => apiClient.get<Application>(`/applications/${id}`).then(r => r.data),
  create: (data: ApplicationCreate) =>
    apiClient.post<Application>('/applications', data).then(r => r.data),
  update: (id: number, data: ApplicationUpdate) =>
    apiClient.patch<Application>(`/applications/${id}`, data).then(r => r.data),
  delete: (id: number) => apiClient.delete(`/applications/${id}`).then(() => undefined),
}
