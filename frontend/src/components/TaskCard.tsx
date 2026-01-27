import { useState } from 'react'
import type { Task } from '../types/task'
import { completeTask, uncompleteTask, deleteTask } from '../services/api'

interface TaskCardProps {
  task: Task
  onTaskUpdated?: () => void
}

/**
 * Formats a date string for display.
 */
function formatDueDate(dateStr: string | null): string | null {
  if (!dateStr) return null
  try {
    const date = new Date(dateStr)
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return null
  }
}

/**
 * Checks if a date is overdue.
 */
function isOverdue(dateStr: string | null): boolean {
  if (!dateStr) return false
  try {
    const date = new Date(dateStr)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    return date < today
  } catch {
    return false
  }
}

/**
 * TaskCard component displays a single task with its details and action buttons.
 */
export function TaskCard({ task, onTaskUpdated }: TaskCardProps) {
  const [isLoading, setIsLoading] = useState(false)
  const formattedDueDate = formatDueDate(task.due_date)
  const overdue = !task.completed && isOverdue(task.due_date)

  const handleToggleComplete = async () => {
    setIsLoading(true)
    try {
      if (task.completed) {
        await uncompleteTask(task.id)
      } else {
        await completeTask(task.id)
      }
      onTaskUpdated?.()
    } catch (error) {
      console.error('Failed to update task:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) return

    setIsLoading(true)
    try {
      await deleteTask(task.id)
      onTaskUpdated?.()
    } catch (error) {
      console.error('Failed to delete task:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <article
      className={`task-card ${task.completed ? 'task-card-completed' : ''} ${isLoading ? 'task-card-loading' : ''}`}
      role="listitem"
      aria-label={`Task: ${task.title}${task.completed ? ', completed' : ', pending'}`}
    >
      <div className="task-card-header">
        <div className="task-card-title">{task.title}</div>
        <div className="task-card-actions">
          <button
            className={`task-action-btn ${task.completed ? 'task-action-undo' : 'task-action-complete'}`}
            onClick={handleToggleComplete}
            disabled={isLoading}
            title={task.completed ? 'Mark as pending' : 'Mark as done'}
          >
            {task.completed ? '↩' : '✓'}
          </button>
          <button
            className="task-action-btn task-action-delete"
            onClick={handleDelete}
            disabled={isLoading}
            title="Delete task"
          >
            ✕
          </button>
        </div>
      </div>

      {task.description && (
        <div className="task-card-description">{task.description}</div>
      )}

      <div className="task-card-meta">
        {/* Status indicator */}
        <span
          className={`task-card-status ${
            task.completed
              ? 'task-card-status-completed'
              : 'task-card-status-pending'
          }`}
        >
          <span className="task-card-status-icon" />
          {task.completed ? 'Done' : 'Pending'}
        </span>

        {/* Priority badge */}
        {task.priority && (
          <span
            className={`task-card-badge task-card-badge-priority-${task.priority}`}
          >
            {task.priority}
          </span>
        )}

        {/* Category badge */}
        {task.category && (
          <span className="task-card-badge task-card-badge-category">
            {task.category}
          </span>
        )}

        {/* Due date */}
        {formattedDueDate && (
          <span
            className={`task-card-badge task-card-badge-due ${
              overdue ? 'task-card-badge-overdue' : ''
            }`}
          >
            {overdue ? 'Overdue: ' : ''}
            {formattedDueDate}
          </span>
        )}
      </div>
    </article>
  )
}
