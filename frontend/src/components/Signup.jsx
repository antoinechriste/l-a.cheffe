import React, { useState, useContext } from 'react'
import axios from 'axios'
import { useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'

export default function Signup(){
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const { setToken } = useContext(AuthContext)
  const nav = useNavigate()

  async function submit(){
    try{
      const res = await axios.post('/api/auth/signup', { username, password })
      setToken(res.data.token)
      nav('/')
    }catch(e){
      alert('Signup failed: ' + (e.response?.data?.error || e.message))
    }
  }

  return (
    <div className="login-panel">
      <h2>Sign up</h2>
      <input placeholder="username" value={username} onChange={e=>setUsername(e.target.value)} />
      <input placeholder="password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      <button onClick={submit}>Create account</button>
    </div>
  )
}
