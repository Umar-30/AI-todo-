import { TaskCard } from './TaskCard'
import type { Task } from '../types/task'

interface TaskSidebarProps {
  tasks: Task[]
  isLoading: boolean
  error: string | null
  onRefresh: () => void
  /** Whether real-time updates are connected */
  isLive?: boolean
}

/**
 * TaskSidebar component displays the task list in a fixed sidebar for the split layout.
 * Shows a live indicator when real-time updates are connected.
 */
export function TaskSidebar({
  tasks,
  isLoading,
  error,
  onRefresh,
  isLive = false,
}: TaskSidebarProps) {
  return (
    <aside className="task-sidebar" aria-label="Task list sidebar">
      <header className="task-sidebar-header">
        <h2 id="task-sidebar-title">
          My Tasks
          {isLive && (
            <span
              className="live-indicator"
              title="Real-time updates active"
              aria-label="Real-time updates active"
            >
              <span className="live-dot"></span>
              LIVE
            </span>
          )}
        </h2>
      </header>

      <div
        className="task-sidebar-content"
        role="list"
        aria-labelledby="task-sidebar-title"
        aria-busy={isLoading}
      >
        {isLoading && (
          <div className="task-sidebar-loading" role="status" aria-live="polite">
            Loading tasks...
          </div>
        )}

        {error && (
          <div className="task-sidebar-error" role="alert">
            {error}
            <button
              onClick={onRefresh}
              className="task-sidebar-retry"
              aria-label="Retry loading tasks"
            >
              Retry
            </button>
          </div>
        )}

        {!isLoading && !error && tasks.length === 0 && (
          <div className="task-sidebar-empty" role="status">
            No tasks yet. Use the chat to add tasks!
          </div>
        )}

        {!isLoading &&
          !error &&
          tasks.map((task) => (
            <TaskCard key={task.id} task={task} onTaskUpdated={onRefresh} />
          ))}
      </div>
    </aside>
  )
}
