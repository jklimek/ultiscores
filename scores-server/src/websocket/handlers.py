"""WebSocket endpoint handlers."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.websocket.manager import manager
from src.models import Match
from sqlalchemy import select

router = APIRouter()


@router.websocket("/ws/matches/{match_id}")
async def websocket_match_endpoint(
    websocket: WebSocket,
    match_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for live match updates.
    
    Args:
        websocket: WebSocket connection
        match_id: Match ID to subscribe to
        db: Database session
    """
    # Connect client
    await manager.connect(websocket, match_id)
    
    try:
        # Send initial match snapshot
        result = await db.execute(
            select(Match).where(Match.id == match_id)
        )
        match = result.scalar_one_or_none()
        
        if match:
            match_data = {
                "id": match.id,
                "status": match.status,
                "home_score": match.home_score,
                "away_score": match.away_score,
                "home_team_id": match.home_team_id,
                "away_team_id": match.away_team_id,
                "home_timeouts": match.home_timeouts,
                "away_timeouts": match.away_timeouts,
                "start_time": match.start_time,
                "round": match.round,
            }
            await manager.broadcast_match_snapshot(match_data, match_id)
        
        # Keep connection alive and handle messages
        while True:
            # Wait for messages from client (heartbeat, etc.)
            try:
                data = await websocket.receive_json()
                
                # Handle client heartbeat
                if data.get("type") == "heartbeat":
                    await manager.send_personal_message(
                        {"type": "heartbeat_ack"},
                        websocket
                    )
                
                # Additional client message handling can be added here
                
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, match_id)
        print(f"Client disconnected from match {match_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, match_id)

