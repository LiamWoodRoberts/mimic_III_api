from app import app,api,ent_df
from app.get_tags import get_entity_tags,get_drugs_and_conditions,clean_text
from app.ner_tagger import medical_suite,load_crf

from flask import render_template,request,jsonify,url_for,redirect

crf_path = "crf_model"
crf = load_crf(crf_path)

text = ['''HISTORY OF PRESENT ILLNESS:  This is an 81-year-old female
with a history of emphysema (not on home O2), who presents
with three days of shortness of breath thought by her primary
care doctor to be a COPD flare.  Two days prior to admission,
she was started on a prednisone taper and one day prior to
admission she required oxygen at home in order to maintain
oxygen saturation greater than 90%.  She has also been on
levofloxacin and nebulizers, and was not getting better, and
presented to the [**Hospital1 18**] Emergency Room.''',
            '''HISTORY OF PRESENT ILLNESS:
44 yo female with a h/o left frontal AVM in the supplementary
motor area. The AVM was treated with stereotactic radiosurgery
(Gamma Knife)in [**2114**]. In [**2116**], the patient developed a seizure
disorder. [**2118-5-27**] she developed
headaches and after an MRI and a digital angiogram showed no
residual pathological vessels, a contrast enhancing lesion
with massive focal residual edema was diagnosed- very
likely represents radionecrosis. The patient had midline
shift and mass effect. On [**2118-8-10**] she had a left craniotomy for
resection of the radionecrosis. She then presented to the office
in [**2118-8-27**] with increased left facial swelling and incision
drainage, she was taken to the OR for a wound washout and
craniectomy. She now returns for a cranioplasty after a long
course of outpatient IV antibiotic therapy.''',
            '''HISTORY OF PRESENT ILLNESS:
This 81 year old woman has a history of COPD. Over the past five
years she has had progressive difficulties with her breathing.
In [**2118-6-4**] she was admitted to [**Hospital1 18**] for respiratory failure
due to a COPD exacerbation. Due to persistent hypoxemia, she
required intubation and a eventual bronchoscopy on [**2118-6-9**] revealed marked
narrowing of the airways on expiration consistent with
tracheomalacia. She subsequently underwent placement of two
silicone stents, one in the left main stem and one in the
trachea. During the admission the patient had complaints of
chest pain and ruled out for an MI. She was subsequently discharged to
[**Hospital1 **] for physical and pulmonary rehab. Repeat bronchoscopy
on [**2118-8-1**] revealed granulation tissue at the distal right lateral
wall of the tracheal stent. There was significant malacia of the
peripheral and central airways with complete collapse of the
airways on coughing and forced expiration. Small nodules were
also noted on the vocal cords. She has noticed improvement in
her respiratory status, but most recently has been in discussion
with Dr. [**First Name4 (NamePattern1) 951**] [**Last Name (NamePattern1) 952**] 
regarding possible tracheobronchial plasty with mesh. Tracheal stents d/c [**2119-4-19**] 
in anticipation of surgery. In terms of symptoms, she describes many years of intermittent
chest pain that she describes as left sided and occurring at any
time. Currently, she notices it about three times a week, and
states that it seems to resolve after three nitroglycerin.
She currently is dependent on oxygen and wears 1.5-2 liters
around the clock. She has frequent coughing and brings up "dark
sputum"''',
'''HISTORY OF PRESENT ILLNESS:
[**Known firstname 622**] [**Known lastname 1836**] is a 62-year-old woman, with longstanding
history of rheumatoid arthritis, probable Sweet's syndrome, and
multiple joint complications requiring orthopedic interventions.
She was found to hve a right cavernous sinus and nasopharyngeal
mass.  She underwent a biopsy of hte nasopharyngeal mass by Dr.
[**First Name4 (NamePattern1) **] [**Last Name (NamePattern1) 1837**] and the pathology, including flow
cytometry,
was reactive for T-cell lymphoid hyperplasia only.

She has a longstanding history of rheumatoid arthritis that
involved small and large joints in her body.  Her disease is
currently controlled by abatacept, hydroxychloroquine, and
methotrexate.  She also has a remote history of erythematous
nodules at her shins, dermatosis (probable Sweet's disease),
severe holocranial headache with an intensity of [**9-28**], and
dysphagia.  But her symptoms resolved with treatment for
autoimmune disease.  Please refer additional past medical
history, past surgical history, facial history, and social
history to the initial note on [**2171-11-4**].

She cam to the BTC for discussion about management of her right
cavernous sinus mass that extends into the middle cranial fossa.


She had a recent head CT at the [**Hospital1 756**] and Woman's Hospital on
[**2171-11-29**], when she went for a consultation there.
She is neurologically stable without headache, nausea, vomiting,
seizure, imbalance, or fall. She has no new systemic complaints.

Her neurological problem started [**9-/2171**] when she experienced
frontal pressure-like sensations.  There was no temporal
pattern;
but they may occur more often in the evening.
She had fullness in her ear and she also had a cold coinciding
to
the onset of her headache.  By late [**Month (only) 359**] and early [**2171-10-21**], she also developed a sharp pain intermittently in the
right
temple region.
She did not have nausea, vomiting, blurry vision, imbalance, or
fall.  A gadolinium-enhanced head MRI, performed at [**Hospital1 346**] on [**2171-10-30**], showed a bright mass
involving the cavernous sinus.''',
'''HISTORY OF PRESENT ILLNESS:
82 yo F with CAD, CHF, HTN, recent PE ([**10-17**]), who presents from
rehab with hypoxia and SOB despite Abx treatment for PNA x 3
days. The patient was in rehab after being discharged from here
for PE. She was scheduled to be discharged on [**12-6**]; on the day
prior to discharge she deveoped fever, hypoxia, and SOB. CXR
showed b/t lower lobe infiltrates. She was started on levoflox
and ceftriaxone on [**12-5**]. When she became hypoxic on NC they
brought her in to the ED.
.
In the [**Hospital1 18**] ED she was febrile to 102.7, P 109 BP 135/56 R 34
O2 90% on 3L. She was started on vanc and zosyn for broader
coverage, tylenol, and 2L NS.
.
The patient reports having sweats and cough before admission.
She complains of SOB and some upper back pain. She denies chest
pain, URI sx, nausea/vomiting, diarrhea, or dysuria. Of note she
had had a rash and was given prednisone for 7 days, ending
[**12-3**]. The rash was speculated to be due to coumadin, but she
was able to be continued on coumadin.''',
'''HISTORY OF PRESENT ILLNESS:
Mr. [**Known lastname 1858**] is an 84 yo man with moderate aortic stenosis (outside
hospital echo in [**2124**] with [**Location (un) 109**] 1 cm2, gradient 28 mmHg, moderate
mitral regurgitation, mild aortic insufficiency), chronic left
ventricular systolic heart failure with EF 25-30%, hypertension,
hyperlipidemia, diabetes mellitus, CAD s/p CABG in [**2099**] with
SVG-LAD-Diagonal, SVG-OM, and SVG-RPDA-RPL, with a re-do CABG in
[**9-/2117**] with LIMA-LAD, SVG-OM, SVG-diagonal, and SVG-RCA. He also
has severe peripheral arterial disease s/p peripheral bypass
surgery. He presented to [**Hospital 1474**] Hospital ER this morning with
shortness of breath and chest pain and was found to be in heart
failure.

He states he was in his usual state of health until 10:30 last
evening when he woke up feeling cold; 1 hour later he developed
moderate to severe sharp chest pain radiating across his chest
associated with nausea, diaphoresis, and dypsnea. The pain was
fairly constant and did not resolve until he was given sL NTG at
6 am by EMS. He has been pain free since. Presenting vitals BP
109/66, HR 71, O2 sat 88% on RA. CXR showed congestive heart
failure; initial troponin-I was mildly elevated at 0.4, CK 70.
He given aspirin and furosemide 80 mg IV (with ~600cc diuresis),
Nitropaste [**1-3**]", and Lovenox 80 mg SQ. During the ambulance
transfer to the [**Hospital1 18**], he also received ~500 cc IVF for ? low
BP).

On further questioning, Mr. [**Known lastname 1858**] has very poor exercise
tolerance due to knee pain that he attributes to osteoarthritis.
But he says that he gets chest pain (similar to pain he had last
night) with fairly minimal exertion (picking up his 11 lb cat,
carrying 1 gallon jug of water, first getting up from sitting to
walk outside or to walk to the bedroom). The pain is associated
with dyspnea and is relieved with few minutes rest. His symptoms
occur about every day to every other day and have been stable
over the past year. He denies orthopnea, paroxysmal nocturnal
dyspnea, but does endorse exertional dyspnea (he cannot identify
the amount of exertion required). Currently, he is dyspneic and
feels somewhat better sitting up; he reports no chest pain.

ROS is also positive for a nose bleed requiring ED visit several
months ago (and cessation of Plavix for a few days), and
currently gross hematuria after Foley placement and Lovenox.'''
    ]

