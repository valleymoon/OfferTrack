import { apiClient } from './client'

export interface BackupPayload {
  version: number
  exported_at: string | null
  applications: Record<string, unknown>[]
  events: Record<string, unknown>[]
  questions: Record<string, unknown>[]
}

export interface ImportResult {
  mode: 'overwrite' | 'merge'
  applications_imported: number
  events_imported: number
  questions_imported: number
}

export const backupApi = {
  export: () =>
    apiClient.get<BackupPayload>('/backup/export').then(r => r.data),
  import: (mode: 'overwrite' | 'merge', payload: BackupPayload) =>
    apiClient
      .post<ImportResult>('/backup/import', { mode, payload })
      .then(r => r.data),
}
