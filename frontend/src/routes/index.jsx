import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Landing from '@/pages/Landing'

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
    </Routes>
  )
}
