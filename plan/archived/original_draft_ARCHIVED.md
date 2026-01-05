# ARCHIVED - ORIGINAL REQUIREMENTS

> **AI AGENTS: REFERENCE ONLY**
>
> This document contains the **original project requirements** and is preserved for historical context.
> Many requirements have been implemented or adjusted since this was written.
>
> For current project status and what remains to be done, see:
> - `/plan/CURRENT_PLAN.md` - Active project plan and status
> - `/CLAUDE.md` - Development instructions
>
> **Archived Date:** 2026-01-05
> **Status:** Requirements document - use for understanding original intent only

---

*Original requirements preserved below*

---

Hybrid PV + BESS vs standalone BESS

Prompt for Claude:
THIS TASK WILL REQUIRE DETAILED PLANNING. THERE ARE A NUMBER OF COMPLEX TASKS WHICH EACH NEED TO BE PLANNED IN SEPARATE SUB-PLANS WITH A REFRESHED CONTEXT WINDOW. PLEASE DESIGN A DETAILED PLAN WITH SEPARATE SUB-PLANS WHICH CAN BE DEVELOPED IN PARALLEL. ONLY PLAN NOW, DO NOT WRITE ANY CODE.
I need your help to create a detailed blogpost / report. This will be hosted on github pages using Shiny. The report will use interactive charts and tables generated in python. I want the code for each of the charts and tables to be saved in a .py file in the github repo so that readers can see how I have generated the analysis and follow along.
Please set up the folder structure and files here C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Git\Hybrid_PV_Blog so that we can publish to github and see the website, and all our analysis is organised.
Charts will generally be interactive, i.e. users can hover over and see lables. We will need to create a consistent style guide. The font can be Lato, and we will need to make a professional but modern colour palette where solar PV is yellow, wind is green, battery is purple in charts. I like teal as a colour also.
There are two niche python packages which we will be using for the analysis, NEMOSIS and PyPSA.

Please see the files C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Context\NEMOSIS_skillv2.docx and C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Context\combined_files.txt for examples of NEMOSIS. Please create a NEMOSIS skill which you can reference. Please note that all NEMOSIS energy market data is saved (and needs to be saved) to this folder C:\Users\matts\Documents\Aus research\Nemosis_data. Please generate a Nemosis skill file that you can reference in future.

Please see this folder C:\Users\matts\Documents\Aus research\Gen modelling\PyPSA for PyPSA. Ignore the outputs and ts_outputs folder. Please generate a PyPSA skill file that you can reference in the future.

I am setting out the draft of the report. Bullets show the text but are rough and will be refined. However, my aim is to avoid verbosity and for the report to be snappy.

 ---ANALYSIS--- is a tag for when there will be a graphic, table or chart. [FOR CLAUDE: ] will denote the analysis steps required to develop the chart

Note that you are using windows. The python environment hybridpv is a mamba environment and is located at C:\Users\matts\miniforge3\envs\hybridpv
Please use the userinterview tool to ask me lots of questions about the plan and project. Then develop a detailed plan to work on this. I will review and amend.

---

*[Full original requirements document preserved - see git history for complete content]*
