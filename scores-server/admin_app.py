"""Streamlit Admin App for Scores Server.

This app provides:
- Database preview (view all tables)
- Tournament creation with full form
- Basic authentication
"""
import streamlit as st
import sqlite3
import pandas as pd
import uuid
import json
from datetime import datetime, date
from typing import Dict, Any, List
import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# Import database and models
from src.database import AsyncSessionLocal
from src.models import (
    Season, Team, Venue, Tournament, Stage, Pool, Match,
    Player, TournamentRoster, MatchEvent, PlayerStats, TeamStats, SpiritScore
)
from src.services.tournament_generator import generate_tournament_structure

# Page config
st.set_page_config(
    page_title="Scores Server Admin",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication credentials (in production, use environment variables)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"


def check_auth(username: str, password: str) -> bool:
    """Check if username and password are correct."""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def login_form():
    """Display login form."""
    st.title("🏆 Scores Server Admin")
    st.subheader("Please log in to continue")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Log in")
        
        if submit:
            if check_auth(username, password):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid username or password")


def logout():
    """Log out the user."""
    st.session_state.authenticated = False
    st.rerun()


# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


# Main app
def main():
    """Main application."""
    if not st.session_state.authenticated:
        login_form()
        return
    
    # Sidebar
    with st.sidebar:
        st.title("🏆 Admin Panel")
        st.write(f"Logged in as: **{ADMIN_USERNAME}**")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
        
        st.divider()
        
        page = st.radio(
            "Navigation",
            ["📊 Database Preview", "➕ Create Tournament"],
            label_visibility="collapsed"
        )
    
    # Main content
    if page == "📊 Database Preview":
        show_database_preview()
    elif page == "➕ Create Tournament":
        show_tournament_creator()


def get_db_connection():
    """Get SQLite database connection for preview."""
    return sqlite3.connect("scores.db")


def show_database_preview():
    """Show database tables and their contents."""
    st.title("📊 Database Preview")
    st.write("View all tables and their contents in the database.")
    
    # Get all tables
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cursor.fetchall()]
    
    if not tables:
        st.warning("No tables found in the database.")
        conn.close()
        return
    
    # Table selector
    selected_table = st.selectbox("Select a table to view:", tables)
    
    if selected_table:
        st.subheader(f"Table: `{selected_table}`")
        
        # Get row count
        count_query = f"SELECT COUNT(*) FROM {selected_table}"
        cursor.execute(count_query)
        row_count = cursor.fetchone()[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Rows", row_count)
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({selected_table})")
        schema = cursor.fetchall()
        
        with col2:
            st.metric("Total Columns", len(schema))
        
        # Show schema
        with st.expander("📋 Table Schema"):
            schema_df = pd.DataFrame(
                schema,
                columns=["ID", "Name", "Type", "NotNull", "DefaultValue", "PK"]
            )
            st.dataframe(schema_df, use_container_width=True)
        
        # Show data
        if row_count > 0:
            st.subheader("Data")
            
            # Pagination
            page_size = st.slider("Rows per page", 10, 100, 50)
            page_num = st.number_input("Page", min_value=1, max_value=max(1, (row_count + page_size - 1) // page_size), value=1)
            offset = (page_num - 1) * page_size
            
            # Query data
            query = f"SELECT * FROM {selected_table} LIMIT {page_size} OFFSET {offset}"
            df = pd.read_sql_query(query, conn)
            
            st.dataframe(df, use_container_width=True, height=400)
            
            # Export option
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f"{selected_table}.csv",
                mime="text/csv"
            )
        else:
            st.info("No data in this table.")
    
    conn.close()


def show_tournament_creator():
    """Show tournament creation form."""
    st.title("➕ Create Tournament")
    st.write("Create a new tournament with all settings and generate matches.")
    
    # Load data for dropdowns
    conn = get_db_connection()
    
    # Get seasons
    seasons_df = pd.read_sql_query("SELECT id, label, year FROM seasons ORDER BY year DESC", conn)
    if seasons_df.empty:
        st.error("No seasons found. Please create a season first.")
        conn.close()
        return
    
    # Get venues
    venues_df = pd.read_sql_query("SELECT id, name, city FROM venues", conn)
    if venues_df.empty:
        st.error("No venues found. Please create a venue first.")
        conn.close()
        return
    
    # Get teams
    teams_df = pd.read_sql_query("SELECT id, name, division FROM teams ORDER BY name", conn)
    if teams_df.empty:
        st.error("No teams found. Please create teams first.")
        conn.close()
        return
    
    conn.close()
    
    # Tournament creation form
    with st.form("tournament_form"):
        st.subheader("Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Tournament Name *", placeholder="e.g., Mistrzostwa Polski Mixed 2025")
            slug = st.text_input("Slug *", placeholder="e.g., mp-mixed-2025")
            
            # Season selector
            season_options = {f"{row['label']} ({row['year']})": row['id'] for _, row in seasons_df.iterrows()}
            selected_season = st.selectbox("Season *", options=list(season_options.keys()))
            season_id = season_options[selected_season]
            
            division = st.selectbox(
                "Division *",
                ["mixed", "open", "women", "junior", "masters"]
            )
        
        with col2:
            start_date = st.date_input("Start Date *", value=date.today())
            end_date = st.date_input("End Date *", value=date.today())
            
            # Venue selector
            venue_options = {f"{row['name']} ({row['city']})": row['id'] for _, row in venues_df.iterrows()}
            selected_venue = st.selectbox("Venue *", options=list(venue_options.keys()))
            venue_id = venue_options[selected_venue]
            
            status = st.selectbox(
                "Status",
                ["upcoming", "in_progress", "completed", "cancelled"]
            )
        
        st.divider()
        st.subheader("Tournament Settings")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            format_type = st.selectbox(
                "Format *",
                ["power_pools", "pool", "swiss", "single_elim", "double_elim"],
                help="Tournament format type"
            )
            
            pool_count = st.number_input(
                "Pool Count",
                min_value=1,
                max_value=10,
                value=2,
                help="Number of pools (for pool formats)"
            )
            
            rest_periods = st.number_input(
                "Rest Periods",
                min_value=0,
                max_value=5,
                value=1,
                help="Minimum matches between games for a team"
            )
        
        with col2:
            match_duration = st.number_input(
                "Match Duration (minutes)",
                min_value=30,
                max_value=120,
                value=75
            )
            
            field_count = st.number_input(
                "Number of Fields",
                min_value=1,
                max_value=10,
                value=2
            )
            
            cap_at = st.number_input(
                "Point Cap",
                min_value=10,
                max_value=20,
                value=15,
                help="Game ends when a team reaches this score"
            )
        
        with col3:
            soft_cap_minutes = st.number_input(
                "Soft Cap (minutes)",
                min_value=60,
                max_value=120,
                value=90,
                help="Time when soft cap is triggered"
            )
            
            hard_cap_minutes = st.number_input(
                "Hard Cap (minutes)",
                min_value=90,
                max_value=150,
                value=110,
                help="Time when hard cap is triggered"
            )
            
            power_pool_size = st.number_input(
                "Power Pool Size",
                min_value=2,
                max_value=8,
                value=4,
                help="Number of teams advancing to championship pool"
            )
        
        st.divider()
        st.subheader("Organiser Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            org_name = st.text_input("Organiser Name", placeholder="e.g., PSGU")
            org_website = st.text_input("Website", placeholder="https://...")
        
        with col2:
            org_email = st.text_input("Contact Email", placeholder="contact@example.com")
        
        st.divider()
        st.subheader("Select Teams")
        
        # Filter teams by division
        division_teams = teams_df[teams_df['division'] == division]
        
        if division_teams.empty:
            st.warning(f"No teams found for division: {division}")
            selected_teams = []
        else:
            team_options = {row['name']: row['id'] for _, row in division_teams.iterrows()}
            selected_team_names = st.multiselect(
                "Teams *",
                options=list(team_options.keys()),
                help="Select teams participating in the tournament"
            )
            selected_teams = [team_options[name] for name in selected_team_names]
        
        # Seeding
        st.write("**Team Seeding**")
        if selected_teams:
            st.info(f"Selected {len(selected_teams)} teams. Assign seeds (1 = highest).")
            
            seeds = {}
            cols = st.columns(3)
            for idx, team_name in enumerate(selected_team_names):
                with cols[idx % 3]:
                    seed = st.number_input(
                        f"{team_name}",
                        min_value=1,
                        max_value=len(selected_teams),
                        value=idx + 1,
                        key=f"seed_{team_options[team_name]}"
                    )
                    seeds[team_options[team_name]] = seed
        
        st.divider()
        
        # Submit button
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            submit = st.form_submit_button("🚀 Create Tournament", use_container_width=True, type="primary")
        
        if submit:
            # Validate
            if not name or not slug:
                st.error("Please fill in all required fields (marked with *).")
                return
            
            if len(selected_teams) < 2:
                st.error("Please select at least 2 teams.")
                return
            
            # Check for duplicate seeds
            seed_values = list(seeds.values())
            if len(seed_values) != len(set(seed_values)):
                st.error("Each team must have a unique seed.")
                return
            
            # Create tournament
            with st.spinner("Creating tournament..."):
                try:
                    # Prepare tournament data
                    tournament_id = str(uuid.uuid4())
                    
                    settings = {
                        "format": format_type,
                        "pool_count": pool_count,
                        "rest_periods": rest_periods,
                        "match_duration_minutes": match_duration,
                        "field_count": field_count,
                        "cap_at": cap_at,
                        "soft_cap_minutes": soft_cap_minutes,
                        "hard_cap_minutes": hard_cap_minutes,
                        "advancement": {
                            "power_pool_size": power_pool_size
                        }
                    }
                    
                    organiser = {
                        "name": org_name,
                        "website": org_website,
                        "contactEmail": org_email
                    }
                    
                    teams_data = [
                        {"teamId": team_id, "seed": seeds[team_id]}
                        for team_id in selected_teams
                    ]
                    
                    # Create tournament using async
                    result = asyncio.run(create_tournament_async(
                        tournament_id=tournament_id,
                        slug=slug,
                        name=name,
                        season_id=season_id,
                        division=division,
                        start_date=start_date.isoformat(),
                        end_date=end_date.isoformat(),
                        status=status,
                        venue_id=venue_id,
                        settings=settings,
                        organiser=organiser,
                        teams=teams_data
                    ))
                    
                    st.success(f"✅ Tournament '{name}' created successfully!")
                    st.success(f"Generated {result['matches_count']} matches across {result['stages_count']} stages.")
                    
                    # Show summary
                    with st.expander("📋 Tournament Summary"):
                        st.json({
                            "id": tournament_id,
                            "name": name,
                            "teams": len(selected_teams),
                            "stages": result['stages_count'],
                            "pools": result['pools_count'],
                            "matches": result['matches_count']
                        })
                
                except Exception as e:
                    st.error(f"Error creating tournament: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())


async def create_tournament_async(
    tournament_id: str,
    slug: str,
    name: str,
    season_id: str,
    division: str,
    start_date: str,
    end_date: str,
    status: str,
    venue_id: str,
    settings: Dict[str, Any],
    organiser: Dict[str, Any],
    teams: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Create tournament asynchronously."""
    async with AsyncSessionLocal() as db:
        try:
            # Create tournament
            tournament = Tournament(
                id=tournament_id,
                slug=slug,
                name=name,
                season_id=season_id,
                division=division,
                start_date=start_date,
                end_date=end_date,
                status=status,
                venue_id=venue_id,
                settings=settings,
                organiser=organiser,
                teams=teams
            )
            db.add(tournament)
            await db.flush()
            
            # Generate tournament structure
            teams_for_generator = [
                {"team_id": t["teamId"], "seed": t["seed"]}
                for t in teams
            ]
            
            structure = await generate_tournament_structure(
                tournament_id=tournament_id,
                teams=teams_for_generator,
                settings=settings,
                db=db
            )
            
            await db.commit()
            
            return {
                "tournament_id": tournament_id,
                "stages_count": len(structure.get("stages", [])),
                "pools_count": len(structure.get("pools", [])),
                "matches_count": len(structure.get("matches", []))
            }
        
        except Exception as e:
            await db.rollback()
            raise e


if __name__ == "__main__":
    main()

