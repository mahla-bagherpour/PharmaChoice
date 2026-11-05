import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="PharmaChoice | Research Decision Lab", page_icon="💊", layout="wide")

st.markdown("""<style>
.block-container {padding-top: 2rem; max-width: 1150px;}
[data-testid="stMetricValue"] {font-weight: 700;}
.hero {padding: 1.3rem 1.6rem; background: linear-gradient(110deg,#142942,#294d65);
color:#fff; border-radius:15px; margin-bottom:1.2rem;}
.hero h1 {color:#fff; margin:0 0 .2rem 0;}
.hero p {color:#dce9f0; margin:0;}
.small-note {font-size:.88rem;color:#657181;}
</style>""", unsafe_allow_html=True)

CASES = [
    {
      "name":"01 · Corticosteroid Response in Asthma", "tag":"Pharmacodynamics · Clinical evidence",
      "research":"Chalmers et al. (2002) randomized 38 steroid-naive adults with mild asthma to inhaled fluticasone or placebo for three weeks; 21 were nonsmokers. The reported change in mean morning peak expiratory flow with fluticasone versus placebo was +27 L/min in nonsmokers and -5 L/min in smokers.",
      "scenario":"You are reviewing treatment-response data from a clinical research team. Two participants have mild asthma, but one currently smokes. The team wants to interpret the evidence without treating individual response as predetermined.",
      "steps":[
        {"q":"What is the strongest inference from the published group-level results?", "choices":["Smoking causes complete corticosteroid resistance in every patient.","In this trial, short-term response to inhaled fluticasone was attenuated among smokers.","The smoker cohort had better mean morning peak-flow improvement."],"correct":1,"why":"The effect was lower among smokers in this study. A difference between group averages does not prove that every smoker fails treatment.","concept":"Group-level evidence and heterogeneous drug response"},
        {"q":"What is the most appropriate next research question?", "choices":["Whether smoking modifies steroid-response pathways and whether treatment strategies differ in controlled trials.","Whether all corticosteroids should be abandoned regardless of clinical context.","Whether a lower response necessarily means the drug never reaches airway tissue."],"correct":0,"why":"A mechanistic and comparative-treatment study could test why response differs; the trial alone does not justify a universal treatment rule.","concept":"Mechanism and study design"},
        {"q":"Lazarus et al. (2007) studied beclomethasone and montelukast. Which evidence statement is most careful?", "choices":["Both drugs were proven equally effective for every smoker.","Montelukast cured corticosteroid resistance permanently.","Treatment response varied by smoking status and outcome; these findings are not an individualized prescribing algorithm."],"correct":2,"why":"That trial measured multiple clinical outcomes and treatment responses. Evidence should be interpreted by endpoint and population, not oversimplified into guaranteed clinical effects.","concept":"External validity and clinical limitations"}
      ],
      "sources":[("Chalmers GW et al., Thorax (2002), DOI: 10.1136/thorax.57.3.226","https://doi.org/10.1136/thorax.57.3.226"),("Lazarus SC et al., AJRCCM (2007), DOI: 10.1164/rccm.200511-1746OC","https://doi.org/10.1164/rccm.200511-1746OC")],
      "limitation":"Chalmers: small, short-term trial in mild asthma; group averages cannot predict any specific patient's response. The two source trials are not interchangeable."
    },
    {
      "name":"02 · Grapefruit–Felodipine Interaction", "tag":"Pharmacokinetics · First-pass metabolism",
      "research":"Lown et al. (1997) investigated repeated grapefruit-juice consumption in 10 healthy men. Small-intestinal enterocyte CYP3A4 protein fell by 62% (P = 0.0006), without an observed corresponding change in hepatic CYP3A4 activity on their test.",
      "scenario":"A clinical pharmacology team observes increased oral felodipine exposure following grapefruit-juice consumption. The administered dose remains constant. Investigators want to distinguish intestinal first-pass effects from changes in clearance elsewhere.",
      "steps":[
        {"q":"Which mechanism best accounts for the study findings?", "choices":["Reduced intestinal CYP3A4 protein and presystemic metabolism.","Increased renal elimination of felodipine.","Induction of hepatic CYP3A4 leading to lower oral bioavailability."],"correct":0,"why":"Reduced intestinal CYP3A4 can allow more orally administered felodipine to escape first-pass metabolism. Lown et al. observed reduced enterocyte CYP3A4 protein.","concept":"Intestinal first-pass metabolism"},
        {"q":"In a simplified model where oral bioavailability increases while dose and systemic clearance are unchanged, what happens to AUC?", "choices":["It must decrease.","It increases in proportion to bioavailability (AUC = F × Dose / CL).","It remains unchanged because dose was constant."],"correct":1,"why":"For linear pharmacokinetics, AUC = F × Dose / CL. Changing F can change oral exposure even if dose is unchanged. This is a model implication, not a measured fold-change from the study.","concept":"AUC, bioavailability, and clearance"},
        {"q":"Which claim goes beyond the specific study evidence?", "choices":["Enterocyte CYP3A4 protein was lower after the juice regimen.","Hepatic CYP3A4 activity was not altered in the study's measured test.","Every drug will interact with grapefruit to the same extent."],"correct":2,"why":"Interaction size varies across drugs, their metabolism and transport characteristics, and other factors. The study does not support a universal claim.","concept":"Evidence boundaries"}
      ],
      "sources":[("Lown KS et al., J Clin Invest (1997), DOI: 10.1172/JCI119439","https://doi.org/10.1172/JCI119439")],
      "limitation":"Only 10 healthy male volunteers; mechanistic and kinetic findings for felodipine must not be generalized to all drugs or populations."
    },
    {
      "name":"03 · P-gp and CNS Drug Exposure", "tag":"Drug transport · Toxicology",
      "research":"Sadeque et al. (2000) examined loperamide with quinidine in eight healthy male volunteers and found respiratory depression in the combination condition, unlike loperamide alone. Kim et al. (2014) reported that another P-gp inhibitor, HM30181, increased systemic loperamide exposure without the same measured CNS effects, highlighting tissue-specific interpretation.",
      "scenario":"A research team compares loperamide given alone and alongside compounds that inhibit the efflux transporter P-glycoprotein (P-gp). They want to distinguish changes in plasma exposure from effects at the blood-brain barrier.",
      "steps":[
        {"q":"Why does loperamide usually have limited central opioid effects at recommended doses?", "choices":["It has no affinity for opioid receptors.","P-gp-mediated efflux limits its CNS penetration.","It never reaches the bloodstream after oral administration."],"correct":1,"why":"P-glycoprotein at the blood-brain barrier can transport certain substrates out of the CNS, limiting brain exposure even when systemic drug is present.","concept":"Transporter-mediated distribution"},
        {"q":"Which interpretation best matches Sadeque et al.'s trial?", "choices":["The quinidine combination was associated with respiratory depression, supporting a possible transporter-mediated interaction.","Respiratory depression occurred equally with and without quinidine.","Changes in plasma drug concentration alone fully explained every result."],"correct":0,"why":"Their small trial reported a respiratory effect with coadministration that they argued was not explained solely by measured plasma concentrations.","concept":"Separating pharmacokinetics and pharmacodynamics"},
        {"q":"Kim et al. (2014) reported increased systemic exposure with HM30181 but no measured CNS changes. What is the best conclusion?", "choices":["Any increase in plasma AUC guarantees CNS toxicity.","P-gp is irrelevant to the brain.","Systemic exposure and CNS effect cannot be assumed to change together; inhibitor and tissue context matter."],"correct":2,"why":"Exposure changes can be tissue-dependent; the trials involved different inhibitors and endpoints. Compare the actual study designs rather than assuming one mechanism explains every outcome.","concept":"Comparison of primary studies"}
      ],
      "sources":[("Sadeque AJ et al., Clin Pharmacol Ther (2000), DOI: 10.1067/mcp.2000.109156","https://doi.org/10.1067/mcp.2000.109156"),("Kim TE et al., Br J Clin Pharmacol (2014), DOI: 10.1111/bcp.12368","https://doi.org/10.1111/bcp.12368")],
      "limitation":"Small volunteer studies with different interventions and endpoints. This module is not advice to combine loperamide with transporter inhibitors; doing so may be dangerous."
    }
]

