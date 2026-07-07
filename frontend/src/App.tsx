/* eslint-disable @typescript-eslint/no-unused-vars */
import { Admin, CustomRoutes } from 'react-admin';
import simpleRestProvider from 'ra-data-simple-rest';
import { Route } from 'react-router-dom';

// Importăm paginile custom (asigură-te că le ai create în src/pages/)
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Chat from './pages/Chat';
import Reports from './pages/Reports';

// Definim cum va comunica frontend-ul cu backend-ul tău FastAPI
// Deocamdată punem URL-ul de bază unde va rula backend-ul
const dataProvider = simpleRestProvider('http://localhost:8000/api');

function App() {
  return (
    <Admin dataProvider={dataProvider} dashboard={Dashboard}>
      {/* Aici punem paginile care NU sunt tabele standard (ex: Chat, Upload) */}
      {/* <CustomRoutes>
        <Route path="/upload" element={<Upload />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/reports" element={<Reports />} />
      </CustomRoutes> */}
      
      {/* Mai târziu, când backend-ul va returna lista de rapoarte, 
          vom adăuga aici o linie de genul:
          <Resource name="reports" list={ReportList} /> 
      */}
    </Admin>
  );
}

export default App;