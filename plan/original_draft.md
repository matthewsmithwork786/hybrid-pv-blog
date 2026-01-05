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
Purpose and summary of the report (not a section of the report)
•	The report is meant to help renewable energy developers and infrastructure investors understand how to decide whether BESS should be collocated with PV plants.
•	It is focused on the Australian market, particularly the NEM. The audience are professional investors and renewable energy operators. In particular, I am focusing on infrastructure investors who need to contract the majority of revenue and who use project finance, rather than those interested in pure merchant exposure.
•	This is an interesting topic because the market is changing. Now that renewable energy penetration has increased, daytime (solar hour) power prices have collapsed. There are also issues with curtailment. Investors in solar would like to contract their power so that they are not exposed to this risk, but there is little appetite for plain solar. 
•	At the same time, batteries have grown rapidly. Batteries can help solve this because they shift power from day time to higher priced hours. 
•	However, batteries do not need to be co-located with solar PV to do this. It often makes more sense for the batteries to be located separately so that:
o	They can charge from cheap or negatively priced power, earning money that way
o	They can be located in areas of the grid which are unconstrained, so they can earn money for grid services and so they don’t need to worry about their output being restricted.
•	However there are good reasons for BESS to co-located with solar PV rather than be standalone:
o	There are infrastructure cost savings by saving a grid connection, design and planning approvals
o	For infrastructure investors and developers, they want to build a more capex heavy system, so they can earn a return on a bigger investment. BESS only is asset light
o	Locking in the BESS power supply could reduce the (small) risk of power prices going up
o	A combined product which is guaranteed green and ‘additional’ could be more attractive to offtakers who have green requirements.
•	In this report I want show a framework for analysing whether to co-locate PV with batteries or not. The framework will be:
o	Determine your return requirements for standalone BESS vs co-located BESS. Do you have operational PV which is going to be uncontracted soon? Adding BESS may be needed to make revenue contracted and prevent merchant exposure. So you may be willing to make a lower return on the BESS to solve this problem.
o	Are there potential efficiency / cost saving benefits for co-locating? These can be quantified and added to the model.
o	Is the location you are looking at for the co-located PV BESS in an area with grid constraints and Marginal Loss Factors. The impact on revenue, especially potential merchant revenue, needs to be quantified.
o	Determine your contracting options. Will the BESS be fully contracted at a fixed price or volume? What is the merchant exposure and other revenue options?
o	Evaluate the options by modelling both a standalone BESS and co-located PV & BESS using PyPSA to run a number of sizing options.
o	Use capex assumptions, price assumptions, to run a financial model for these options and see the return. Compare the returns to your benchmark return requirement.


REPORT OUTLINE STARTS HERE:

Report Title: Beyond the Solar Curve: A Capital Allocation Framework for Co-located vs. Standalone BESS in the NEM
Section 1: The Investment Problem (The End of "Plain" Solar)
Context: Why the historical investment model for PV is broken and why capital must pivot.
1.1 The Collapse of the Unfirmed PPA
Utility-scale RE assets in the NEM have historically relied on fixed-price contracts of 7–15 years. These allowed developers to secure high-leverage, long-term project finance.
With the end of the LRET and increasing "solar anti-correlation" (price cannibalization), the value of PV in daytime hours has collapsed. It has become increasingly difficult to secure the long-term PPAs required for debt sizing.
The Curtailment Risk: Investors are not just facing low prices, but physical curtailment due to grid congestion during solar peaks.
---ANALYSIS---
Column chart showing the average annual wholesale price between the hours of 1000 – 1600 in NSW from 2018 to 2025. On a secondary axis, plot the curtailment for solar PV plants in NSW over the same period.
[FOR CLAUDE: Use NEMOSIS to download annual prices for the period, filter for the hours and NSW, and create the chart. For curtailment, see the code in C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Context\Hybridpv_Gen curt NSW.ipynb]
/ ---ANALYSIS---
1.2 The Certificate Cliff
LGC certificate prices have also dropped as the obligation has been fulfilled, from an average of $50 in Jan 2024 to $6.50 in Jan 2026.
Navigating LGC market trends: prices are at all-time lows, and the market transitions to a voluntary scheme post-2030.
Regulatory Uncertainty: There is general uncertainty regarding the planned replacement scheme, Guarantees of Origins (GOs). GOs will have a time-stamp element allowing offtakers to buy certificates matching the exact time of consumption. Just as physical PV is oversupplied, solar-hour GOs will likely be oversupplied, depressing their value.
Section 2: The BESS Integration Thesis
Context: BESS is the obvious technical solution, but the commercial implementation is split.
2.1 Restoring Value
Battery storage offers a path forward for PV assets. Adding BESS to a PV farm can shift generation to predictable, high-value times, providing price support.
Behind-the-meter BESS can physically protect PV from daytime curtailment, converting "waste" into revenue.
2.2 The Investor Dilemma
While BESS solves the intermittency issue, it does not need to be co-located to do so.
The market is splitting into two distinct asset classes:
Standalone BESS: Optimizing for location, grid services, and arbitrage (contracted or merchant).
Co-located (Hybrid): Optimizing for infrastructure efficiency, firming, and "green" product creation.
For new investors, the question is: Does the PV plant add value to the BESS, or is it a sunk cost dragging down the battery's potential?
Section 3: The Trade-Off Analysis (Standalone vs. Co-located)
Context: A direct comparison of the two deployment models.
3.1 The Case for Standalone (Flexibility & Location)
Utility-scale batteries are now a key part of the NEM. Growth is driven by steep cost reductions, modularity, and rapid installation timelines.
---ANALYSIS---
Column chart showing the MWH of batteries installed across the NEM from 2018 to 2025, including the committed and anticipated numbers from 2026 onwards.
[FOR CLAUDE: Take the data from sheet ExistingGeneration&NewDevs in C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Context\NEM Generation Information Oct 2025.xlsx to make a chart like the below image. ‘NEM BESS plants MWh by year.png’]
/ ---ANALYSIS---
Currently, the majority of batteries in the NEM are standalone. This allows them to act as a separate asset class, capable of charging from the grid whenever prices are lowest (or negative).
Correction to common misconception: Standalone BESS are not solely merchant/volatility plays. They can be fully contracted (e.g., tolling agreements, stiff grid services), but their physical location is chosen to maximize these independent revenue streams rather than accommodate a solar farm.
---ANALYSIS---
Interactive map of Battery storage facilities across the NEM. Here, we want to show whether the BESS is standalone or co-located. We’ll define co-located as ‘within 1km of a solar PV facilitiy’
[FOR CLAUDE: see C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Context\Hybridpv_NSWGeneratorMap.ipynb for an example of how to generate the map of generators. An extra layer of analysis will need to be added to calculate whether the BESS is within 1 km of a solar PV facility. The ‘standalone’ BESS should be purple and the ‘co-located’ BESS should be dark orange.]
/---ANALYSIS---
Strategic Advantages of Standalone:
Siting Freedom: Ability to site BESS in regions with better Marginal Loss Factors (MLFs) or specific congestion zones to capture FCAS value.
Speed: Quicker time to installation. BESS permitting and construction in Australia can take [X – Y months] vs [Z – A months] for a PV plant.
[FOR CLAUDE: Please research and find sources, ideally from sources like AEMO, the Australian energy regulator, Modo Energy, etc)]
Augmentation Cycles: No need to align lifetimes. BESS often need replacement/augmentation after 15–20 years, whereas PV lasts 30–35 years. Standalone avoids the complexity of mismatched asset lifespans.
Negative Pricing Revenue: Ability to generate revenue by charging during negative price periods (getting paid to charge). Co-located plants can typically only do this if they are willing to curtail their own generation to make room for grid imports.
---ANALYSIS---
Column chart showing percentage of achieved revenue for batteries in NSW which were operational for the full year (2025), by price bucket. X axis will be price bucket (market price 
/
M
W
h
,
s
t
a
r
t
i
n
g
a
t
<
−
/MWh,startingat<−
1000, going to >$2000 in perhaps 6 reasonable buckets).
[FOR CLAUDE: the aim here is to show how much theoretical merchant revenues batteries in NSW made from charging during negative prices in 2025. See the code at C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Context\hyridpv_pricerevskew.ipynb however amend it so it is only looking at batteries which were operated for the whole of 2025, and looks at net revenue, i.e. flows from both charging and discharging]
/---ANALYSIS---
3.2 The Case for Co-located (Capital Efficiency & Product Definition)
Definition: We define co-located batteries as physically connected to a PV asset, though the relationship can be contractual.
Integration Models:
[FOR CLAUDE: Please re-create the diagram below using the python packages graphviz, diagrams, schemdraw, and appropriate icons sourced from the web when necessary. Please show multiple options which I can choose between
‘Modo BESS Colocated options diagram.png’ ]
While theoretical revenue may be lower than an optimized standalone asset (as per mdavis, "Why Colocating solar and batteries does not increase electricity spot market revenue"), infrastructure investors may prioritize the following benefits:
Capex Synergies: Shared grid connection, electrical infrastructure, land, and development costs (planning/permitting).
Capital Deployment: Investors can build a more capex-heavy system, deploying larger checks into a single project to earn a return on a larger asset base.
Operational Efficiencies: O&M savings from a single site; co-optimizing network charges and ancillary services (Yang et al., 2021).
Grid Access: A hybrid plant (especially DC-coupled) may gain approval in constrained areas where a PV-only plant would fail, as the BESS adds stability to the network operator.
The "Green" Premium: A co-located product is arguably "guaranteed green" and "additional." This attracts offtakers with strict ESG requirements who want a shaped renewable profile, not just brown power from the grid backed by certificates.
CIS Eligibility: Co-located plants are eligible for specific Capacity Investment Scheme contracts, reducing financing risk.
The Retrofit Logic: For investors with existing PV portfolios, co-location is a defensive move. It deploys capital quickly and reduces the PV asset's exposure to merchant tail risk/curtailment, effectively "preserving" the original IRR.
Section 4: The Technical Constraints (Grid & MLFs)
Context: The "Hidden Killers" of returns. Why simply adding a battery to a solar farm can destroy value.
4.1 Revenue Skew & Sensitivity
Batteries are extremely sensitive to high price events. Using the simplifying assumption that the only source of revenue is price arbitrage, they would have made X% of their annual revenue in Y hours.
---ANALYSIS---
[FOR CLAUDE: Price skew – show the % of revenue made in 2025 by batteries by hour of operation. So X% was made in the first 10% of hours, Y% in the next 10% of hours. Please see C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Context\hyridpv_pricerevskew.ipynb and made the necessary amendments]
/---ANALYSIS---
4.2 The MLF Trap
Because of this sensitivity to specific pricing windows, Grid Constraints and Marginal Loss Factors (MLFs) are critical. Solar farms are often located in areas with poor MLFs (end of line).
If a battery is co-located at a site with a poor MLF, it is penalized on both import and export, potentially destroying the arbitrage spread.
---ANALYSIS---
[FOR CLAUDE: We need to re-create this analysis for batteries operational over the whole of 2025, using NEMOSIS data. Please see C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Context\NEMOSIS prompt_Curtailment and MLFs.md for suggestions on how to calculate this.
‘Modo BESS revenue MLF constraints.jpg’
Even big batteries are falling victim to grid bottlenecks
/---ANALYSIS---
---ANALYSIS---
Map of NSW showing the MLFs of each grid connection point. Something like this:
‘NEM map MLFs.png’
[FOR CLAUDE: Please consider how this can be done. If there is no MLF map for grid connection points or regions 2025, calculate it for all generators using ideas from C:\Users\matts\Documents\Aus research\Hybrid PV BESS vs standalone\Code\Context\NEMOSIS prompt_Curtailment and MLFs.md. Then map the MLFs of the generators as points.]
/---ANALYSIS---
Section 5: The Strategic Framework (The Decision)
Context: A step-by-step logic flow for investors to determine the correct configuration.
Step 1: Determine the Hurdle Rate & Benchmark
New Build: Are you comparing to a standalone BESS? What are the contracting options (Risk-Adjusted Return)?
Retrofit: Are you comparing to a downside case of uncontracted/curtailed PV? (A lower BESS return may be acceptable if it saves the PV valuation).
Step 2: Quantify Efficiencies
Calculate Capex & O&M savings from co-location.
Step 3: Determine Contracting Options
Will the BESS be fully contracted (Fixed Price/Volume)?
Is there a "Green Premium" available for confirmed solar-charged power (GOs/RECs)?
What is the merchant exposure?
Step 4: Location Viability
Assess the site for grid constraints and MLFs. Does the location support the high-peak discharge required for the business case?
[FOR CLAUDE: Organise and refine this, it needs work. Once it is complete, we will turn this into a decision tree diagram using something like dtreeviz. ]
Step 5: Modelling & Validation
Operational Model: Use PyPSA to simulate dispatch of co-located vs. standalone BESS under various sizing options.
Financial Model: Input capex and price assumptions to calculate Levered IRR. Compare against the benchmark determined in Step 1.
