import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
)

// Gracefully fade out and remove the HTML pre-loader
const preloader = document.getElementById('app-loading')
if (preloader) {
  preloader.style.opacity = '0'
  setTimeout(() => preloader.remove(), 300)
}

