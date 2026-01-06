-- Supabase Database Schema for Pharmacist Jobs
-- Run this in the Supabase SQL Editor

-- Create table for pharmacist jobs
CREATE TABLE IF NOT EXISTS pharmacist_jobs (
    id TEXT PRIMARY KEY,
    site TEXT,
    job_url TEXT UNIQUE NOT NULL,
    job_url_direct TEXT,
    title TEXT,
    company TEXT,
    location TEXT,
    date_posted DATE,
    job_type TEXT,
    salary_source TEXT,
    interval TEXT,
    min_amount NUMERIC,
    max_amount NUMERIC,
    currency TEXT,
    is_remote BOOLEAN,
    job_level TEXT,
    job_function TEXT,
    listing_type TEXT,
    emails TEXT,
    description TEXT,
    company_industry TEXT,
    company_url TEXT,
    company_logo TEXT,
    company_url_direct TEXT,
    company_addresses TEXT,
    company_num_employees TEXT,
    company_revenue TEXT,
    company_description TEXT,
    skills TEXT,
    experience_range TEXT,
    company_rating NUMERIC,
    company_reviews_count INTEGER,
    vacancy_count INTEGER,
    work_from_home_type TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index on job_url for faster lookups
CREATE INDEX IF NOT EXISTS idx_job_url ON pharmacist_jobs(job_url);

-- Create index on scraped_at for querying recent jobs
CREATE INDEX IF NOT EXISTS idx_scraped_at ON pharmacist_jobs(scraped_at);

-- Create index on company for filtering
CREATE INDEX IF NOT EXISTS idx_company ON pharmacist_jobs(company);

-- Create index on date_posted for filtering by date
CREATE INDEX IF NOT EXISTS idx_date_posted ON pharmacist_jobs(date_posted);

-- Enable Row Level Security (RLS)
ALTER TABLE pharmacist_jobs ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows anyone to read (adjust based on your needs)
CREATE POLICY "Allow public read access" ON pharmacist_jobs
    FOR SELECT USING (true);

-- Create a policy that allows service role to insert/update
-- Note: For GitHub Actions, you'll use the anon key, so adjust this policy
CREATE POLICY "Allow anon insert/update" ON pharmacist_jobs
    FOR ALL USING (true);

-- Optional: Create a view for recent jobs (last 7 days)
CREATE OR REPLACE VIEW recent_pharmacist_jobs AS
SELECT *
FROM pharmacist_jobs
WHERE scraped_at > NOW() - INTERVAL '7 days'
ORDER BY scraped_at DESC;


