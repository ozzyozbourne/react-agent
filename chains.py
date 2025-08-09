from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
import os

llm = ChatOpenAI(
    api_key=SecretStr(os.environ["OPENROUTER_API_KEY"]),
    base_url=os.environ["OPENROUTER_BASE_URL"],
    model=os.environ["MODEL_NAME"],
)

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert security auditor specializing in code review and vulnerability assessment.
            Your role is to critically analyze the previous security assessment and provide deeper insights.

            Focus on:
            - Identifying any missed vulnerabilities or security issues
            - Evaluating the severity and exploitability of identified issues
            - Suggesting additional attack vectors that weren't considered
            - Providing more comprehensive remediation strategies
            - Considering edge cases and advanced attack scenarios

            Be thorough, technical, and prioritize findings by risk level.
            Use industry standards like OWASP Top 10, CWE classifications when relevant."""
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a senior security engineer performing a comprehensive code security audit.
            Analyze the provided code for security vulnerabilities and potential risks.

            Your analysis should cover:
            1. **Critical Vulnerabilities**: SQL injection, command injection, XSS, authentication bypass, etc.
            2. **High-Risk Issues**: Insecure deserialization, XXE, SSRF, path traversal, etc.
            3. **Medium Risks**: Weak cryptography, information disclosure, improper error handling
            4. **Low Risks**: Best practice violations, potential future vulnerabilities
            5. **Code Quality Issues**: That could lead to security problems

            For each issue found:
            - Explain the vulnerability and its potential impact
            - Provide proof-of-concept or exploitation scenario if applicable
            - Suggest specific remediation with code examples
            - Rate severity (Critical/High/Medium/Low)

            Also consider the code's context, dependencies, and deployment environment.
            If reviewing previous assessments, build upon them with new findings or refined analysis."""
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

generate_chain = generation_prompt | llm
reflect_chain = reflection_prompt | llm
