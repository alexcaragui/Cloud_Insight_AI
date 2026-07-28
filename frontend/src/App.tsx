import { createBrowserRouter, RouterProvider } from 'react-router-dom'

import Layout from './components/layout/Layout'
import { AuthGuard } from './components/guards/AuthGuard'
import Dashboard from './pages/Dashboard'
import Upload from './pages/Upload'
import Chat from './pages/Chat'
import Reports from './pages/Reports'
import Login from './pages/Login'
import Models from './pages/Models'

const router = createBrowserRouter([
  {
    path: '/login',
    element: <Login />,
  },
  {
    element: <AuthGuard />,
    children: [
      {
        path: '/',
        element: <Layout />,
        children: [
          { index: true, element: <Dashboard /> },
          { path: 'upload', element: <Upload /> },
          { path: 'chat', element: <Chat /> },
          { path: 'models', element: <Models /> },
          { path: 'reports', element: <Reports /> },
        ],
      },
    ],
  },
])

function App() {
  return <RouterProvider router={router} />
}

export default App
