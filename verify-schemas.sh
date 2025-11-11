#!/bin/bash

# Schema Verification Script
# Tests that backend responses match frontend Zod schemas

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "═══════════════════════════════════════════════"
echo "  Schema Verification - Backend vs Frontend"
echo "═══════════════════════════════════════════════"
echo ""

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
    local name="$1"
    local url="$2"
    local required_fields="$3"
    
    echo -n "Testing $name... "
    
    # Get response
    response=$(curl -s "$url" 2>&1)
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ FAILED${NC} (curl error)"
        ((FAILED++))
        return 1
    fi
    
    # Check if valid JSON
    if ! echo "$response" | python3 -m json.tool > /dev/null 2>&1; then
        echo -e "${RED}✗ FAILED${NC} (invalid JSON)"
        echo "Response: $response"
        ((FAILED++))
        return 1
    fi
    
    # Check required fields
    for field in $required_fields; do
        if ! echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); exit(0 if isinstance(d, list) and len(d) > 0 and '$field' in d[0] else 1)" 2>/dev/null; then
            echo -e "${RED}✗ FAILED${NC} (missing field: $field)"
            ((FAILED++))
            return 1
        fi
    done
    
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
}

# Test Tournaments
echo "【TOURNAMENTS】"
test_endpoint "List tournaments" \
    "http://localhost:8000/v1/tournaments/" \
    "id slug name season division startDate endDate status venue stages teams updatedAt"

# Test Teams  
echo ""
echo "【TEAMS】"
test_endpoint "List teams" \
    "http://localhost:8000/v1/teams/" \
    "id name shortName slug division seasons roster"

# Test specific team roster structure
echo -n "Testing team roster structure... "
team_response=$(curl -s "http://localhost:8000/v1/teams/" 2>&1)
if echo "$team_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if not data or not isinstance(data, list):
        sys.exit(1)
    team = data[0]
    # Check roster structure
    if 'roster' not in team:
        print('Missing roster')
        sys.exit(1)
    if len(team['roster']) > 0:
        roster_entry = team['roster'][0]
        required = ['tournamentId', 'player', 'jerseyNumber', 'captain']
        for field in required:
            if field not in roster_entry:
                print(f'Missing {field} in roster entry')
                sys.exit(1)
        # Check player structure
        player = roster_entry['player']
        player_fields = ['id', 'jerseyNumber', 'name', 'roles', 'clubHistory']
        for field in player_fields:
            if field not in player:
                print(f'Missing {field} in player object')
                sys.exit(1)
        # Check name structure
        name = player['name']
        if 'first' not in name or 'last' not in name or 'display' not in name:
            print('Missing name fields')
            sys.exit(1)
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test Seasons structure
echo -n "Testing team seasons structure... "
if echo "$team_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if not data or not isinstance(data, list):
        sys.exit(1)
    team = data[0]
    if 'seasons' not in team:
        print('Missing seasons')
        sys.exit(1)
    if len(team['seasons']) > 0:
        season = team['seasons'][0]
        required = ['season', 'division', 'tournaments']
        for field in required:
            if field not in season:
                print(f'Missing {field} in season')
                sys.exit(1)
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test Venue structure
echo ""
echo "【VENUE】"
echo -n "Testing venue structure in tournaments... "
tournament_response=$(curl -s "http://localhost:8000/v1/tournaments/" 2>&1)
if echo "$tournament_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if not data or not isinstance(data, list):
        sys.exit(1)
    tournament = data[0]
    if 'venue' not in tournament:
        print('Missing venue')
        sys.exit(1)
    venue = tournament['venue']
    required = ['name', 'city', 'country', 'timezone', 'fields']
    for field in required:
        if field not in venue:
            print(f'Missing {field} in venue')
            sys.exit(1)
    # Check fields structure
    if len(venue['fields']) > 0:
        field = venue['fields'][0]
        if 'id' not in field or 'label' not in field:
            print('Missing id/label in venue field')
            sys.exit(1)
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test Stages structure  
echo ""
echo "【STAGES】"
echo -n "Testing stages structure in tournaments... "
if echo "$tournament_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if not data or not isinstance(data, list):
        sys.exit(1)
    tournament = data[0]
    if 'stages' not in tournament:
        print('Missing stages')
        sys.exit(1)
    if len(tournament['stages']) > 0:
        stage = tournament['stages'][0]
        required = ['id', 'name', 'stageType', 'division', 'pools']
        for field in required:
            if field not in stage:
                print(f'Missing {field} in stage')
                sys.exit(1)
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Test Pools structure
echo -n "Testing pools structure in stages... "
if echo "$tournament_response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if not data or not isinstance(data, list):
        sys.exit(1)
    tournament = data[0]
    if 'stages' not in tournament or len(tournament['stages']) == 0:
        sys.exit(0)  # No stages, skip
    stage = tournament['stages'][0]
    if 'pools' not in stage or len(stage['pools']) == 0:
        sys.exit(0)  # No pools, skip
    pool = stage['pools'][0]
    required = ['id', 'label', 'stageId', 'teams']
    for field in required:
        if field not in pool:
            print(f'Missing {field} in pool')
            sys.exit(1)
    # Check teams in pool
    if len(pool['teams']) > 0:
        team = pool['teams'][0]
        if 'teamId' not in team or 'seed' not in team:
            print('Missing teamId/seed in pool team')
            sys.exit(1)
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
" 2>&1; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════"
echo "  Test Summary"
echo "═══════════════════════════════════════════════"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All schema tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some schema tests failed${NC}"
    echo ""
    echo "Check the logs for details:"
    echo "  tail -f logs/backend.log | grep -i error"
    echo "  tail -f logs/frontend.log | grep -i 'failed to parse'"
    exit 1
fi

