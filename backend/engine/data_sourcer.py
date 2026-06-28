import asyncio
from duckduckgo_search import AsyncDDGS
import logging

logger = logging.getLogger(__name__)

class DataPreFetcher:
    def __init__(self):
        self.max_results = 3

    async def _search(self, query: str) -> list[dict]:
        """Helper to run async duckduckgo search and format results."""
        results = []
        try:
            async with AsyncDDGS() as ddgs:
                async for r in ddgs.text(query, max_results=self.max_results):
                    results.append({
                        "title": r.get("title"),
                        "url": r.get("href"),
                        "snippet": r.get("body")
                    })
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
        return results

    def _format_results(self, results: list[dict], source_type: str) -> list[dict]:
        """Formats raw search results for the prompt builder."""
        formatted = []
        for r in results:
            formatted.append({
                "source_type": source_type,
                "title": r["title"],
                "url": r["url"],
                "content": r["snippet"]
            })
        return formatted

    async def fetch_statutes(self, jurisdiction: str, crime_type: str) -> list[dict]:
        query = f"official penal code statute {jurisdiction} {crime_type}"
        results = await self._search(query)
        return self._format_results(results, "Official Statute Code")

    async def fetch_sentencing_stats(self, jurisdiction: str, crime_type: str) -> list[dict]:
        query = f"sentencing commission statistics report {jurisdiction} {crime_type} average sentence"
        results = await self._search(query)
        return self._format_results(results, "Sentencing Commission Report")

    async def fetch_comparable_jurisdictions(self, crime_type: str) -> list[dict]:
        # The prompt specifically demands UK, Canada, Australia, Germany, Sweden
        query = f"international sentencing guidelines {crime_type} UK Canada Australia Germany Sweden"
        results = await self._search(query)
        return self._format_results(results, "International Legal Precedent")

    async def fetch_behavioral_research(self, defendant_context: str) -> list[dict]:
        # defendant_context might contain age or mental health notes
        query = f"behavioral psychology recidivism risk rehabilitation {defendant_context}"
        results = await self._search(query)
        return self._format_results(results, "Behavioral Psychology Journal")

    async def fetch_bias_studies(self, jurisdiction: str, crime_type: str) -> list[dict]:
        query = f"racial socioeconomic sentencing disparity bias study {jurisdiction} {crime_type}"
        results = await self._search(query)
        return self._format_results(results, "Criminology Bias Study")

    async def prefetch_all(self, case_dict: dict) -> dict:
        """
        Runs all searches concurrently.
        case_dict should contain: 'jurisdiction', 'crime_type', 'defendant_profile'
        """
        jurisdiction = case_dict.get("jurisdiction", "")
        crime = case_dict.get("crime_type", "")
        profile = case_dict.get("defendant_profile", "")

        statutes_task = self.fetch_statutes(jurisdiction, crime)
        stats_task = self.fetch_sentencing_stats(jurisdiction, crime)
        comp_task = self.fetch_comparable_jurisdictions(crime)
        behav_task = self.fetch_behavioral_research(profile)
        bias_task = self.fetch_bias_studies(jurisdiction, crime)

        # Run all 5 searches in parallel
        results = await asyncio.gather(
            statutes_task, stats_task, comp_task, behav_task, bias_task
        )

        return {
            "statutes": results[0],
            "sentencing_data": results[1],
            "comparable_jurisdictions": results[2],
            "behavioral_research": results[3],
            "bias_studies": results[4]
        }
