#!/usr/bin/env python3
"""
Optional field mapping utility for aligning script output with existing schema.
Use this if your Supabase table has different field names.
"""

# Example field mapping dictionary
# If your table uses different column names, map them here
FIELD_MAPPING = {
    # Example mappings (uncomment and modify as needed):
    # "job_url": "url",  # If your table uses "url" instead of "job_url"
    # "company": "company_name",  # If your table uses "company_name"
    # "date_posted": "posted_date",  # If your table uses "posted_date"
}

# Fields that the script sends (for reference)
SCRIPT_FIELDS = [
    "id", "site", "job_url", "job_url_direct", "title", "company", "location",
    "date_posted", "job_type", "salary_source", "interval", "min_amount",
    "max_amount", "currency", "is_remote", "job_level", "job_function",
    "listing_type", "emails", "description", "company_industry", "company_url",
    "company_logo", "company_url_direct", "company_addresses",
    "company_num_employees", "company_revenue", "company_description",
    "skills", "experience_range", "company_rating", "company_reviews_count",
    "vacancy_count", "work_from_home_type", "scraped_at"
]


def map_fields(job_dict, field_mapping=None):
    """
    Maps field names in job_dict according to field_mapping.
    
    Args:
        job_dict: Dictionary with job data
        field_mapping: Dictionary mapping old names to new names
    
    Returns:
        Dictionary with mapped field names
    """
    if not field_mapping:
        field_mapping = FIELD_MAPPING
    
    if not field_mapping:
        return job_dict
    
    mapped_dict = {}
    for key, value in job_dict.items():
        # Use mapped name if exists, otherwise keep original
        new_key = field_mapping.get(key, key)
        mapped_dict[new_key] = value
    
    return mapped_dict


# Example usage (uncomment to test):
# if __name__ == "__main__":
#     sample_job = {
#         "job_url": "https://example.com/job",
#         "company": "Example Corp",
#         "title": "Pharmacist"
#     }
#     mapped = map_fields(sample_job, {"job_url": "url", "company": "company_name"})
#     print(mapped)


