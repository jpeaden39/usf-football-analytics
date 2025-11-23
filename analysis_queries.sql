-- ============================================
-- USF FOOTBALL ANALYTICS - COMPLETE QUERY COLLECTION
-- Database: usf_football_analytics
-- Created: November 4, 2025
-- ============================================

-- ============================================
-- QUERY 1: Season-by-Season Performance
-- Shows the complete picture of each season
-- ============================================
SELECT 
    season,
    wins,
    losses,
    ROUND(CAST(wins AS DOUBLE) / (wins + losses) * 100, 1) as win_percentage,
    points_per_game,
    points_allowed_per_game,
    ROUND(points_per_game - points_allowed_per_game, 1) as point_differential,
    conference,
    status
FROM team_season_stats
ORDER BY season;


-- ============================================
-- QUERY 2: The Turnaround Story (Complete Seasons Only)
-- Compare Jeff Scott vs Alex Golesh - COMPLETE SEASONS
-- ============================================
SELECT 
    CASE 
        WHEN season <= 2022 THEN 'Jeff Scott Era (2020-2022)'
        ELSE 'Alex Golesh Era (2023-2024)'
    END as coaching_era,
    COUNT(*) as seasons,
    SUM(wins) as total_wins,
    SUM(losses) as total_losses,
    CAST(SUM(wins) AS VARCHAR) || '-' || CAST(SUM(losses) AS VARCHAR) as overall_record,
    ROUND((CAST(SUM(wins) AS DOUBLE) / CAST((SUM(wins) + SUM(losses)) AS DOUBLE)) * 100, 1) as win_percentage,
    ROUND(AVG(points_per_game), 1) as avg_ppg,
    ROUND(AVG(points_allowed_per_game), 1) as avg_points_allowed,
    ROUND(AVG(total_yards_per_game), 1) as avg_total_offense
FROM team_season_stats
WHERE status = 'Complete'
GROUP BY 
    CASE 
        WHEN season <= 2022 THEN 'Jeff Scott Era (2020-2022)'
        ELSE 'Alex Golesh Era (2023-2024)'
    END
ORDER BY coaching_era;


-- ============================================
-- QUERY 2B: The Turnaround Story (Including 2025)
-- Compare Jeff Scott vs Alex Golesh - INCLUDING CURRENT SEASON
-- ============================================
SELECT 
    CASE 
        WHEN season <= 2022 THEN 'Jeff Scott Era (2020-2022)'
        ELSE 'Alex Golesh Era (2023-2025)'
    END as coaching_era,
    COUNT(*) as seasons,
    SUM(wins) as total_wins,
    SUM(losses) as total_losses,
    CAST(SUM(wins) AS VARCHAR) || '-' || CAST(SUM(losses) AS VARCHAR) as overall_record,
    ROUND((CAST(SUM(wins) AS DOUBLE) / CAST((SUM(wins) + SUM(losses)) AS DOUBLE)) * 100, 1) as win_percentage,
    ROUND(AVG(points_per_game), 1) as avg_ppg,
    ROUND(AVG(points_allowed_per_game), 1) as avg_points_allowed,
    ROUND(AVG(total_yards_per_game), 1) as avg_total_offense
FROM team_season_stats
GROUP BY 
    CASE 
        WHEN season <= 2022 THEN 'Jeff Scott Era (2020-2022)'
        ELSE 'Alex Golesh Era (2023-2025)'
    END
ORDER BY coaching_era;


-- ============================================
-- QUERY 2C: Year-by-Year Coaching Impact
-- Shows progression under each coach
-- ============================================
SELECT 
    cs.season,
    cs.head_coach,
    ts.wins,
    ts.losses,
    CAST(ts.wins AS VARCHAR) || '-' || CAST(ts.losses AS VARCHAR) as record,
    ROUND((CAST(ts.wins AS DOUBLE) / CAST((ts.wins + ts.losses) AS DOUBLE)) * 100, 1) as win_pct,
    ts.points_per_game as ppg,
    ts.points_allowed_per_game as pa_pg,
    ts.status
FROM team_season_stats ts
JOIN coaching_staff cs ON ts.season = cs.season
ORDER BY ts.season;


-- ============================================
-- QUERY 3: Offensive Improvement Over Time
-- Track offensive progression year by year
-- ============================================
SELECT 
    season,
    ROUND(total_yards_per_game, 1) as total_offense,
    ROUND(passing_yards_per_game, 1) as passing,
    ROUND(rushing_yards_per_game, 1) as rushing,
    ROUND(points_per_game, 1) as ppg,
    CASE 
        WHEN season > 2020 THEN ROUND(points_per_game - LAG(points_per_game) OVER (ORDER BY season), 1)
    END as ppg_change_from_prior_year
FROM team_season_stats
ORDER BY season;


-- ============================================
-- QUERY 4: Defensive Performance
-- Show how defense improved under new staff
-- ============================================
SELECT 
    season,
    ROUND(points_allowed_per_game, 1) as ppg_allowed,
    ROUND(yards_allowed_per_game, 1) as yards_allowed,
    turnover_margin,
    CASE 
        WHEN turnover_margin > 0 THEN 'Positive'
        WHEN turnover_margin < 0 THEN 'Negative'
        ELSE 'Even'
    END as turnover_trend
FROM team_season_stats
ORDER BY season;


