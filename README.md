# Multi-Agent Intelligent Recruitment System 

During this project, I developed a Multi-Agent Intelligent Recruitment System that simulates an AI-powered hiring assistant. The system was built entirely with local, free tools and integrates four agents — candidate profiling, technical assessment design, behavioral analysis, and market intelligence.

I used Python with Streamlit for the UI and also built a CLI for batch runs. The agents work in a modular way, each generating structured outputs like JSON and Markdown reports. To make the project reproducible, I created synthetic candidate profiles, interview transcripts, and market data that the agents can analyze.

The project follows a multi-agent architecture, where each agent is responsible for a distinct stage in the recruitment workflow. The Candidate Profiler ingests candidate information from synthetic_profiles.json and creates structured profiles. The Assessment Designer generates role-specific technical evaluations and outputs them as assessments.json. The Behavioral Analyzer reviews candidate transcripts from transcripts.json and produces soft-skill and behavioral trait reports in behavioral_analysis.json. Finally, the Market Intelligence Agent processes market_compensation.csv to provide salary benchmarks and competitive insights. All of these agents are accessed through Streamlit, which acts as the UI layer for interaction while the modular agents serve as the backend logic.

    JSON files were chosen over a database for simplicity and portability;
    Candidate evaluations are strictly text- and performance-based

## MetaUpSpace_Assignment_DemoVideo_SoumyajitBagchi

# DEMO VIDEO DRIVE LINK: https://drive.google.com/drive/folders/1641vxiRp3ITREngTFnCGn-GJkstyBK6Y?usp=drive_link

## LIVE APPLICATION LINK: http://192.168.31.178:8501 [Strea]

#Few screenshot of the Streamlit Live Project
<img width="1917" height="966" alt="image" src="https://github.com/user-attachments/assets/25821ce5-3650-4860-bf1e-00561021e798" />
<img width="1906" height="895" alt="image" src="https://github.com/user-attachments/assets/078132ba-583e-49f9-be1a-f8c88957f494" />
<img width="1919" height="1022" alt="image" src="https://github.com/user-attachments/assets/bd79ecbd-f1dd-4cb1-a919-0855f1c89b90" />


<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/8749caaf-4fd8-4f13-b0f9-09d442fa0ec1" />
