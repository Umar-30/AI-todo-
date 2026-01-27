/**
 * Task entity interface for Todo AI Chatbot.
 */
export interface Task {
  id: string
  user_id: string
  title: string
  description: string | null
  completed: boolean
  due_date: string | null // ISO8601 format
  priority: 'high' | 'medium' | 'low' | null
  category: string | null
  created_at: string // ISO8601 format
  updated_at: string // ISO8601 format
}

/**
 * Response from GET /api/{user_id}/tasks endpoint.
 */
export interface TaskListResponse {
  tasks: Task[]
}
