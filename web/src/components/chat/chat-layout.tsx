'use client'

import { useState } from 'react'
import { ConversationList } from './conversation-list'
import { ConversationView } from './conversation-view'

export function ChatLayout() {
  const [showConversationView, setShowConversationView] = useState(false)

  return (
    <div className="flex h-[calc(100vh-theme(spacing.16))] gap-4">
      {/* Conversation List - hidden on mobile when viewing conversation */}
      <div
        className={`
          w-full md:w-[300px] md:shrink-0
          ${showConversationView ? 'hidden md:block' : 'block'}
        `}
      >
        <ConversationList
          onSelectConversation={() => setShowConversationView(true)}
        />
      </div>

      {/* Conversation View - full width on mobile, flex-1 on desktop */}
      <div
        className={`
          flex-1
          ${showConversationView ? 'block' : 'hidden md:block'}
        `}
      >
        <ConversationView
          onBack={() => setShowConversationView(false)}
          showBackButton={showConversationView}
        />
      </div>
    </div>
  )
}
