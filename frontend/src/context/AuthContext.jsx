import React, { createContext, useState } from 'react'

export const AuthContext = createContext({ token: null, setToken: () => {} })

export function AuthProvider({ children }){
  const [token, setToken] = useState(localStorage.getItem('cookbot_token'))
  function setAndStore(t){
    if(t) localStorage.setItem('cookbot_token', t)
    else localStorage.removeItem('cookbot_token')
    setToken(t)
  }
  return (
    <AuthContext.Provider value={{ token, setToken: setAndStore }}>{children}</AuthContext.Provider>
  )
}
