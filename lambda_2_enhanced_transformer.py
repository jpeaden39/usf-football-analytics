import json
import boto3
import os
from datetime import datetime
import csv
from io import StringIO

def lambda_handler(event, context):
    """
    Transforms ESPN JSON data into CSV format with DETAILED team statistics
    """
    
    s3_client = boto3.client('s3')
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    
    print(f"Starting enhanced transformation for bucket: {bucket_name}")
    
    try:
        # Step 1: Get the most recent JSON file
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='v2-automation/raw/'
        )
        
        if 'Contents' not in response:
            print("No files found in raw folder")
            return {
                'statusCode': 200,
                'body': json.dumps('No files to process')
            }
        
        json_files = [obj for obj in response['Contents'] if obj['Key'].endswith('.json')]
        
        if not json_files:
            print("No JSON files found")
            return {
                'statusCode': 200,
                'body': json.dumps('No JSON files to process')
            }
        
        latest_file = sorted(json_files, key=lambda x: x['LastModified'], reverse=True)[0]
        json_key = latest_file['Key']
        
        print(f"Processing file: {json_key}")
        
        # Step 2: Read and parse JSON
        json_obj = s3_client.get_object(Bucket=bucket_name, Key=json_key)
        json_data = json.loads(json_obj['Body'].read().decode('utf-8'))
        
        # Step 3: Extract basic team info (wins/losses and PPG from record)
        team_info = json_data.get('team_info', {}).get('team', {})
        record = team_info.get('record', {})
        items = record.get('items', [{}])[0]
        stats = items.get('stats', [])
        
        # Extract from record stats (this has wins/losses AND points per game!)
        wins = 0
        losses = 0
        points_per_game = 0.0
        points_allowed_per_game = 0.0
        
        for stat in stats:
            stat_name = stat.get('name')
            stat_value = stat.get('value', 0)
            
            if stat_name == 'wins':
                wins = int(stat_value)
            elif stat_name == 'losses':
                losses = int(stat_value)
            elif stat_name == 'avgPointsFor':
                points_per_game = float(stat_value)
            elif stat_name == 'avgPointsAgainst':
                points_allowed_per_game = float(stat_value)
        
        season = json_data.get('season', datetime.now().year)
        
        print(f"Record stats - Season: {season}, Record: {wins}-{losses}")
        print(f"  PPG from record: {points_per_game}, Opp PPG: {points_allowed_per_game}")
        
        # Step 4: Extract DETAILED statistics from team_statistics
        team_statistics = json_data.get('team_statistics', {})
        results = team_statistics.get('results', {})
        stats_obj = results.get('stats', {})
        
        # Initialize with defaults
        passing_yards_per_game = 0.0
        rushing_yards_per_game = 0.0
        total_yards_per_game = 0.0
        yards_allowed_per_game = 0.0
        turnover_margin = 0
        
        # Helper function to find stat by name in categories
        def find_stat_value(categories, target_name):
            """Search through nested categories to find a specific stat"""
            for category in categories:
                if 'stats' in category:
                    for stat in category['stats']:
                        if stat.get('name') == target_name:
                            return stat.get('value', 0)
            return 0
        
        # Extract from the stats categories
        if 'categories' in stats_obj:
            categories = stats_obj['categories']
            
            # Find passing stats
            passing_yards_per_game = find_stat_value(categories, 'passingYardsPerGame')
            
            # Find rushing stats
            rushing_yards_per_game = find_stat_value(categories, 'rushingYardsPerGame')
            
            # Calculate total yards per game
            if passing_yards_per_game and rushing_yards_per_game:
                total_yards_per_game = passing_yards_per_game + rushing_yards_per_game
            else:
                total_yards_per_game = find_stat_value(categories, 'yardsPerGame')
            
            # Find turnover differential
            takeaways = find_stat_value(categories, 'totalTakeaways')
            giveaways = find_stat_value(categories, 'totalGiveaways')
            if takeaways or giveaways:
                turnover_margin = int(takeaways - giveaways)
            else:
                turnover_margin = int(find_stat_value(categories, 'turnOverDifferential'))
        
        print(f"Extracted detailed stats:")
        print(f"  PPG: {points_per_game}")
        print(f"  Points Allowed: {points_allowed_per_game}")
        print(f"  Pass Yards/Game: {passing_yards_per_game}")
        print(f"  Rush Yards/Game: {rushing_yards_per_game}")
        print(f"  Total Yards/Game: {total_yards_per_game}")
        print(f"  Turnover Margin: {turnover_margin}")
        
        # Determine conference
        conference = 'AAC'  # default
        if 'groups' in team_info:
            groups = team_info.get('groups', {})
            if isinstance(groups, dict) and 'parent' in groups:
                parent_id = groups.get('parent', {}).get('id', '')
                # AAC is id 151, Big 12 would be different
                conference = 'AAC' if parent_id == '80' else 'Big 12'
        
        # Step 5: Create new row with REAL stats
        new_row = {
            'season': season,
            'wins': int(wins),
            'losses': int(losses),
            'points_per_game': round(points_per_game, 1),
            'points_allowed_per_game': round(points_allowed_per_game, 1),
            'total_yards_per_game': round(total_yards_per_game, 1),
            'yards_allowed_per_game': round(yards_allowed_per_game, 1),  # Will be 0 for now, can add later
            'passing_yards_per_game': round(passing_yards_per_game, 1),
            'rushing_yards_per_game': round(rushing_yards_per_game, 1),
            'turnover_margin': int(turnover_margin),
            'conference': conference,
            'status': 'In Progress' if datetime.now().month < 12 else 'Complete'
        }
        
        print(f"Created row: {new_row}")
        
        # Step 6: Update CSV
        csv_key = 'v1-foundation/data/team_stats/team_season_stats.csv'
        
        try:
            csv_obj = s3_client.get_object(Bucket=bucket_name, Key=csv_key)
            existing_csv = csv_obj['Body'].read().decode('utf-8')
            
            csv_reader = csv.DictReader(StringIO(existing_csv))
            rows = list(csv_reader)
            
            # Update or append
            season_exists = False
            for i, row in enumerate(rows):
                if int(row['season']) == season:
                    rows[i] = new_row
                    season_exists = True
                    print(f"Updated existing row for season {season}")
                    break
            
            if not season_exists:
                rows.append(new_row)
                print(f"Added new row for season {season}")
            
        except s3_client.exceptions.NoSuchKey:
            print("CSV doesn't exist yet, creating new one")
            rows = [new_row]
        
        # Step 7: Write updated CSV
        output = StringIO()
        fieldnames = ['season', 'wins', 'losses', 'points_per_game', 'points_allowed_per_game',
                     'total_yards_per_game', 'yards_allowed_per_game', 'passing_yards_per_game',
                     'rushing_yards_per_game', 'turnover_margin', 'conference', 'status']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=csv_key,
            Body=output.getvalue(),
            ContentType='text/csv'
        )
        
        print(f"Successfully updated CSV at {csv_key}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Enhanced stats transformed and CSV updated successfully!',
                'season': season,
                'record': f"{wins}-{losses}",
                'points_per_game': points_per_game,
                'total_yards_per_game': total_yards_per_game,
                'csv_location': f"s3://{bucket_name}/{csv_key}"
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing enhanced stats',
                'error': str(e)
            })
        }
