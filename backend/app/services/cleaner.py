"""AI-powered data cleaning assistant."""

from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.services.ai_provider import AIProvider, get_chat_model

SYSTEM_PROMPT = """You are an expert data cleaning assistant for MasterDataCleaner.

Your role is to help users:
1. Analyze data quality issues (missing values, duplicates, format inconsistencies)
2. Suggest appropriate cleaning operations
3. Generate cleaning code/scripts when requested
4. Explain data transformations

When analyzing data:
- Identify patterns and anomalies
- Recommend specific cleaning steps
- Consider data types and business context
- Preserve data integrity

Be concise but thorough. Provide actionable recommendations."""


class DataCleaningAssistant:
    """AI assistant for data cleaning guidance."""

    def __init__(
        self,
        provider: AIProvider = AIProvider.OPENAI,
        model: Optional[str] = None,
        temperature: float = 0.3,
    ):
        """
        Initialize the data cleaning assistant.

        Args:
            provider: AI provider to use
            model: Specific model name (uses default if not provided)
            temperature: Sampling temperature (lower = more deterministic)
        """
        self.llm = get_chat_model(provider, model, temperature)
        self.provider = provider
        self.model = model

    async def analyze_data(self, data_summary: str) -> str:
        """
        Analyze data and provide cleaning recommendations.

        Args:
            data_summary: Summary/description of the data to analyze

        Returns:
            Analysis and recommendations
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "Analyze this data and recommend cleaning steps:\n\n{data}"),
        ])

        chain = prompt | self.llm
        response = await chain.ainvoke({"data": data_summary})
        return response.content

    async def suggest_fix(self, issue_description: str) -> str:
        """
        Suggest how to fix a specific data quality issue.

        Args:
            issue_description: Description of the data issue

        Returns:
            Suggested fix
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "How should I fix this data quality issue?\n\n{issue}"),
        ])

        chain = prompt | self.llm
        response = await chain.ainvoke({"issue": issue_description})
        return response.content

    async def generate_code(self, task_description: str, language: str = "python") -> str:
        """
        Generate code for a data cleaning task.

        Args:
            task_description: Description of the cleaning task
            language: Programming language (default: python)

        Returns:
            Generated code
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", "Generate {language} code for this data cleaning task:\n\n{task}"),
        ])

        chain = prompt | self.llm
        response = await chain.ainvoke({"language": language, "task": task_description})
        return response.content

    async def chat(self, message: str) -> str:
        """
        General chat with the assistant.

        Args:
            message: User message

        Returns:
            Assistant response
        """
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=message),
        ]
        response = await self.llm.ainvoke(messages)
        return response.content
