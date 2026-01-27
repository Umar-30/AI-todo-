import type { ReactNode } from 'react'

interface LayoutProps {
  chatArea: ReactNode
  sidebar: ReactNode
}

/**
 * Layout component provides the 70/30 grid split between chat and sidebar.
 */
export function Layout({ chatArea, sidebar }: LayoutProps) {
  return (
    <div className="app-layout">
      <div className="chat-area">{chatArea}</div>
      {sidebar}
    </div>
  )
}
