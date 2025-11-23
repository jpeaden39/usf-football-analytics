# USF Football Analytics Pipeline: Documenting a Historic Turnaround

**Automated data pipeline tracking the University of South Florida Bulls' dramatic transformation under head coach Alex Golesh**

![USF Dashboard](dashboard_screenshot.png)

## 📊 The Story

When Alex Golesh took over as USF's head coach in 2023, the program had won just **4 games in 3 years** while averaging **17.7 points per game**. 

Three seasons later, the Bulls have won **20 games** and are averaging **33.3 PPG** - with the 2025 season on pace for a **program-record 41.6 PPG**.

This project automates the collection and analysis of this historic turnaround.

---

## 🏗️ Architecture

![Architecture Diagram](architecture_diagram.png)

### Components:

- **AWS Lambda** (Python): Automated data fetching and transformation
- **Amazon S3**: Data lake storage (raw JSON + processed CSV)
- **Amazon Athena**: SQL query engine for analytics
- **Amazon QuickSight**: Interactive dashboards and visualizations
- **Amazon EventBridge**: Scheduled automation (every Monday)
- **Amazon SNS**: Email notifications on successful updates
- **ESPN API**: Real-time college football statistics

---

## 🚀 Features

### Automated Data Pipeline
- **Weekly updates**: Every Monday at 3:00 PM EST, Lambda fetches latest stats from ESPN API
- **Real-time processing**: JSON data automatically transformed to CSV within seconds
- **Email notifications**: Confirmation sent when new data is available
- **Error handling**: Built-in retry logic and comprehensive logging

### Rich Dataset
- **6 seasons of data** (2020-2025)
- Team statistics: wins, losses, PPG, yards, turnovers
- Coaching staff information
- Key player statistics (QB Byrum Brown)

### Interactive Dashboard
- Points per game trend analysis
- Before/After coaching comparison
- Season-by-season performance metrics
- Player impact visualization

---

## 💡 Key Insights

### The Golesh Effect

| Metric | Before Golesh (2020-2022) | After Golesh (2023-2025) | Change |
|--------|---------------------------|--------------------------|--------|
| **Avg PPG** | 17.7 | 33.3 | +88% 📈 |
| **Total Wins** | 4 | 20 | +400% 🔥 |
| **Win %** | 13.8% | 55.6% | +303% |

### QB Byrum Brown: The Catalyst
- **7,753 career passing yards** (2023-2025)
- **1,622 career rushing yards**
- Dual-threat ability unlocking offensive explosion
- 2025: Leading team to program-record 41.6 PPG

---

## 🛠️ Technical Implementation

### Lambda Function #1: Data Fetcher
```python
# Fetches data from ESPN API
# Saves raw JSON to S3: v2-automation/raw/
# Triggered: EventBridge schedule (Mondays 3pm EST)
```

**Key Features:**
- Robust error handling
- Comprehensive logging to CloudWatch
- Efficient API calls (single request per execution)

### Lambda Function #2: Data Transformer
```python
# Transforms JSON to CSV
# Calculates advanced statistics
# Updates master dataset
```

**Key Features:**
- S3 trigger (processes new files automatically)
- Data validation and cleaning
- Maintains historical data integrity

### EventBridge Scheduling
- **Schedule**: `cron(0 20 ? * MON *)`
- **Time**: 8:00 PM UTC (3:00 PM EST)
- **Ensures**: ESPN has updated weekend game results

### Athena SQL Views
Created optimized views for dashboard queries:
- `coaching_era_stats` - Aggregate statistics by coach
- `golesh_impact` - Before/after comparison
- `current_season` - Live season tracking

---

## 🧪 Challenges & Solutions

### Challenge 1: Lambda Recursive Loop
**Problem**: Lambda #2 was triggering itself infinitely, causing AWS to shut it down.

**Root Cause**: S3 trigger was watching entire bucket, including the output folder.

**Solution**: 
- Added prefix filter: `v2-automation/raw/`
- Added suffix filter: `.json`
- Ensured Lambda only triggers on NEW input files, not its own outputs

### Challenge 2: Stale Data on Monday Updates
**Problem**: Automation ran Monday 8am EST, but ESPN hadn't updated weekend game stats yet.

**Root Cause**: ESPN typically updates stats Sunday night/Monday morning.

