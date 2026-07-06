import { createBrowserRouter, RouterProvider } from 'react-router-dom';

// Importăm paginile
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Chat from './pages/Chat';
import Reports from './pages/Reports';
import Login from './pages/Login';

// Definim rutele
const router = createBrowserRouter([
  {
    path: "/",
    element: <Dashboard />,
  },
  {
    path: "/upload",
    element: <Upload />,
  },
  {
    path: "/chat",
    element: <Chat />,
  },
  {
    path: "/reports",
    element: <Reports />,
  },
  {
    path: "/login",
    element: <Login />,
  },
]);

// Componenta principală care randează router-ul
function App() {
  return <RouterProvider router={router} />;
}

export default App;