st.markdown('<div class="hero"><h1>💊 PharmaChoice</h1><p>Research-Based Interactive Pharmacology Decision Simulator · Honors Project</p></div>', unsafe_allow_html=True)
st.caption("Educational research simulator • Not for diagnosis or treatment decisions • Scientific sources are linked below")

if "answers" not in st.session_state:
    st.session_state.answers = {}
if "stage" not in st.session_state:
    st.session_state.stage = {}

with st.sidebar:
    st.header("Research Lab")
    st.write("Three evidence-based modules, each with three decisions and detailed mechanistic feedback.")
    st.divider()
    for i, c in enumerate(CASES):
        n = sum(k[0] == i for k in st.session_state.answers)
        st.write(f"**{i+1}.** {n}/3 decisions completed")
    st.divider()
    if st.button("Reset all decisions", use_container_width=True):
        st.session_state.answers = {}
        st.session_state.stage = {}
        st.rerun()

selected_index = st.selectbox("Select a research module", range(len(CASES)), format_func=lambda i: CASES[i]["name"])
c = CASES[selected_index]
st.caption(c["tag"])
left, right = st.columns([1.5, 1])
with left:
    st.subheader("Research brief")
    st.info(c["scenario"])
    with st.expander("View original-study evidence", expanded=True):
        st.write(c["research"])