**Solution**: Changed EventBridge schedule from 1:00 PM UTC (8am EST) to 8:00 PM UTC (3pm EST), ensuring fresh data.

### Challenge 3: QuickSight Permissions
**Problem**: Dashboard showed "No data" despite successful Athena queries.

**Root Cause**: QuickSight didn't have permission to read S3 buckets.

**Solution**: 
- Enabled S3 access in QuickSight security settings
- Selected specific buckets: `usf-football-stats-data`
- Granted read permissions to Athena query results bucket

### Challenge 4: Data Type Compatibility
**Problem**: QuickSight couldn't import table directly from Athena.

**Solution**: Created simplified view with explicit type casting:
```sql
CREATE VIEW quicksight_data AS
SELECT 
    CAST(season AS INTEGER) as season,
    CAST(wins AS INTEGER) as wins,
    CAST(points_per_game AS DOUBLE) as ppg
FROM team_season_stats;
```

---

## 📚 What I Learned

### Technical Skills Developed
- **AWS Lambda**: Serverless architecture, event-driven programming
- **S3 Event Triggers**: Understanding prefix/suffix filtering to prevent loops
- **Athena SQL**: Writing efficient queries for large datasets
- **QuickSight**: Data visualization and dashboard design
- **IAM Permissions**: Configuring cross-service access securely
- **EventBridge**: Cron scheduling in cloud environments
- **API Integration**: Working with RESTful APIs (ESPN)
- **Error Handling**: Building resilient, production-ready code

### Data Engineering Concepts
- **Data Lake Architecture**: Separating raw and processed data
- **ETL Pipeline**: Extract, Transform, Load best practices
- **Automation**: Building hands-off data pipelines
- **Data Validation**: Ensuring data quality and integrity
- **Schema Design**: Organizing data for efficient querying

### Problem-Solving Approach
This project taught me the importance of:
- **Systematic debugging** (CloudWatch logs were crucial)
- **Reading error messages carefully** (region mismatches, permission issues)
- **Iterative development** (building piece by piece, testing frequently)
- **Documentation** (comments and logs saved hours of troubleshooting)

---

## 🤖 Role of AI in This Project

### Claude as Learning Partner
Unlike previous projects where I struggled alone, **I used Claude AI as a real-time mentor** throughout this build. This was transformative:

**What Worked:**
- **Learning while building**: Instead of tutorials, I built a real project and asked questions when stuck
- **Debugging partner**: Claude helped interpret error messages and suggest fixes
- **Best practices**: Learned production-ready patterns (error handling, logging, etc.)
- **Architectural guidance**: Understood WHY certain AWS services work together

**Key Difference from Past Projects:**
- **Previous attempts**: Watched tutorials → got stuck → abandoned project
- **This project**: Built something real → hit problems → solved them with AI guidance → kept momentum

**Example**: When Lambda recursive loop occurred, Claude helped me:
1. Understand WHAT was happening (reading CloudWatch logs)
2. WHY it was happening (S3 trigger configuration)
3. HOW to fix it (prefix/suffix filters)
4. WHY that fix worked (understanding event-driven architecture)

**Result**: I now understand Lambda triggers deeply, not just "copied code that works."

---

## 📁 Project Structure

```
usf-football-analytics/
├── lambda/
│   ├── fetcher/
│   │   └── lambda_function.py          # ESPN API data fetcher
│   └── transformer/
│       └── lambda_function.py          # JSON to CSV transformer
├── athena/
│   ├── table_definitions.sql           # CREATE TABLE statements
│   └── views.sql                       # Analytical views
├── data/
│   ├── team_season_stats.csv          # Master dataset
│   ├── coaching_staff.csv             # Coaching history
│   └── key_players.csv                # Player statistics
├── dashboard/
│   └── usf_turnaround_dashboard.pdf   # QuickSight export
└── README.md
```

---

## 🚦 Getting Started

### Prerequisites
- AWS Account with appropriate permissions
- Python 3.9+ (for Lambda)
- Basic SQL knowledge (for Athena queries)

### Setup Instructions

#### 1. Create S3 Bucket
```bash
aws s3 mb s3://usf-football-stats-data
aws s3 mb s3://usf-football-stats-data/v1-foundation/data/
aws s3 mb s3://usf-football-stats-data/v2-automation/raw/
```

#### 2. Deploy Lambda Functions

