import React, { createContext, useState } from 'react'

export const ChatContext = createContext({ messages: [], addMessage: () => {} })

export function ChatProvider({ children }){
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi! I\'m CookBot. Tell me what you\'d like to cook or your dietary preferences.' }
  ])
  function addMessage(msg){ setMessages(m => [...m, msg]) }
  return (
    <ChatContext.Provider value={{ messages, addMessage }}>{children}</ChatContext.Provider>
  )
}
