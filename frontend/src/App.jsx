import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Chat from './components/Chat'
import Login from './components/Login'
import Signup from './components/Signup'
import { AuthProvider } from './context/AuthContext'
import { ChatProvider } from './context/ChatContext'

export default function App() {
  return (
    <AuthProvider>
      <ChatProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Chat/>} />
            <Route path="/login" element={<Login/>} />
            <Route path="/signup" element={<Signup/>} />
          </Routes>
        </BrowserRouter>
      </ChatProvider>
    </AuthProvider>
  )
}
