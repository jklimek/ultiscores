"""WebSocket connection manager for live match updates."""
import asyncio
import json
from typing import Dict, Set, Optional
from fastapi import WebSocket
from datetime import datetime


class ConnectionManager:
    """Manage WebSocket connections for live match updates."""
    
    def __init__(self):
        """Initialize connection manager."""
        # match_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.heartbeat_interval = 30  # seconds
        
    async def connect(self, websocket: WebSocket, match_id: str):
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            match_id: Match ID to subscribe to
        """
        await websocket.accept()
        
        if match_id not in self.active_connections:
            self.active_connections[match_id] = set()
        
        self.active_connections[match_id].add(websocket)
        
        # Send connection acknowledgment
        await self.send_personal_message(
            {
                "type": "connection_ack",
                "match_id": match_id,
                "heartbeat_interval": self.heartbeat_interval * 1000,  # ms
                "timestamp": datetime.utcnow().isoformat(),
            },
            websocket
        )
    
    def disconnect(self, websocket: WebSocket, match_id: str):
        """
        Remove a WebSocket connection.
        
        Args:
            websocket: WebSocket connection
            match_id: Match ID
        """
        if match_id in self.active_connections:
            self.active_connections[match_id].discard(websocket)
            
            # Clean up empty match subscriptions
            if not self.active_connections[match_id]:
                del self.active_connections[match_id]
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send message to a specific connection.
        
        Args:
            message: Message dictionary
            websocket: Target WebSocket
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message: {e}")
    
    async def broadcast(self, message: dict, match_id: str):
        """
        Broadcast message to all connections subscribed to a match.
        
        Args:
            message: Message dictionary
            match_id: Match ID
        """
        if match_id not in self.active_connections:
            return
        
        # Add timestamp to message
        message["timestamp"] = datetime.utcnow().isoformat()
        
        # Send to all connected clients
        disconnected = set()
        for connection in self.active_connections[match_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection, match_id)
    
    async def broadcast_match_snapshot(self, match_data: dict, match_id: str):
        """
        Broadcast full match state snapshot.
        
        Args:
            match_data: Full match data
            match_id: Match ID
        """
        await self.broadcast(
            {
                "type": "match_snapshot",
                "match": match_data,
            },
            match_id
        )
    
    async def broadcast_score_update(
        self, match_id: str, home_score: int, away_score: int, status: str
    ):
        """
        Broadcast score update.
        
        Args:
            match_id: Match ID
            home_score: Home team score
            away_score: Away team score
            status: Match status
        """
        await self.broadcast(
            {
                "type": "score_update",
                "match_id": match_id,
                "home_score": home_score,
                "away_score": away_score,
                "status": status,
            },
            match_id
        )
    
    async def broadcast_event_created(self, match_id: str, event: dict):
        """
        Broadcast new match event.
        
        Args:
            match_id: Match ID
            event: Event data
        """
        await self.broadcast(
            {
                "type": "event_created",
                "match_id": match_id,
                "event": event,
            },
            match_id
        )
    
    async def broadcast_timeout_taken(
        self, match_id: str, team_id: str, timeouts_remaining: int
    ):
        """
        Broadcast timeout update.
        
        Args:
            match_id: Match ID
            team_id: Team ID
            timeouts_remaining: Timeouts remaining
        """
        await self.broadcast(
            {
                "type": "timeout_taken",
                "match_id": match_id,
                "team_id": team_id,
                "timeouts_remaining": timeouts_remaining,
            },
            match_id
        )
    
    async def broadcast_spirit_updated(self, match_id: str, spirit_data: dict):
        """
        Broadcast spirit score update.
        
        Args:
            match_id: Match ID
            spirit_data: Spirit score data
        """
        await self.broadcast(
            {
                "type": "spirit_updated",
                "match_id": match_id,
                "spirit": spirit_data,
            },
            match_id
        )
    
    async def broadcast_error(self, match_id: str, error: str, fatal: bool = False):
        """
        Broadcast error message.
        
        Args:
            match_id: Match ID
            error: Error message
            fatal: Whether error is fatal (should disconnect)
        """
        await self.broadcast(
            {
                "type": "error",
                "error": error,
                "fatal": fatal,
            },
            match_id
        )
    
    def get_connection_count(self, match_id: str) -> int:
        """
        Get number of active connections for a match.
        
        Args:
            match_id: Match ID
            
        Returns:
            Connection count
        """
        return len(self.active_connections.get(match_id, set()))
    
    def get_all_match_ids(self) -> Set[str]:
        """Get set of all match IDs with active connections."""
        return set(self.active_connections.keys())


# Global connection manager instance
manager = ConnectionManager()

