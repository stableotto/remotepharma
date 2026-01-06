#!/usr/bin/env python3
"""
Script to search for remote pharmacist jobs using JobSpy
"""
import sys
import os
import csv
import json
from datetime import datetime

# Add the current directory to Python path so we can import jobspy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jobspy import scrape_jobs

# Try to import Supabase (optional)
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Note: Supabase client not installed. Install with: pip install supabase")

# Optional: Field mapping for existing schemas
# If your Supabase table uses different column names, map them here
# Example: FIELD_MAPPING = {"job_url": "url", "company": "company_name"}
FIELD_MAPPING = {}
# You can also set this via environment variable as JSON: SUPABASE_FIELD_MAPPING='{"job_url":"url"}'
if os.getenv("SUPABASE_FIELD_MAPPING"):
    import json
    FIELD_MAPPING = json.loads(os.getenv("SUPABASE_FIELD_MAPPING"))

# Search for remote pharmacist jobs
print("Searching for remote pharmacist jobs...")
jobs = scrape_jobs(
    site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
    search_term="pharmacist",
    is_remote=True,  # Filter for remote jobs only
    results_wanted=50,  # Get more results
    country_indeed='USA',
    verbose=1,  # Show progress
)

print(f"\nFound {len(jobs)} remote pharmacist jobs")
print("\n" + "="*80)
print(jobs.head(20).to_string())
print("="*80)

# Save to CSV and JSON
if len(jobs) > 0:
    csv_file = "pharmacist_remote_jobs.csv"
    json_file = "pharmacist_remote_jobs.json"
    
    # Save as CSV
    jobs.to_csv(csv_file, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    print(f"\nResults saved to {csv_file}")
    
    # Save as JSON (records format - array of objects)
    jobs_json = jobs.to_json(orient="records", date_format="iso")
    with open(json_file, 'w') as f:
        json.dump(json.loads(jobs_json), f, indent=2)
    print(f"Results saved to {json_file}")
    
    # Upload to Supabase if configured
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if SUPABASE_AVAILABLE and supabase_url and supabase_key:
        try:
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Convert DataFrame to list of dicts for Supabase
            jobs_list = json.loads(jobs_json)
            
            # Add metadata and clean up None values, apply field mapping
            scraped_time = datetime.utcnow().isoformat()
            processed_jobs = []
            for job in jobs_list:
                # Clean up None/NaN values
                cleaned_job = {}
                for key, value in job.items():
                    if value != value or value is None:  # Check for NaN
                        cleaned_job[key] = None
                    else:
                        cleaned_job[key] = value
                
                # Add scraped_at timestamp
                cleaned_job['scraped_at'] = scraped_time
                
                # Apply field mapping if configured
                if FIELD_MAPPING:
                    mapped_job = {}
                    for key, value in cleaned_job.items():
                        new_key = FIELD_MAPPING.get(key, key)
                        mapped_job[new_key] = value
                    processed_jobs.append(mapped_job)
                else:
                    processed_jobs.append(cleaned_job)
            
            jobs_list = processed_jobs
            
            # Upsert jobs (insert or update if exists)
            # Using job_url as unique identifier
            # Table name can be configured via environment variable
            table_name = os.getenv("SUPABASE_TABLE_NAME", "pharmacist_jobs")
            response = supabase.table(table_name).upsert(
                jobs_list,
                on_conflict="job_url"
            ).execute()
            
            print(f"\n✅ Successfully uploaded {len(jobs_list)} jobs to Supabase")
            print(f"   Table: {table_name}")
            
        except Exception as e:
            print(f"\n❌ Error uploading to Supabase: {str(e)}")
            print("   Continuing with local file saves...")
    elif supabase_url or supabase_key:
        print("\n⚠️  Supabase credentials found but client not installed.")
        print("   Install with: pip install supabase")
    
    # Show summary
    print(f"\nSummary:")
    print(f"  Total jobs found: {len(jobs)}")
    print(f"  Jobs by site:")
    print(jobs['site'].value_counts().to_string())
else:
    print("\nNo jobs found. Try adjusting your search parameters.")

