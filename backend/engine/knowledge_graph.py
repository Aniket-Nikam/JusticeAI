import logging
from neo4j import AsyncGraphDatabase

import os

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password=None):
        self.uri = uri
        self.user = user
        self.password = password or os.getenv("NEO4J_PASSWORD")
        self.driver = None

    async def connect(self):
        try:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            await self.driver.verify_connectivity()
            logger.info("Connected to Neo4j Knowledge Graph successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def seed_test_data(self):
        """Seeds the graph with dummy precedent data for testing."""
        if not self.driver:
            await self.connect()

        queries = [
            "MATCH (n) DETACH DELETE n",
            "CREATE (ca:Jurisdiction {name: 'California', country: 'USA'})",
            "CREATE (ny:Jurisdiction {name: 'New York', country: 'USA'})",
            "CREATE (sa:CrimeType {name: 'Sexual Assault', severity_tier: 1})",
            "CREATE (tf:CrimeType {name: 'Theft', severity_tier: 3})",
            "CREATE (j1:Judge {name: 'Aaron Persky', bias_score: 0.8})",
            "CREATE (j2:Judge {name: 'Jane Doe', bias_score: 0.2})",
            "CREATE (c1:Case {id: 'CA-2015-101', description: 'University athlete sexual assault', actual_months: 6})",
            "CREATE (c2:Case {id: 'CA-2018-402', description: 'Non-athlete sexual assault', actual_months: 84})",
            "MATCH (c:Case {id: 'CA-2015-101'}), (ca:Jurisdiction {name: 'California'}) CREATE (c)-[:IN_JURISDICTION]->(ca)",
            "MATCH (c:Case {id: 'CA-2015-101'}), (sa:CrimeType {name: 'Sexual Assault'}) CREATE (c)-[:OF_CRIME_TYPE]->(sa)",
            "MATCH (c:Case {id: 'CA-2015-101'}), (j:Judge {name: 'Aaron Persky'}) CREATE (c)-[:SENTENCED_BY]->(j)",
            "MATCH (c:Case {id: 'CA-2018-402'}), (ca:Jurisdiction {name: 'California'}) CREATE (c)-[:IN_JURISDICTION]->(ca)",
            "MATCH (c:Case {id: 'CA-2018-402'}), (sa:CrimeType {name: 'Sexual Assault'}) CREATE (c)-[:OF_CRIME_TYPE]->(sa)",
            "MATCH (c:Case {id: 'CA-2018-402'}), (j:Judge {name: 'Jane Doe'}) CREATE (c)-[:SENTENCED_BY]->(j)"
        ]
        
        try:
            async with self.driver.session() as session:
                for q in queries:
                    await session.run(q)
                logger.info("Knowledge Graph seeded with test precedent data.")
        except Exception as e:
            logger.error(f"Failed to seed Neo4j: {e}")

    async def find_precedents(self, crime_type: str, jurisdiction: str):
        """Finds historical cases for a specific crime in a specific jurisdiction."""
        if not self.driver:
            await self.connect()
            
        query = """
        MATCH (c:Case)-[:OF_CRIME_TYPE]->(ct:CrimeType {name: $crime_type})
        MATCH (c)-[:IN_JURISDICTION]->(j:Jurisdiction {name: $jurisdiction})
        MATCH (c)-[:SENTENCED_BY]->(judge:Judge)
        RETURN c.id as case_id, c.actual_months as months, judge.name as judge, judge.bias_score as bias
        """
        try:
            async with self.driver.session() as session:
                result = await session.run(query, crime_type=crime_type, jurisdiction=jurisdiction)
                records = await result.data()
                return records
        except Exception as e:
            logger.error(f"Failed to query Neo4j: {e}")
            return []
