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
try:
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"],
        search_term="pharmacist",
        google_search_term="pharmacist jobs remote in the last month",  # Specific Google Jobs query
        is_remote=True,  # Filter for remote jobs only
        results_wanted=50,  # Get more results per site
        hours_old=720,  # Only jobs from last 30 days (720 hours) - applies to most sites
        country_indeed='USA',
        linkedin_fetch_description=True,  # Fetch full descriptions from LinkedIn (slower but gets descriptions)
        verbose=1,  # Show progress
    )
except Exception as e:
    import traceback
    print(f"\n❌ Error during job scraping:")
    print(f"   Error: {str(e)}")
    print(f"   Error type: {type(e).__name__}")
    print(f"\n   Full traceback:")
    traceback.print_exc()
    sys.exit(1)

print(f"\nFound {len(jobs)} remote pharmacist jobs")

# Remove duplicates within this scrape (same application_url)
if len(jobs) > 0:
    try:
        # Check if application_url column exists
        if 'application_url' in jobs.columns:
            initial_count = len(jobs)
            jobs = jobs.drop_duplicates(subset=['application_url'], keep='first')
            duplicates_removed = initial_count - len(jobs)
            if duplicates_removed > 0:
                print(f"Removed {duplicates_removed} duplicate jobs (same application_url)")
            print(f"Unique jobs after deduplication: {len(jobs)}")
        else:
            # If application_url doesn't exist yet, use job_url for deduplication
            if 'job_url' in jobs.columns:
                initial_count = len(jobs)
                jobs = jobs.drop_duplicates(subset=['job_url'], keep='first')
                duplicates_removed = initial_count - len(jobs)
                if duplicates_removed > 0:
                    print(f"Removed {duplicates_removed} duplicate jobs (same job_url)")
                print(f"Unique jobs after deduplication: {len(jobs)}")
    except Exception as e:
        print(f"Warning: Error during deduplication: {e}")
        print("Continuing with all jobs...")
    
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
                            if interval_lower in ["hourly", "hour", "hr"]:
                                transformed_job["salary_type"] = "hourly"
                            elif interval_lower in ["yearly", "annual", "year"]:
                                transformed_job["salary_type"] = "yearly"
                            elif interval_lower in ["monthly", "month"]:
                                # Convert to yearly and adjust salary
                                transformed_job["salary_type"] = "yearly"
                                if "salary_min" in transformed_job and transformed_job["salary_min"]:
                                    transformed_job["salary_min"] = transformed_job["salary_min"] * 12
                                if "salary_max" in transformed_job and transformed_job["salary_max"]:
                                    transformed_job["salary_max"] = transformed_job["salary_max"] * 12
                            elif interval_lower in ["weekly", "week"]:
                                # Convert to yearly and adjust salary
                                transformed_job["salary_type"] = "yearly"
                                if "salary_min" in transformed_job and transformed_job["salary_min"]:
                                    transformed_job["salary_min"] = transformed_job["salary_min"] * 52
                                if "salary_max" in transformed_job and transformed_job["salary_max"]:
                                    transformed_job["salary_max"] = transformed_job["salary_max"] * 52
                            elif interval_lower in ["daily", "day"]:
                                # Convert to yearly and adjust salary (260 working days)
                                transformed_job["salary_type"] = "yearly"
                                if "salary_min" in transformed_job and transformed_job["salary_min"]:
                                    transformed_job["salary_min"] = transformed_job["salary_min"] * 260
                                if "salary_max" in transformed_job and transformed_job["salary_max"]:
                                    transformed_job["salary_max"] = transformed_job["salary_max"] * 260
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
                    
                    # Ensure description is never null (required field)
                    if "description" not in transformed_job or not transformed_job.get("description"):
                        transformed_job["description"] = "No description available."

                    # Normalize job_type - must match database check constraint
                    # TEMPORARY: If we can't match known values, remove it to avoid constraint errors
                    # TODO: Update this once we know the exact allowed values from constraint
                    if "job_type" in transformed_job:
                        job_type = transformed_job["job_type"]
                        if job_type:
                            job_type = str(job_type).lower().strip()
                            # Normalize common variations - try to match database constraint
                            # Common allowed values might be: 'full-time', 'part-time', 'contract', etc.
                            if job_type in ["fulltime", "full-time", "full time", "ft", "fulltime"]:
                                transformed_job["job_type"] = "full-time"
                            elif job_type in ["parttime", "part-time", "part time", "pt"]:
                                transformed_job["job_type"] = "part-time"
                            elif job_type in ["contract", "contractor", "contractual"]:
                                transformed_job["job_type"] = "contract"
                            elif job_type in ["temporary", "temp"]:
                                transformed_job["job_type"] = "temporary"
                            elif job_type in ["internship", "intern"]:
                                transformed_job["job_type"] = "internship"
                            elif job_type in ["per-diem", "perdiem", "per diem", "perdiem"]:
                                transformed_job["job_type"] = "per-diem"
                            else:
                                # Unknown value - remove it to avoid constraint violation
                                # Better to have NULL job_type than fail entire insert
                                print(f"   Warning: Unknown job_type '{job_type}', removing to avoid constraint error")
                                transformed_job.pop("job_type", None)
                        else:
                            # Remove if empty
                            transformed_job.pop("job_type", None)

                    # Normalize salary_type - database constraint only allows 'hourly' or 'yearly'
                    # CHECK constraint: salary_type = ANY (ARRAY['hourly'::text, 'yearly'::text])
                    if "salary_type" in transformed_job:
                        salary_type = str(transformed_job.get("salary_type", "")).lower().strip()
                        if salary_type in ["hourly", "hour", "hr", "hrly"]:
                            transformed_job["salary_type"] = "hourly"
                        elif salary_type in ["yearly", "annual", "year", "yr"]:
                            transformed_job["salary_type"] = "yearly"
                        elif salary_type in ["monthly", "month", "mo"]:
                            # Convert monthly to yearly (multiply by 12)
                            transformed_job["salary_type"] = "yearly"
                            if "salary_min" in transformed_job and transformed_job["salary_min"]:
                                transformed_job["salary_min"] = transformed_job["salary_min"] * 12
                            if "salary_max" in transformed_job and transformed_job["salary_max"]:
                                transformed_job["salary_max"] = transformed_job["salary_max"] * 12
                        elif salary_type in ["weekly", "week", "wk"]:
                            # Convert weekly to yearly (multiply by 52)
                            transformed_job["salary_type"] = "yearly"
                            if "salary_min" in transformed_job and transformed_job["salary_min"]:
                                transformed_job["salary_min"] = transformed_job["salary_min"] * 52
                            if "salary_max" in transformed_job and transformed_job["salary_max"]:
                                transformed_job["salary_max"] = transformed_job["salary_max"] * 52
                        elif salary_type in ["daily", "day"]:
                            # Convert daily to yearly (multiply by 260 working days)
                            transformed_job["salary_type"] = "yearly"
                            if "salary_min" in transformed_job and transformed_job["salary_min"]:
                                transformed_job["salary_min"] = transformed_job["salary_min"] * 260
                            if "salary_max" in transformed_job and transformed_job["salary_max"]:
                                transformed_job["salary_max"] = transformed_job["salary_max"] * 260
                        elif not salary_type or salary_type == "none" or salary_type == "null":
                            # Remove salary_type if invalid/empty (let it be NULL)
                            transformed_job.pop("salary_type", None)
                        else:
                            # Unknown value - default to yearly
                            print(f"   Warning: Unknown salary_type '{salary_type}', defaulting to yearly")
                            transformed_job["salary_type"] = "yearly"

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

                    # Map company to company_name if company_name field exists in table
                    # (We'll check allowed_fields later to see if company_name is allowed)
                    if "company" in transformed_job and transformed_job.get("company"):
                        # Try to preserve company name - map to company_name if that field exists
                        # Otherwise we'll remove it since jobs table uses company_id (UUID FK)
                        company_name = transformed_job.get("company")
                        # We'll check if company_name is in allowed_fields below
                        if company_name:
                            transformed_job["company_name"] = company_name
                    
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
                        "company",  # Remove original company field
                        "id",
                        "interval",
                        "scraped_at",
                    ]  # Added interval and scraped_at
                    for field in fields_to_remove:
                        transformed_job.pop(field, None)

                    # Ensure all required fields have values before whitelisting
                    # Description is required (NOT NULL constraint)
                    if "description" not in transformed_job or not transformed_job.get("description"):
                        transformed_job["description"] = "No description available."
                    
                    # Title is likely required
                    if "title" not in transformed_job or not transformed_job.get("title"):
                        transformed_job["title"] = "Untitled Job"
                    
                    # Slug should already be generated, but ensure it exists
                    if "slug" not in transformed_job or not transformed_job.get("slug"):
                        import re
                        title = transformed_job.get("title", "untitled-job")
                        slug = re.sub(r"[^\w\s-]", "", title.lower())
                        slug = re.sub(r"[-\s]+", "-", slug)
                        transformed_job["slug"] = slug[:100] if slug else "untitled-job"
                    
                    # Whitelist only columns that exist in jobs table
                    # Note: If your table has a company_name text field, add it here
                    allowed_fields = {
                        "id",
                        "title",
                        "slug",
                        "description",
                        "company_id",
                        "company_name",  # Add if your jobs table has this field
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
                    
                    # Safety: If job_type or salary_type might violate constraints, remove them
                    # Better to have NULL than fail the entire insert
                    # (We'll fix the exact values once we know the constraints)
                    if "job_type" in final_job and final_job["job_type"]:
                        # Keep it for now, but we'll need to validate against actual constraint
                        pass
                    if "salary_type" in final_job and final_job["salary_type"]:
                        # Already validated above to only be 'hourly' or 'yearly'
                        pass
                    
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
                # Use application_url for conflict resolution (prevents duplicates)
                # Requires unique constraint on application_url - see ADD_UNIQUE_CONSTRAINT.sql
                try:
                    response = supabase.table(table_name).upsert(
                        transformed_jobs,
                        on_conflict="application_url"
                    ).execute()
                except Exception as conflict_error:
                    # If constraint doesn't exist yet, fall back to regular insert
                    if "unique" in str(conflict_error).lower() or "constraint" in str(conflict_error).lower():
                        print(f"   Note: Unique constraint on application_url not found. Run ADD_UNIQUE_CONSTRAINT.sql first.")
                        print(f"   Inserting without conflict resolution (may create duplicates)...")
                        response = supabase.table(table_name).insert(transformed_jobs).execute()
                    else:
                        raise
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
    if len(jobs) > 0 and 'site' in jobs.columns:
        print(f"  Jobs by site:")
        print(jobs['site'].value_counts().to_string())
    else:
        print("  No jobs found or site column missing.")
else:
    print("\nNo jobs found. Try adjusting your search parameters.")

