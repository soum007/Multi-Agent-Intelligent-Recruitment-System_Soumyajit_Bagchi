# Multi-Agent Intelligent Recruitment System 

During this project, I developed a Multi-Agent Intelligent Recruitment System that simulates an AI-powered hiring assistant. The system was built entirely with local, free tools and integrates four agents — candidate profiling, technical assessment design, behavioral analysis, and market intelligence.

I used Python with Streamlit for the UI and also built a CLI for batch runs. The agents work in a modular way, each generating structured outputs like JSON and Markdown reports. To make the project reproducible, I created synthetic candidate profiles, interview transcripts, and market data that the agents can analyze.

The project follows a multi-agent architecture, where each agent is responsible for a distinct stage in the recruitment workflow. The Candidate Profiler ingests candidate information from synthetic_profiles.json and creates structured profiles. The Assessment Designer generates role-specific technical evaluations and outputs them as assessments.json. The Behavioral Analyzer reviews candidate transcripts from transcripts.json and produces soft-skill and behavioral trait reports in behavioral_analysis.json. Finally, the Market Intelligence Agent processes market_compensation.csv to provide salary benchmarks and competitive insights. All of these agents are accessed through Streamlit, which acts as the UI layer for interaction while the modular agents serve as the backend logic.

    JSON files were chosen over a database for simplicity and portability;
    Candidate evaluations are strictly text- and performance-based


#DEMO VIDEO DRIVE LINK: 

## LIVE APPLICATION LINK:
