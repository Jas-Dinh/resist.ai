![Product Logo](images/resistai-logo.svg)  

# antibiotic stewardship

When patients present with symptoms of a bacterial infection, doctors face a critical dilemma. Traditional culture-based antibiotic susceptibility testing (AST) takes 24-48 hours to determine effective antibiotics. This delay forces clinicians to either prescribe broad-spectrum antibiotics—contributing to antimicrobial resistance (AMR)—or risk using narrow, potentially ineffective antibiotics, endangering patients.

The consequences are severe: the CDC estimates over 35,000 Americans die annually due to AMR, with costs reaching $55 billion. Globally, according to the WHO, bacterial AMR directly caused approximately 1.3 million deaths and contributed to 5 million deaths in 2019.

Broad-spectrum antibiotics create wider disruption of beneficial microbiota, allowing resistant bacteria to thrive without competition, and increase selective pressure for resistant genes. This highlights the importance of antibiotic stewardship—the coordinated interventions designed to promote appropriate antibiotic use while improving patient outcomes and reducing microbial resistance. Effective antibiotic stewardship programs rely on timely, accurate information about bacterial pathogens and their susceptibility patterns. However, the current 24-48 hour delay in culture-based testing creates a significant barrier to implementing best practices. Clinicians often resort to empirical broad-spectrum therapy as a safety measure, undermining stewardship efforts.

resist.ai promotes antibiotic stewardship by using AI to accelerate bacterial identification and antibiotic susceptibility testing, potentially saving up to 48 hours in treatment decisions. By providing rapid, personalized antibiotic recommendations, our system supports antibiotic stewardship goals of using the right antibiotic, at the right dose, for the right duration, and at the right time—ultimately reducing inappropriate antibiotic use while improving patient care.

---

# behind the product

resist.ai combines phase contrast microscopy image data with Electronic Health Record (EHR) data to deliver a comprehensive set of personalized antibiotic recommendations. 

**1. Identify bacteria**
  - Requires minimal equipment: just a phase contrast microscope and a single photograph captured by a lab technician
  - Developed custom convolutional neural network for bacterial identification, trained model on **add data** for three different bacterial species: Escherichia Coli, Klebsiella Pneumoniae, and Psuedomonas Aeruginosa
  - Simpler deep learning architectures outperformed complex, large models

![CNN Architecture](images/CNN_architecture.png)

**2. Predict antibiotic susceptibilities**
  - Transformed complex EHR data from the [MIMIC IV Database](https://mimic.mit.edu/) into meaningful features while preventing data leakage
    - Key techniques included higher-level racial groupings, mean imputation by gender & age, CCSR category mapping, ATC category mapping, and bag-of-words counts
    - Tracked total medical procedures and days since last medical procedure
  - Evaluated logistic regression, Random Forest, XGBoost, and Histogram-Based XGBoost
  - Histogram-Based XGBoost selected as it effectively handles missing values common in EHR data
  - Built individual models for each bacteria-antibiotic pair
  - Prioritized precision over recall as prescribing a resistant antibiotic (false positive) is more dangerous than missing a susceptible one (false negative)

**3. Explain**
- Used SHAP values to transform ML-based antibiogram from a "black box" into an interpretable clinical tool
- Identified key patient-specific features (lab values, medication history, clinical timeline) that influence antibiotic resistance probabilities
- Explainable predictions enable clinicians to understand not just what the model predicts, but why

![SHAP Values](images/SHAP_example.png)

**4. Evaluate**
- **Technical performance**
  - Microscopy model: 97% overall accuracy, with precision ranging from 0.89 to 1.00 and recall from 0.96 to 0.98
  - EHR-based antibiotic susceptibility models: precision between 0.55 and 0.96, comparable to research results (0.46-0.99)
    
- **Fairness assessment**
  - Tested E. coli + Ampicillin across racial groups
  - No statistically significant difference in overall accuracies (chi-squared: 12.6, p-value: 0.39)
  - Identified disparities in specific error types (i.e., false-positive rates)
  - Reduced disparities significantly through stratification on combined racial category and target, eliminating statistical significance in differences for 3 groups and lowering false positive rates for Hispanic groups from 45% to 24%
  
- **Decision comparison** 
  - *Resistance assessment*
    - 19% of antibiotics prescribed by physicians were resistant
    -  Models would have correctly identified 59% of these antibiotics as resistant
  - *Lower tier usage*
    - 56% of patients received a lower tier where a higher tier was available 
    - Models would have identified a first-tier, susceptible antibiotic for 99% of these patients 
  - *Broad spectrum usage*
    - 85% of patients received a broad spectrum where a lower spectrum was available 
    - Models would have identified a lower spectrum, susceptible antibiotic for 99% of these patients 

---

# meet the team 

add people & roles 

---

# testimonials

> "This product is awesome"
> — Jane Doe

