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
            # Table name can be configured via environment variable
            table_name = os.getenv("SUPABASE_TABLE_NAME", "pharmacist_jobs")
            
            # Transform jobs for custom schema if needed
            transformed_jobs = []
            for job in jobs_list:
                transformed_job = {}

                # Apply field mapping if configured
                if FIELD_MAPPING:
                    for key, value in job.items():
                        new_key = FIELD_MAPPING.get(key, key)
                        transformed_job[new_key] = value
                else:
                    transformed_job = job.copy()

                # Custom transformations for jobs table schema
                if table_name == "jobs":
                    # Map interval to salary_type BEFORE other transformations
                    if "interval" in transformed_job and "salary_type" not in transformed_job:
                        interval = transformed_job.pop("interval", None)
                        if interval:
                            interval_lower = str(interval).lower()
                            if interval_lower in ["yearly", "annual"]:
                                transformed_job["salary_type"] = "yearly"
                            elif interval_lower in ["monthly"]:
                                transformed_job["salary_type"] = "monthly"
                            elif interval_lower in ["hourly"]:
                                transformed_job["salary_type"] = "hourly"
                            elif interval_lower in ["weekly"]:
                                transformed_job["salary_type"] = "weekly"
                            else:
                                transformed_job["salary_type"] = "yearly"  # Default

                    # Map job_url to application_url and remove job_url
                    if "job_url" in transformed_job and "application_url" not in transformed_job:
                        transformed_job["application_url"] = transformed_job["job_url"]
                    # Always remove job_url for jobs table (column doesn't exist)
                    transformed_job.pop("job_url", None)

                    # Generate slug from title if not present
                    if "slug" not in transformed_job and "title" in transformed_job:
                        import re
                        title = transformed_job.get("title", "")
                        slug = re.sub(r"[^\w\s-]", "", title.lower())
                        slug = re.sub(r"[-\s]+", "-", slug)
                        transformed_job["slug"] = slug[:100]  # Limit length

                    # Map date_posted to posted_at
                    if "date_posted" in transformed_job and "posted_at" not in transformed_job:
                        transformed_job["posted_at"] = transformed_job.pop("date_posted", None)

                    # Set default status if not present - set to approved so jobs appear immediately
                    if "status" not in transformed_job:
                        transformed_job["status"] = "approved"

                    # Normalize job_type: "fulltime" -> "full-time"
                    if "job_type" in transformed_job:
                        job_type = transformed_job["job_type"]
                        if job_type:
                            job_type = str(job_type).lower().replace("fulltime", "full-time").replace(
                                "parttime", "part-time"
                            )
                            transformed_job["job_type"] = job_type

                    # Normalize salary_type if it exists
                    if "salary_type" in transformed_job:
                        salary_type = str(transformed_job.get("salary_type", "")).lower()
                        if salary_type in ["yearly", "annual"]:
                            transformed_job["salary_type"] = "yearly"
                        elif salary_type in ["monthly"]:
                            transformed_job["salary_type"] = "monthly"
                        elif salary_type in ["hourly"]:
                            transformed_job["salary_type"] = "hourly"

                    # Map is_remote to is_featured if needed (or remove if not applicable)
                    if "is_remote" in transformed_job:
                        # Only set is_featured if is_remote is True
                        if transformed_job.get("is_remote"):
                            transformed_job["is_featured"] = True
                        # Remove is_remote as it doesn't exist in jobs table
                        transformed_job.pop("is_remote", None)

                    # Map min_amount/max_amount to salary_min/salary_max and remove originals
                    if "min_amount" in transformed_job and "salary_min" not in transformed_job:
                        try:
                            transformed_job["salary_min"] = int(transformed_job["min_amount"])
                        except (TypeError, ValueError):
                            transformed_job["salary_min"] = None
                    if "max_amount" in transformed_job and "salary_max" not in transformed_job:
                        try:
                            transformed_job["salary_max"] = int(transformed_job["max_amount"])
                        except (TypeError, ValueError):
                            transformed_job["salary_max"] = None
                    transformed_job.pop("min_amount", None)
                    transformed_job.pop("max_amount", None)

                    # Remove fields that don't exist in jobs table (including interval)
                    fields_to_remove = [
                        "site",
                        "job_url_direct",
                        "location",
                        "salary_source",
                        "currency",
                        "job_level",
                        "job_function",
                        "listing_type",
                        "emails",
                        "company_industry",
                        "company_url",
                        "company_logo",
                        "company_url_direct",
                        "company_addresses",
                        "company_num_employees",
                        "company_revenue",
                        "company_description",
                        "skills",
                        "experience_range",
                        "company_rating",
                        "company_reviews_count",
                        "vacancy_count",
                        "work_from_home_type",
                        "company",
                        "id",
                        "interval",
                        "scraped_at",
                    ]  # Added interval and scraped_at
                    for field in fields_to_remove:
                        transformed_job.pop(field, None)

                    # Whitelist only columns that exist in jobs table
                    allowed_fields = {
                        "id",
                        "title",
                        "slug",
                        "description",
                        "company_id",
                        "requirements",
                        "benefits",
                        "salary_min",
                        "salary_max",
                        "salary_type",
                        "job_type",
                        "experience_level",
                        "schedule_flexibility",
                        "application_url",
                        "application_email",
                        "status",
                        "is_featured",
                        "posted_by",
                        "posted_at",
                        "approved_at",
                        "expires_at",
                        "created_at",
                        "updated_at",
                    }
                    final_job = {k: v for k, v in transformed_job.items() if k in allowed_fields}
                    transformed_jobs.append(final_job)
                else:
                    transformed_jobs.append(transformed_job)
            
            # For jobs table, insert without explicit on_conflict
            # (primary key/constraints will handle uniqueness)
            print(f"\n📤 Uploading {len(transformed_jobs)} jobs to Supabase...")
            print(f"   Table: {table_name}")
            if transformed_jobs:
                print(f"   Sample job keys: {list(transformed_jobs[0].keys())[:10]}")

            if table_name == "jobs":
                # No explicit on_conflict – rely on primary key and let duplicates be handled later if needed
                response = supabase.table(table_name).upsert(transformed_jobs).execute()
            else:
                # Determine conflict key for other tables
                conflict_key = "job_url"
                response = supabase.table(table_name).upsert(
                    transformed_jobs,
                    on_conflict=conflict_key,
                ).execute()

            # Check response
            if hasattr(response, "data"):
                inserted_count = len(response.data) if response.data else 0
                print(f"\n✅ Successfully uploaded {inserted_count} jobs to Supabase")
                print(f"   Table: {table_name}")
                if response.data and len(response.data) > 0:
                    print(f"   First job title: {response.data[0].get('title', 'N/A')}")
            else:
                print(f"\n✅ Upsert completed (response: {type(response)})")
                print(f"   Table: {table_name}")
            
        except Exception as e:
            import traceback
            print(f"\n❌ Error uploading to Supabase:")
            print(f"   Error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            print(f"\n   Full traceback:")
            traceback.print_exc()
            print("\n   Continuing with local file saves...")
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

