// User types
export interface User {
  id: number
  username: string
  email: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface SignupData {
  username: string
  email: string
  password: string
  password2?: string
}

// Activity types
export interface Activity {
  id: number
  user: number
  name: string
  description?: string
  energy_level: -2 | -1 | 0 | 1 | 2
  activity_date: string
  created_at: string
  updated_at: string
}

export interface ActivityFormData {
  name: string
  description?: string
  energy_level: number
  activity_date?: string
}

// Dashboard types
export interface DailyStats {
  count: number
  avg_energy: number
}

export interface WeeklyDataPoint {
  date: string
  avg_energy: number
  count: number
}

export interface TopActivity {
  name: string
  avg_energy: number
  count: number
}

export interface DashboardData {
  today_count: number
  today_avg: number
  weekly_data: WeeklyDataPoint[]
  draining_activities: TopActivity[]
  energizing_activities: TopActivity[]
  recent_activities: Activity[]
}

// API Response types
export interface ApiError {
  message: string
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