**Fetcher Function:**
```bash
cd lambda/fetcher
zip -r function.zip .
aws lambda create-function \
  --function-name USF-Stats-Fetcher \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role
```

**Transformer Function:**
```bash
cd lambda/transformer
zip -r function.zip .
aws lambda create-function \
  --function-name USF-Stats-Transformer \
  --runtime python3.9 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://function.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role
```

#### 3. Configure S3 Trigger for Transformer
- Go to Lambda console → USF-Stats-Transformer
- Add trigger → S3
- Bucket: `usf-football-stats-data`
- Event type: PUT
- Prefix: `v2-automation/raw/`
- Suffix: `.json`

#### 4. Create EventBridge Rule
```bash
aws events put-rule \
  --name USF-Weekly-Stats-Update \
  --schedule-expression "cron(0 20 ? * MON *)"

aws events put-targets \
  --rule USF-Weekly-Stats-Update \
  --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT_ID:function:USF-Stats-Fetcher"
```

#### 5. Set Up Athena
- Create database: `usf_football_analytics`
- Run table creation scripts from `athena/table_definitions.sql`
- Create views from `athena/views.sql`

#### 6. Configure QuickSight (Optional)
- Enable QuickSight in your AWS account
- Grant S3 permissions to QuickSight role
- Connect to Athena data source
- Import datasets and build visualizations

---

## 📈 Future Enhancements

### Short Term
- [ ] Add player statistics tracking beyond QB
- [ ] Include opponent analysis
- [ ] Track conference standings
- [ ] Add game-by-game breakdown

### Medium Term
- [ ] Predictive modeling (win probability)
- [ ] Comparison with other AAC teams
- [ ] Historical program records tracking
- [ ] Mobile-friendly dashboard

### Long Term
- [ ] Infrastructure as Code (Terraform)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Real-time game updates (WebSocket)
- [ ] Multi-sport expansion

---

## 🎓 Lessons for Other Builders

### What Worked
1. **Start with manual data** - I created CSVs by hand first, then automated
2. **Build incrementally** - Lambda 1 first, then Lambda 2, then dashboard
3. **Test frequently** - Manual Lambda tests caught issues early
4. **Use CloudWatch** - Logs are your best friend for debugging
5. **AI as mentor** - Don't just copy code; understand WHY it works

### Common Pitfalls to Avoid
1. **S3 trigger loops** - Always use prefix/suffix filters!
2. **IAM permissions** - Be explicit about cross-service access
3. **Region mismatches** - Keep all services in same region
4. **Data staleness** - Account for data source update timing
5. **Over-engineering** - Ship working code, optimize later

### If I Started Over
I would:
- Document architecture decisions as I go
- Create CloudFormation templates from day one
- Set up monitoring/alerting earlier
- Build test data generators
- Use version control from the start

---

## 🏆 Results & Impact

### Personal Achievement
- **First completed data engineering project** after multiple failed attempts
- Built production-grade automation running reliably every week
- Created portfolio piece demonstrating end-to-end pipeline
- Learned AWS services deeply through hands-on problem solving

### Technical Metrics
- **100% automation success rate** since fixing recursive loop
- **< 30 second** end-to-end pipeline execution
- **6 seasons** of historical data analyzed
- **Zero manual intervention** required for weekly updates

### Data Insights Uncovered
- USF's offense improved **88%** under new coaching
- Team is on pace for **program-record** scoring season
- QB Byrum Brown's dual-threat ability is key differentiator
- Defensive improvement (38.4 → 25.9 PPG allowed) equally important

---

## 📞 Contact

**James**  
- GitHub: [Your GitHub]
- LinkedIn: [Your LinkedIn]
- Email: [Your Email]

---

## 🙏 Acknowledgments

- **ESPN API** for providing comprehensive college football data
- **AWS Free Tier** for making this project possible
- **Claude AI (Anthropic)** for serving as a patient debugging partner and teaching me data engineering concepts
- **USF Football** for the inspiring turnaround story worth documenting

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 📊 Project Stats

- **Lines of Code**: ~400 (Python Lambda functions)
- **AWS Services Used**: 6 (Lambda, S3, Athena, QuickSight, EventBridge, SNS)
- **Data Points**: 60+ (6 seasons × 10+ metrics)
- **Development Time**: 2 weeks
- **Cost**: < $5/month (staying within AWS Free Tier)

---

**Built with ☕ and determination by a data engineering student who refused to give up**