with right:
    st.subheader("Mechanism explorer")
    if selected_index == 0:
        st.write("**Published mean morning PEF change (L/min)**")
        df = pd.DataFrame({"Group":["Nonsmokers","Smokers"],"Change (L/min)":[27,-5]}).set_index("Group")
        st.bar_chart(df)
        st.caption("Reported Chalmers et al. group-level values; not individual outcomes.")
    elif selected_index == 1:
        st.write("**Illustrative normalized plasma profiles**")
        times = [i * .25 for i in range(49)]
        def curve(t, bio):
            return bio * 2 * (math.exp(-0.22*t) - math.exp(-1.45*t))
        df = pd.DataFrame({"Hours":times,"Baseline model":[curve(t, .5) for t in times],"Higher-F model":[curve(t, .9) for t in times]}).set_index("Hours")
        st.line_chart(df)
        st.caption("SIMULATED—not empirical felodipine curves. Only F differs in this conceptual example.")
    else:
        st.write("**Conceptual CNS exposure**")
        transport = st.slider("Illustrative P-gp efflux strength", 0, 100, 70, 5)
        st.metric("Relative CNS accessibility index", f"{100-transport}/100")
        st.progress((100-transport)/100)
        st.caption("SIMULATED conceptual index, not a validated clinical prediction or a patient-specific estimate.")

st.divider()
step = st.session_state.stage.get(selected_index, 0)
step = min(step, 2)
questions = c["steps"]
st.subheader(f"Decision {step+1} of 3")
st.progress((step+1)/3)
q = questions[step]
st.write(f"**{q['q']}**")
key = (selected_index, step)
chosen = st.radio("Choose the most defensible interpretation:", q["choices"], index=None, key=f"radio_{selected_index}_{step}")
existing = st.session_state.answers.get(key)
if st.button("Evaluate decision", type="primary", disabled=chosen is None):
    st.session_state.answers[key] = q["choices"].index(chosen)
    st.rerun()
if existing is not None:
    is_correct = existing == q["correct"]
    if is_correct:
        st.success("Evidence-aligned decision")
    else:
        st.warning("Revisit the evidence")
    st.markdown(f"**Mechanism / scientific feedback:** {q['why']}")
    st.caption(f"Concept: {q['concept']}")
    if step < 2:
        if st.button("Continue to next decision →"):
            st.session_state.stage[selected_index] = step + 1
            st.rerun()
    else:
        score = sum(st.session_state.answers.get((selected_index, j)) == questions[j]["correct"] for j in range(3))
        st.metric("Module score", f"{score} / 3")
        if st.button("Review module from decision 1"):
            st.session_state.stage[selected_index] = 0
            st.rerun()

st.divider()
with st.expander("Primary literature, citations & limitations", expanded=True):
    for name, url in c["sources"]:
        st.markdown(f"- [{name}]({url})")
    st.markdown(f"**Interpretation limitations:** {c['limitation']}")

st.subheader("Research performance")
completed = len(st.session_state.answers)
correct = sum(st.session_state.answers[(i,j)] == CASES[i]["steps"][j]["correct"] for i,j in st.session_state.answers)
col1, col2, col3 = st.columns(3)
col1.metric("Decisions completed", f"{completed} / 9")
col2.metric("Evidence-aligned", correct)
col3.metric("Accuracy", f"{round(correct/completed*100)}%" if completed else "—")
if completed == 9:
    report = ["PharmaChoice – Research Decision Summary", f"Decisions: {completed}/9", f"Correct: {correct}/9", ""]
    for i,cse in enumerate(CASES):
        score = sum(st.session_state.answers.get((i,j)) == cse["steps"][j]["correct"] for j in range(3))
        report.append(f"{cse['name']}: {score}/3")
    report.extend(["", "Educational only. Not a clinical assessment."])
    st.download_button("Download performance summary", "\n".join(report), file_name="PharmaChoice_Performance.txt", mime="text/plain")

st.caption("Scientific reasoning, mechanisms, and limitations are emphasized over memorization. This is an educational prototype; no real patient data are used.")
