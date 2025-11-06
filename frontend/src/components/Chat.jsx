import React, { useState, useContext } from 'react'
import axios from 'axios'
import { AuthContext } from '../context/AuthContext'
import { ChatContext } from '../context/ChatContext'

export default function Chat(){
  const { token } = useContext(AuthContext)
  const { messages, addMessage } = useContext(ChatContext)
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)

  async function send(){
    if(!text) return
    addMessage({ role: 'user', content: text })
    setLoading(true)
    try{
      const res = await axios.post('/api/chat/query', { query: text }, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
      if (res.data && res.data.result){
        addMessage({ role: 'assistant', content: res.data.result })
      } else {
        addMessage({ role: 'assistant', content: 'Sorry, no response.' })
      }
    }catch(e){
      addMessage({ role: 'assistant', content: 'Error: ' + (e.response?.data?.error || e.message) })
    }finally{ setLoading(false); setText('') }
  }

  return (
    <div className="app">
      <div className="header">CookBot — your cooking assistant</div>
      <div className="chat-window">
        {messages.map((m,i)=> (
          <div key={i} className={`message ${m.role}`}>
            <div className="bubble">{m.content}</div>
          </div>
        ))}
      </div>
      <div className="input-area">
        <input type="text" value={text} onChange={e=>setText(e.target.value)} placeholder={loading ? 'Thinking...' : 'Ask for a recipe or meal plan...'} />
        <button onClick={send} disabled={loading}>{loading ? '...' : 'Send'}</button>
      </div>
    </div>
  )
}
