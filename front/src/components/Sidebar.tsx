'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useCallback, useEffect, useState } from 'react'
import { Plus, Settings, MessageSquare, FolderOpen, Upload, Trash2 } from 'lucide-react'

import { ThemeToggle } from '@/components/ThemeToggle'
import { ConfirmModal } from '@/components/ui/Modal'
import {
  CHATS_UPDATED_EVENT,
  deleteChat,
  getCachedChatList,
  listChats,
  type ChatSummaryResponse,
} from '@/lib/api'

const knowledgeBase = [
  { name: 'Files', href: '/files', icon: FolderOpen },
  { name: 'Upload files', href: '/upload', icon: Upload },
]

function chatHref(id: string) {
  return `/chat/${id}`
}

function isChatActive(pathname: string, chatId: string) {
  return pathname === chatHref(chatId)
}

export default function Sidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const [chats, setChats] = useState<ChatSummaryResponse[]>([])
  const [isLoadingChats, setIsLoadingChats] = useState(true)
  const [chatsError, setChatsError] = useState(false)
  const [pendingDeleteChat, setPendingDeleteChat] =
    useState<ChatSummaryResponse | null>(null)
  const [isDeletingChat, setIsDeletingChat] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const loadChats = useCallback(async (force = false) => {
    setChatsError(false)

    if (!force) {
      const cached = getCachedChatList()
      if (cached) {
        setChats(cached)
        setIsLoadingChats(false)
        return
      }
    }

    setIsLoadingChats(true)
    try {
      const items = await listChats({ force: true })
      setChats(items)
    } catch {
      setChatsError(true)
    } finally {
      setIsLoadingChats(false)
    }
  }, [])

  useEffect(() => {
    void loadChats()
    const onChatsUpdated = () => {
      void loadChats(true)
    }
    window.addEventListener(CHATS_UPDATED_EVENT, onChatsUpdated)
    return () => window.removeEventListener(CHATS_UPDATED_EVENT, onChatsUpdated)
  }, [loadChats])

  const handleCloseDeleteConfirm = useCallback(() => {
    if (isDeletingChat) return
    setPendingDeleteChat(null)
    setDeleteError(null)
  }, [isDeletingChat])

  const handleConfirmDeleteChat = useCallback(async () => {
    if (!pendingDeleteChat) return

    const chatId = pendingDeleteChat.id
    const wasActive = isChatActive(pathname, chatId)
    setIsDeletingChat(true)
    setDeleteError(null)

    try {
      await deleteChat(chatId)
      setPendingDeleteChat(null)
      if (wasActive) {
        router.push('/chat/new')
      }
    } catch {
      setDeleteError('Could not delete the chat. Try again.')
    } finally {
      setIsDeletingChat(false)
    }
  }, [pendingDeleteChat, pathname, router])

  return (
    <aside className="w-56 bg-sidebar-bg text-sidebar-text flex flex-col h-screen shrink-0">
      <ConfirmModal
        open={pendingDeleteChat !== null}
        onClose={handleCloseDeleteConfirm}
        onConfirm={handleConfirmDeleteChat}
        title="Delete chat?"
        description={
          <>
            <p>
              This will permanently delete{' '}
              <span className="font-medium text-text-primary">
                {pendingDeleteChat?.title ?? 'this chat'}
              </span>{' '}
              and all of its messages. This cannot be undone.
            </p>
            {deleteError ? (
              <p className="mt-3 text-error">{deleteError}</p>
            ) : null}
          </>
        }
        confirmLabel="Delete"
        confirmVariant="danger"
        isLoading={isDeletingChat}
      />

      <div className="p-5 pb-4">
        <h1 className="text-xl font-bold text-white tracking-tight">Knowforge</h1>
      </div>

      <div className="px-4 mb-6">
        <Link
          href="/chat/new"
          className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-primary hover:bg-primary-hover text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          New Chat
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto px-2">
        <div className="mb-6">
          <p className="px-3 mb-1.5 text-xs font-semibold uppercase tracking-wider text-sidebar-text/60">
            Chats
          </p>
          {isLoadingChats ? (
            <p className="px-3 py-2 text-xs text-sidebar-text/50">Loading…</p>
          ) : chatsError ? (
            <p className="px-3 py-2 text-xs text-sidebar-text/50">Could not load chats</p>
          ) : chats.length === 0 ? (
            <p className="px-3 py-2 text-xs text-sidebar-text/50">No chats yet</p>
          ) : (
            chats.map((chat) => {
              const href = chatHref(chat.id)
              const active = isChatActive(pathname, chat.id)
              return (
                <div
                  key={chat.id}
                  className={`group flex items-center gap-1 rounded-lg pr-1 transition-colors min-w-0 ${
                    active
                      ? 'bg-sidebar-active text-white'
                      : 'hover:bg-sidebar-active/50 text-sidebar-text'
                  }`}
                >
                  <Link
                    href={href}
                    title={chat.title}
                    className="flex min-w-0 flex-1 items-center gap-2.5 px-3 py-2 text-sm"
                  >
                    <MessageSquare size={14} className="opacity-60 shrink-0" />
                    <span className="truncate">{chat.title}</span>
                  </Link>
                  <button
                    type="button"
                    aria-label={`Delete chat ${chat.title}`}
                    title="Delete chat"
                    onClick={(event) => {
                      event.preventDefault()
                      event.stopPropagation()
                      setDeleteError(null)
                      setPendingDeleteChat(chat)
                    }}
                    className={`shrink-0 rounded-md p-1.5 transition-opacity hover:bg-white/10 ${
                      active
                        ? 'opacity-70 hover:opacity-100'
                        : 'opacity-0 group-hover:opacity-70 group-focus-within:opacity-70 hover:opacity-100'
                    }`}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              )
            })
          )}
        </div>

        <div>
          <p className="px-3 mb-1.5 text-xs font-semibold uppercase tracking-wider text-sidebar-text/60">
            Knowledge Base
          </p>
          {knowledgeBase.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                  pathname === item.href
                    ? 'bg-sidebar-active text-white'
                    : 'hover:bg-sidebar-active/50 text-sidebar-text'
                }`}
              >
                <Icon size={14} className="opacity-60" />
                {item.name}
              </Link>
            )
          })}
        </div>
      </nav>

      <div className="space-y-1 border-t border-white/10 p-4">
        <ThemeToggle />
        <Link
          href="/settings"
          className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-sidebar-text transition-colors hover:bg-sidebar-active/50"
        >
          <Settings size={14} className="opacity-60" />
          Settings
        </Link>
      </div>
    </aside>
  )
}
