import json
import boto3
import os
from datetime import datetime
from urllib import request, error

def lambda_handler(event, context):
    """
    Fetches USF football stats from ESPN (basic info + detailed statistics)
    """
    
    # Configuration
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    team_id = os.environ.get('TEAM_ID', '58')  # USF team ID
    current_year = datetime.now().year
    
    print(f"Starting enhanced fetch for team {team_id}, season {current_year}")
    
    # ESPN API endpoints
    team_url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{team_id}"
    stats_url = f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{team_id}/statistics?season={current_year}"
    
    try:
        # Fetch basic team info (record, conference, etc.)
        print(f"Fetching team info from: {team_url}")
        with request.urlopen(team_url) as response:
            team_data = json.loads(response.read())
        
        print("Team data fetched successfully")
        
        # Fetch detailed statistics
        print(f"Fetching statistics from: {stats_url}")
        with request.urlopen(stats_url) as response:
            stats_data = json.loads(response.read())
        
        print("Statistics data fetched successfully")
        
        # Combine both datasets into one JSON
        combined_data = {
            'timestamp': datetime.now().isoformat(),
            'season': current_year,
            'team_info': team_data,
            'team_statistics': stats_data
        }
        
        # Prepare S3 file path
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        s3_key = f"v2-automation/raw/usf-stats-{timestamp}.json"
        
        # Save to S3
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=json.dumps(combined_data, indent=2),
            ContentType='application/json'
        )
        
        print(f"Saved combined data to S3: {s3_key}")
        
        # Send SNS notification
        sns_client = boto3.client('sns')
        topic_arn = os.environ.get('SNS_TOPIC_ARN')
        
        if topic_arn:
            try:
                message_body = f"""USF Football Stats have been updated!

File Location: s3://{bucket_name}/{s3_key}
Timestamp: {timestamp}
Season: {current_year}
Team ID: {team_id}

Data includes:
✓ Team record and basic info
✓ Detailed offensive statistics
✓ Detailed defensive statistics

Your enhanced automation is working!"""
                
                sns_client.publish(
                    TopicArn=topic_arn,
                    Subject='USF Stats Updated - Enhanced Version!',
                    Message=message_body
                )
                print("Email notification sent")
            except Exception as e:
                print(f"Failed to send notification: {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Enhanced stats fetched and saved successfully!',
                's3_location': f"s3://{bucket_name}/{s3_key}",
                'timestamp': timestamp,
                'season': current_year,
                'data_types': ['team_info', 'team_statistics']
            })
        }
        
    except error.URLError as e:
        print(f"Error fetching data: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Failed to fetch stats',
                'error': str(e)
            })
        }
    
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Unexpected error occurred',
                'error': str(e)
            })
        }