@app.route("/contact")
def test():
    return render_template("/contact.html")

@app.route("/annotation")
def contribute():
    return render_template("/annotation.html")

@app.route("/services")
def services():
    return render_template("/services.html")

@app.route("/demo",methods=["GET","POST"])
def demo():
    idx = 0
    if request.method == "POST":
        idx = int(request.form["index"])
    return render_template("/demo.html",sample=text[idx],index=idx)

@app.route("/medical_suite",methods=["POST"])
def suite():
    if request.method == "POST":
        index = int(request.form["index"])
        sample = text[index]
        age,gender,symptoms,conditions,procedures,drugs = medical_suite(sample,crf)
        return render_template("/medical_suite.html",sample=sample,age=age,gender=gender,symptoms=symptoms,conditions=conditions,procedures=procedures,drugs=drugs)

@app.route("/",methods=["GET","POST"])
@app.route("/home",methods=["GET","POST"])
def home():
    d_and_c = {"DRUGS":['None'],"CONDITIONS":["None"]}
    if request.method == "POST":
        text = request.form["text"]
        text = clean_text(text)
        ent_locs = get_entity_tags(text,ent_df)
        d_and_c = get_drugs_and_conditions(ent_locs)
        return render_template("/home.html",ents = d_and_c)
    else:
        return render_template("/home.html",ents=d_and_c)
