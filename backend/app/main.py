from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

app = FastAPI(title="CloudInsight-AI Data Ingestion API")

# --- 1. CONFIGURARE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. GESTIONAR PENTRU WEBSOCKETS ---
# Aici ținem minte cine este conectat, pentru a ști cui trimitem mesajele
class ConnectionManager:
    def __init__(self):
        # Un dicționar care asociază un client_id cu conexiunea lui
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)

manager = ConnectionManager()

# Bază de date falsă pentru a stoca rezultatele procesării
fake_database = {}

# Schema datelor pe care le așteptăm de la Frontend
class DataInput(BaseModel):
    client_id: str
    data_payload: str

# --- 3. FUNCȚIA DE PROCESARE (Simulare) ---
# Aceasta va rula în fundal (background) ca să nu blocheze endpoint-ul
async def process_data_in_background(client_id: str, data: str):
    # Simulăm prima parte a procesării
    await asyncio.sleep(2)
    await manager.send_message("Status: Am început procesarea datelor...", client_id)
    
    # Simulăm partea a doua a procesării
    await asyncio.sleep(3)
    await manager.send_message("Status: Procesare la 80%...", client_id)
    
    # Finalizăm procesarea
    await asyncio.sleep(1)
    fake_database[client_id] = f"SUCCES: Datele '{data}' au fost transformate!"
    
    # Trimitem semnalul final către Frontend să își ia datele
    await manager.send_message("CALL_OUTPUT_ENDPOINT", client_id)


# --- 4. CELE 3 ENDPOINT-URI CERUTE DE MENTOR ---

# Endpoint 1: INPUT
@app.post("/api/data-ingestion")
async def data_ingestion(payload: DataInput, background_tasks: BackgroundTasks):
    """FE cheamă asta pentru a trimite datele."""
    # Adăugăm task-ul în fundal. Funcția returnează instant un răspuns către FE.
    background_tasks.add_task(process_data_in_background, payload.client_id, payload.data_payload)
    return {"status": "accepted", "message": "Datele au intrat în procesare."}


# Endpoint 2: CHANNEL-LISTENER (WebSocket)
@app.websocket("/api/data-ingestion-listener/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """FE se conectează aici pentru a asculta actualizări."""
    await manager.connect(websocket, client_id)
    try:
        # Menținem conexiunea deschisă și ascultăm dacă FE trimite ceva
        while True:
            data = await websocket.receive_text()
            # Aici am putea răspunde înapoi dacă FE trimite mesaje pe WebSocket
    except WebSocketDisconnect:
        manager.disconnect(client_id)


# Endpoint 3: OUTPUT
@app.get("/api/data-ingestion-response/{client_id}")
async def data_ingestion_response(client_id: str):
    """FE cheamă asta după ce a primit semnalul pe WebSocket."""
    result = fake_database.get(client_id)
    if result:
        # Curățăm "baza de date" după ce am livrat rezultatul (opțional)
        del fake_database[client_id]
        return {"status": "completed", "final_data": result}
    
    return {"status": "pending", "message": "Datele nu sunt gata încă."}