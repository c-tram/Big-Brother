# MLB API Coverage Analysis

## Current State: Our Backend vs Complete MLB API

### ✅ What We Currently Cover (20 endpoints)

**Team Endpoints (4):**
- `get_teams()` - All MLB teams  
- `get_team()` - Specific team details
- `get_team_roster()` - Team roster for season
- `get_team_stats()` - Team statistics

**Player Endpoints (2):**
- `get_player()` - Specific player details
- `get_player_stats()` - Player statistics

**Game Endpoints (5):**
- `get_schedule()` - Game schedule by date range
- `get_game()` - Live game feed
- `get_game_boxscore()` - Game boxscore
- `get_game_linescore()` - Game linescore
- `get_games_by_date()` - All games for specific date

**Season/Standings (2):**
- `get_standings()` - League standings
- `get_seasons()` - Available seasons

**Statistics (2):**
- `get_league_leaders()` - League statistical leaders
- `get_team_stats_leaders()` - Team statistical leaders

**Organizational (3):**
- `get_venues()` - All MLB venues
- `get_venue()` - Specific venue details
- `get_divisions()` - MLB divisions
- `get_leagues()` - MLB leagues

**Utility (2):**
- `get_current_season()` - Current season year
- `get_date_range_games()` - Games for last N days

---

## ❌ What We're MISSING (Critical Gaps)

Based on the official MLB API documentation, we're missing **60+ endpoints** that provide comprehensive MLB data:

### 🔴 CRITICAL MISSING ENDPOINTS

**Advanced Player Data:**
- Player search by name (`search_player_all`)
- Player team history (`player_teams`)
- Player career hitting stats (`sport_career_hitting`)
- Player career pitching stats (`sport_career_pitching`)
- Player league-specific stats (`sport_career_hitting_lg`, `sport_career_pitching_lg`)
- Player season hitting stats (`sport_hitting_tm`)
- Player season pitching stats (`sport_pitching_tm`)
- Player projected stats (`proj_pecota_batting`, `proj_pecota_pitching`)

**Team Data:**
- Team 40-man roster (`roster_40`)
- Team all-time roster (`roster_team_alltime`)
- Team historical data by seasons

**Advanced Game Data:**
- Game play-by-play data
- Game pitch-by-pitch data
- Game events and situations
- Game weather conditions
- Game attendance details
- Game umpire information

**Reports & Analysis:**
- Transactions (`transaction_all`)
- Injuries (`wsfb_news_injury`)
- Broadcast information (`mlb_broadcast_info`)
- Hitting leaders (`leader_hitting_repeater`)
- Pitching leaders (`leader_pitching_repeater`)

**Draft & Prospects:**
- Draft results and prospects
- Minor league data
- Farm system information

**Awards & Recognition:**
- Player awards and achievements
- All-Star game data
- Hall of Fame information

**Advanced Statistics:**
- Sabermetrics (WAR, wOBA, FIP, etc.)
- Statcast data (exit velocity, launch angle, etc.)
- Advanced fielding metrics
- Situational statistics

**Historical Data:**
- Historical seasons and records
- Franchise history
- Record books

### 🟡 SPECIFIC USE CASE GAPS

For the "Aaron Judge hitting at Dodger Stadium" example:
1. ✅ We can get Judge's player info
2. ✅ We can get games at Dodger Stadium  
3. ❌ We can't efficiently query "Judge's performance at specific venues"
4. ❌ We lack situational/split statistics
5. ❌ We don't have advanced metrics for performance analysis

---

## 🎯 RECOMMENDED EXPANSION PLAN

### Phase 1: Player Performance Enhancement (High Priority)
```python
# Missing endpoints to add:
def search_players(self, name_part: str, active_only: bool = True) -> Dict
def get_player_career_hitting(self, player_id: int, game_type: str = 'R') -> Dict
def get_player_career_pitching(self, player_id: int, game_type: str = 'R') -> Dict
def get_player_season_hitting(self, player_id: int, season: int, game_type: str = 'R') -> Dict
def get_player_season_pitching(self, player_id: int, season: int, game_type: str = 'R') -> Dict
def get_player_team_history(self, player_id: int, season: Optional[int] = None) -> Dict
def get_player_splits(self, player_id: int, group: str, season: Optional[int] = None) -> Dict
```

