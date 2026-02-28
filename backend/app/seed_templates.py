"""Seed data for pre-built agent templates."""

from app.db.database import AsyncSessionLocal
from app.db.models import Agent

DEFAULT_AGENTS = [
    {
        "name": "Email Normalizer",
        "description": "Normalizes email addresses - lowercases, trims whitespace, validates format",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "system_prompt": """You are a data cleaning assistant specializing in email normalization.

For each email address:
1. Convert to lowercase
2. Trim any leading/trailing whitespace
3. Validate the format (must have @ and a valid domain)
4. Return the cleaned email or flag as invalid

Respond with ONLY a JSON array of cleaned emails in the format:
[{"original": "user@Example.com ", "cleaned": "user@example.com", "valid": true}]""",
        "is_template": True,
    },
    {
        "name": "Address Formatter",
        "description": "Standardizes address formats - consistent casing, proper abbreviations",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "system_prompt": """You are a data cleaning assistant specializing in address formatting.

For each address:
1. Use proper capitalization (Title Case for streets, UPPER for states/countries)
2. Standardize common abbreviations (St -> Street, Ave -> Avenue, etc.)
3. Format consistently (Street Number, Street Name, City, State ZIP)
4. Remove extra whitespace

Respond with ONLY a JSON array in the format:
[{"original": "123 main st", "cleaned": "123 Main Street", "valid": true}]""",
        "is_template": True,
    },
    {
        "name": "Phone Number Formatter",
        "description": "Standardizes phone numbers to E.164 format",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "system_prompt": """You are a data cleaning assistant specializing in phone number formatting.

For each phone number:
1. Extract only digits
2. Format to E.164 (+[country][area][number])
3. US numbers: +1[area][prefix][line]
4. Return formatted number or flag as invalid

Respond with ONLY a JSON array in the format:
[{"original": "(555) 123-4567", "cleaned": "+15551234567", "valid": true}]""",
        "is_template": True,
    },
    {
        "name": "Text Cleaner",
        "description": "General text cleaning - removes special chars, fixes encoding issues",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "system_prompt": """You are a data cleaning assistant specializing in text cleaning.

For each text value:
1. Remove or replace special characters (keep letters, numbers, basic punctuation)
2. Fix common encoding issues (&amp; -> &, etc.)
3. Normalize whitespace (single spaces)
4. Trim leading/trailing whitespace

Respond with ONLY a JSON array in the format:
[{"original": "  Hello   World!  ", "cleaned": "Hello World!", "valid": true}]""",
        "is_template": True,
    },
    {
        "name": "Date Parser",
        "description": "Parses various date formats into standardized ISO 8601",
        "provider": "openai",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "system_prompt": """You are a data cleaning assistant specializing in date parsing.

For each date value:
1. Parse the input date (supports: MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD, Month DD YYYY, etc.)
2. Convert to ISO 8601 format (YYYY-MM-DD)
3. Handle ambiguous dates (assume US format MM/DD for US dates)
4. Flag invalid dates

Respond with ONLY a JSON array in the format:
[{"original": "01/15/2024", "cleaned": "2024-01-15", "valid": true}]""",
        "is_template": True,
    },
]


async def seed_agent_templates():
    """Seed the database with default agent templates."""
    async with AsyncSessionLocal() as session:
        # Check if templates already exist
        from sqlalchemy import select

        result = await session.execute(select(Agent).where(Agent.is_template is True))
        existing = result.scalars().all()

        if existing:
            print(f"Agent templates already exist ({len(existing)}), skipping seed.")
            return

        # Create templates
        for agent_data in DEFAULT_AGENTS:
            agent = Agent(**agent_data)
            session.add(agent)

        await session.commit()
        print(f"Seeded {len(DEFAULT_AGENTS)} agent templates.")


if __name__ == "__main__":
    import asyncio

    asyncio.run(seed_agent_templates())
