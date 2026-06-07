# TODO

## Security
- [ ] Rotate the EIA API key. The old key was hardcoded in the forecast model scripts and is present in git history.
  - Create a new key at https://www.eia.gov/opendata/
  - Update `.env` locally with the new key
  - Consider using `git-filter-repo` or similar to purge the old key from history if this repo becomes public

## Deployment
- [ ] Choose a hosting platform (Render, Vercel, Fly.io, etc.)
- [ ] Set up environment variables on the hosting platform:
  - `OPENAI_API_KEY`
  - `EIA_API_KEY` (only needed if re-running forecast models)
- [ ] Configure CORS in `backend/main.py` for production frontend domain
- [ ] Add health check endpoint monitoring

## Enhancements
- [ ] Add caching layer (e.g., Redis) for OpenAI recommendations
- [ ] Add rate limiting to the recommendations endpoint
- [ ] Implement pagination or search suggestions for the search endpoint
- [ ] Add building comparison feature
- [ ] Add export to PDF/CSV for dashboard reports

## Data Pipeline
- [ ] Automate ETL runs with a scheduler (GitHub Actions cron or similar)
- [ ] Add data validation checks between pipeline steps
- [ ] Version the generated CSVs or migrate to a lightweight database (SQLite/PostgreSQL)