-- ============================================
-- QUERY 5: Coaching Staff Timeline with Results
-- Show all coaching changes and their impact
-- ============================================
SELECT 
    cs.season,
    cs.head_coach,
    cs.offensive_coordinator,
    cs.defensive_coordinator,
    cs.years_at_usf,
    ts.wins,
    ts.losses,
    ROUND((CAST(ts.wins AS DOUBLE) / CAST((ts.wins + ts.losses) AS DOUBLE)) * 100, 1) as win_pct,
    cs.notes
FROM coaching_staff cs
JOIN team_season_stats ts ON cs.season = ts.season
ORDER BY cs.season;


-- ============================================
-- QUERY 6: Top Players by Season
-- See the star players each year (500+ yards)
-- ============================================
SELECT 
    season,
    player_name,
    position,
    stat_type,
    stat_value,
    additional_notes
FROM key_players
WHERE stat_type IN ('Passing Yards', 'Rushing Yards', 'Receiving Yards')
    AND stat_value > 500
ORDER BY season DESC, stat_value DESC;


-- ============================================
-- QUERY 7: Byrum Brown's Impact
-- Focus on the QB who changed everything
-- ============================================
SELECT 
    season,
    player_name,
    position,
    stat_type,
    stat_value,
    additional_notes
FROM key_players
WHERE player_name = 'Byrum Brown'
ORDER BY season, stat_type;


-- ============================================
-- QUERY 8: 2025 Current Season vs Historical Average
-- Show how 2025 compares to past performance
-- ============================================
SELECT 
    'Current 2025 Season' as category,
    wins,
    losses,
    points_per_game,
    points_allowed_per_game,
    total_yards_per_game
FROM team_season_stats
WHERE season = 2025

UNION ALL

SELECT 
    'Historical Average (2020-2024)' as category,
    ROUND(AVG(wins), 1) as wins,
    ROUND(AVG(losses), 1) as losses,
    ROUND(AVG(points_per_game), 1) as points_per_game,
    ROUND(AVG(points_allowed_per_game), 1) as points_allowed_per_game,
    ROUND(AVG(total_yards_per_game), 1) as total_yards_per_game
FROM team_season_stats
WHERE season BETWEEN 2020 AND 2024;


-- ============================================
-- QUERY 9: Best and Worst Seasons
-- Identify the extremes
-- ============================================
SELECT 
    'Best Season' as type,
    season,
    wins,
    losses,
    CAST(wins AS VARCHAR) || '-' || CAST(losses AS VARCHAR) as record,
    points_per_game,
    points_allowed_per_game
FROM team_season_stats
WHERE status = 'Complete'
ORDER BY wins DESC, points_per_game DESC
LIMIT 1

UNION ALL

SELECT 
    'Worst Season' as type,
    season,
    wins,
    losses,
    CAST(wins AS VARCHAR) || '-' || CAST(losses AS VARCHAR) as record,
    points_per_game,
    points_allowed_per_game
FROM team_season_stats
WHERE status = 'Complete'
ORDER BY wins ASC, points_per_game ASC
LIMIT 1;


-- ============================================
-- QUERY 10: Complete Summary Report
-- Everything in one view for easy presentation
-- ============================================
SELECT 
    ts.season,
    cs.head_coach,
    CAST(ts.wins AS VARCHAR) || '-' || CAST(ts.losses AS VARCHAR) as record,
    ROUND((CAST(ts.wins AS DOUBLE) / CAST((ts.wins + ts.losses) AS DOUBLE)) * 100, 1) as win_pct,
    ts.points_per_game as ppg,
    ts.points_allowed_per_game as pa_pg,
    ts.total_yards_per_game as total_off,
    ts.turnover_margin as to_margin,
    ts.conference,
    ts.status
FROM team_season_stats ts
JOIN coaching_staff cs ON ts.season = cs.season
ORDER BY ts.season;


-- ============================================
-- BONUS QUERY 11: Offensive vs Defensive Improvement
-- Shows which side of the ball improved more
-- ============================================
SELECT 
    CASE 
        WHEN season <= 2022 THEN 'Jeff Scott Era'
        ELSE 'Alex Golesh Era'
    END as era,
    ROUND(AVG(points_per_game), 1) as avg_points_scored,
    ROUND(AVG(points_allowed_per_game), 1) as avg_points_allowed,
    ROUND(AVG(total_yards_per_game), 1) as avg_total_yards,
    ROUND(AVG(yards_allowed_per_game), 1) as avg_yards_allowed,
    ROUND(AVG(turnover_margin), 1) as avg_turnover_margin
FROM team_season_stats
WHERE status = 'Complete'
GROUP BY 
    CASE 
        WHEN season <= 2022 THEN 'Jeff Scott Era'
        ELSE 'Alex Golesh Era'
    END;


-- ============================================
-- BONUS QUERY 12: 2025 Pace Projection
-- If USF maintains current pace, what's the final record?
-- ============================================
SELECT 
    '2025 Current (8 games)' as status,
    6 as wins,
    2 as losses,
    CAST(6 AS VARCHAR) || '-' || CAST(2 AS VARCHAR) as record,
    ROUND((CAST(6 AS DOUBLE) / 8.0) * 100, 1) as win_pct
    
UNION ALL

SELECT 
    '2025 Projected (12 games)' as status,
    ROUND((6.0 / 8.0) * 12, 0) as projected_wins,
    ROUND((2.0 / 8.0) * 12, 0) as projected_losses,
    CAST(ROUND((6.0 / 8.0) * 12, 0) AS VARCHAR) || '-' || 
    CAST(ROUND((2.0 / 8.0) * 12, 0) AS VARCHAR) as projected_record,
    ROUND((CAST(6 AS DOUBLE) / 8.0) * 100, 1) as projected_win_pct;