### Phase 2: Advanced Game Analytics (Medium Priority)
```python
def get_game_play_by_play(self, game_id: int) -> Dict
def get_game_pitch_data(self, game_id: int) -> Dict
def get_game_events(self, game_id: int) -> Dict
def get_games_advanced_filter(self, **filters) -> Dict  # Team, venue, player combinations
```

### Phase 3: Reports & Intelligence (Medium Priority)  
```python
def get_transactions(self, start_date: str, end_date: str) -> Dict
def get_injuries(self) -> Dict
def get_hitting_leaders(self, stat: str, season: int, limit: int = 10) -> Dict
def get_pitching_leaders(self, stat: str, season: int, limit: int = 10) -> Dict
def get_broadcast_info(self, start_date: str, end_date: str) -> Dict
```

### Phase 4: Complete Coverage (Low Priority)
```python
def get_draft_results(self, year: int) -> Dict
def get_prospects_data(self, team_id: Optional[int] = None) -> Dict
def get_awards(self, season: int, award_type: Optional[str] = None) -> Dict
def get_all_star_data(self, season: int) -> Dict
def get_40_man_roster(self, team_id: int) -> Dict
def get_team_all_time_roster(self, team_id: int, start_season: int, end_season: int) -> Dict
```

---

## 🚀 IMPLEMENTATION STRATEGY

### 1. Enhanced MLBApi Service
Create extended service that bridges both API versions:
- `https://statsapi.mlb.com/api/v1` (current - modern endpoints)
- `http://lookup-service-prod.mlb.com` (legacy - comprehensive historical data)

### 2. Smart Query Optimization
```python
class AdvancedMLBApi(MLBApi):
    def get_player_venue_performance(self, player_name: str, venue_name: str, seasons: List[int]) -> Dict:
        """Aaron Judge at Dodger Stadium use case"""
        # 1. Search for player
        # 2. Get all games at venue for seasons
        # 3. Filter games where player participated
        # 4. Aggregate performance statistics
        # 5. Return comprehensive analysis
```

### 3. Database Model Extensions
Update models to store comprehensive data:
```python
# New models needed:
class PlayerGameSplits  # Venue-specific performance
class GamePlayByPlay   # Detailed game events
class PlayerTransactions  # Team changes, trades
class PlayerAwards     # Recognition and achievements
class AdvancedStats    # Sabermetrics and Statcast
```

### 4. Natural Language Query Support
```python
class NLQueryProcessor:
    def process_query(self, query: str) -> Dict:
        """Convert 'Aaron Judge hitting at Dodger Stadium' to API calls"""
        # Parse entities (player, venue, action)
        # Determine required endpoints
        # Execute optimized query sequence
        # Return structured results
```

---

## 🎯 ANSWER TO YOUR QUESTION

**Does our backend truly scrape EVERYTHING available in the MLB API?**

**NO.** We're currently covering only **~25%** of available MLB API endpoints.

**Critical Missing Coverage:**
- ❌ Player career/season detailed statistics
- ❌ Advanced player search and filtering  
- ❌ Situational and split statistics
- ❌ Transactions, injuries, awards data
- ❌ Play-by-play and pitch-level data
- ❌ Draft, prospects, and minor league data
- ❌ Advanced analytics and sabermetrics

**For the Aaron Judge at Dodger Stadium example:**
- ✅ We can get basic player info and venue games
- ❌ We lack efficient player-venue performance queries
- ❌ We're missing advanced hitting metrics and situational stats
- ❌ No comprehensive historical performance analysis

**Recommendation:** Implement Phase 1 expansions immediately to support flexible querying for frontend LLM integration.
