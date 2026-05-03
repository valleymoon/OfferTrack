import { apiClient } from './client'

export interface DashboardStats {
  total: number
  interviewing: number
  offered: number
  ended: number
}

export interface DashboardUpcomingApplication {
  id: number
  company: string
  position: string
  status: string
}

export interface DashboardUpcomingEvent {
  event_id: number
  stage: string
  happened_at: string
  note: string
  application: DashboardUpcomingApplication
}

export interface DashboardStaleApplication {
  id: number
  company: string
  position: string
  applied_at: string
  days_since_applied: number
}

export interface DashboardData {
  stats: DashboardStats
  upcoming_interviews: DashboardUpcomingEvent[]
  stale_applications: DashboardStaleApplication[]
}

export interface DashboardParams {
  past_days: number
  future_days: number
  stale_days: number
}

export const dashboardApi = {
  get: (params: DashboardParams) =>
    apiClient.get<DashboardData>('/dashboard', { params }).then(r => r.data),
}

export interface TimeWindowPreset {
  label: string
  past: number
  future: number
}

export const TIME_WINDOW_PRESETS: TimeWindowPreset[] = [
  { label: '仅未来 7 天', past: 0, future: 7 },
  { label: '过去 3 + 未来 7 天', past: 3, future: 7 },
  { label: '过去 7 + 未来 7 天', past: 7, future: 7 },
]
