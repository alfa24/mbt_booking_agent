'use client'

import { ConversationView } from './conversation-view'

export function ChatLayout() {
  return (
    <div className="flex h-[calc(100vh-theme(spacing.16))]">
      <ConversationView />
    </div>
  )
}
