import cv2
import pandas as pd
import numpy as np
import joblib
from skimage.feature import hog
# from skimage import exposure
from sklearn.preprocessing import StandardScaler
# from tensorflow.keras.models import load_model
import shap


import streamlit as st

# @st.cache_resource
# def load_h5_model(model_path):
#     # model takes too long to load so i cache it and load when app opens
#     pass
#     # return load_model(model_path)

def html_customizations():
    css = """
        <style>
        :root {
        --primary-blue: #4a6fa5;
        --light-blue: #7abff1;
        --light-green: #7fe5a7;
        --dark-text: #2c3e50;
        --light-text: #ecf0f1;
        --background: #f5f9fc;
        }

        body {
        background: var(--background);
        color: var(--dark-text);
        }

        .metric-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px;
        border-radius: 10px;
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        width: 200px;
        text-align: center;
        }

        .metric-label {
        font-size: 16px;
        font-weight: bold;
        color: #555;
        }

        .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #333;
        }

        button {
        background: linear-gradient(to right, var(--light-blue), var(--light-green));
        color: var(--dark-text);
        border: 1px solid var(--primary-blue);
        }

        button:hover {
        background: linear-gradient(to right, var(--light-green), var(--light-blue));
        }

        table {
        border-color: var(--primary-blue);
        }

        th {
        background: var(--primary-blue);
        color: var(--light-text);
        }

        tr:nth-child(even) {
        background: rgba(122, 191, 241, 0.1);
        }
        </style>
        """
    st.markdown(
    """
        <style>
        /* Main app background */
        [data-testid="stAppViewContainer"] {
            background-color: #f5f9fc;
            color: #2c3e50;
        }

        /* Optional: Sidebar background */
        [data-testid="stSidebar"] {
            background-color: #e8efff;
            color: #2c3e50;
        }
        </style>
    """,
        unsafe_allow_html=True
    )
    st.markdown("""
    <style>
    div.stButton > button {
        background: linear-gradient(to right, #7abff1, #7fe5a7);
        color: #2c3e50;
        font-size: 16px;
        border: 2px solid #4a6fa5;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }

    div.stButton > button:hover {
        background: linear-gradient(to right, #7fe5a7, #7abff1);
        color: #ffffff;
        border-color: #2ecc71;
    }
    </style>
    """, unsafe_allow_html=True)

def load_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (128, 128))
    return image

def extract_features(image, minutes):
    hog_features, _ = hog(image, pixels_per_cell=(8, 8), cells_per_block=(2, 2), visualize=True)
    
    edges = cv2.Canny(image, 100, 200)
    edge_features = edges.flatten()
    
    ret, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    contour_features = []
    for contour in contours[:5]:
        moments = cv2.moments(contour)
        hu_moments = cv2.HuMoments(moments).flatten()
        contour_features.extend(hu_moments)
    
    while len(contour_features) < 35:  # Padding for consistency
        contour_features.append(0.0)
        
    features = np.hstack([hog_features, edge_features, contour_features])#, minutes])
    return features

def predict_bacteria(image_path, timepoint, model =None):

    # this is for training lite model
    model_path = "svm_model.pkl"
    scaler_path = "scaler.pkl"         
    
    species_map = {0: 'E. faecalis', 1: 'K. pneumoniae', 2:'E. coli', 3:'P. aeruginosa'}
    image = load_image(image_path)
    features = extract_features(image, timepoint)
    print(features.shape)

    #comment out
    scaler = joblib.load(scaler_path)
    features_scaled = scaler.transform([features])
    model = joblib.load(model_path)
    prediction = model.predict(features_scaled)[0]
    print(model.decision_function(features_scaled))
    scores = model.decision_function(features_scaled)[0]

    # comment out
    # prediction = model.predict(features)
    # print(model.decision_function(features))
    # scores = model.decision_function(features)[0]

    exp_scores = np.exp(scores - np.max(scores))
    probabilities = exp_scores / np.sum(exp_scores)
    confidence = np.max(probabilities)
    print(f"Model Prediction Output: {prediction}")
    print(f"Model Confidence: {confidence}")
    bacteria = species_map[int(prediction)]
    return bacteria, confidence

def mapping(shap_dict):
    df1 = pd.read_csv(R"icd_code_map.csv").rename(columns={"ccsr_category": "code", "ccsr_category_description": "map"})[["code", "map"]]
    df2 = pd.read_csv(R"ndc_act_mapping.csv").rename(columns={"atc_class": "code", "atc_class_name": "map"})[["code", "map"]]
    df_combined = pd.concat([df1, df2], ignore_index=True)

    copy = shap_dict.copy()
    for i in copy.keys():
        if i in df_combined["code"].values:
            val = shap_dict[i]
            shap_dict[df_combined[df_combined["code"] == i]["map"].values[0]] = val
            del shap_dict[i]
    
    return shap_dict

def find_shap(model, X_subject):

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_subject)

    # shap_values shape: (1, num_features, 2) -> [sample, feature, class]
    if isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
        shap_row = shap_values[0, :, 1]  # first sample, class 1
    else:
        raise ValueError(f"Unexpected SHAP output shape: {shap_values.shape}")

    feature_names = X_subject.columns.tolist()

    if len(feature_names) != len(shap_row):
        raise ValueError(f"Feature count ({len(feature_names)}) and SHAP value count ({len(shap_row)}) do not match.")

    # Sort by importance (absolute value of SHAP)
    sorted_shap = sorted(zip(feature_names, shap_row), key=lambda x: abs(x[1]), reverse=True)[:5]
    sorted_shap = dict(sorted_shap)
    return mapping(sorted_shap)

def predict_antibiotic(bacteria, patient_data):
    #using only e coli antibiotics for now

    model_path = "rf_models_25_03_16.pkl"
    models_dict = joblib.load(model_path)

    predictions = {}
    confidences = {}
    f_importances = {}

    for name, model in models_dict.items():
        pred = model.predict(patient_data)[0]
        confidence = max(model.predict_proba(patient_data)[0])
        predictions[name] = "Susceptible" if pred == 1 else "Resistant"
        confidences[name] = confidence
        f_importances[name] = find_shap(model, patient_data)

    return predictions, confidences, f_importances

def validate_patient_id(patient_id, patient_df):
    if patient_id:
        if patient_id.isdigit():
            patient_id = int(patient_id)
            
            if patient_id in patient_df['subject_id'].values:
                pass #maybe output more data such as patient too risky for model use
            else:
                st.warning(f"Patient ID {patient_id} not found.")
        else:
            st.error("Please enter a valid numeric ID.")
    return patient_id

def load_logo():
    st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://raw.githubusercontent.com/Jas-Dinh/resist.ai/68928f55d3af92c68669736b46724ebe8c9f8599/images/resistai-logo.svg" width="300"/>
    </div>
    """,
    unsafe_allow_html=True
)


def main():
    st.set_page_config(page_title="Bacteria Classification", layout="centered")
    html_customizations()
    load_logo()
    # model = load_h5_model("cnn_model.h5")
    st.title("Upload an Image and Patient ID")
    
    uploaded_image = st.file_uploader("Upload Bacterial Image", type=["jpg", "png", "jpeg"])

    patient_df = pd.read_csv(R"patient_sample.csv")
    selected_patient = st.text_input("Enter Patient ID (numeric)", value="10002557", placeholder="Ex. 10002557")
    selected_patient= validate_patient_id(selected_patient, patient_df)
        
    timepoint = st.number_input("Enter Timepoint (Minutes)", min_value=0, max_value=30, value=15)
    
    if st.button("Classify Bacteria"):
        if uploaded_image is not None and selected_patient is not None:
            with st.spinner("Processing Image and Data..."):
                image_path = "temp_image.jpg"
                with open(image_path, "wb") as f:
                    f.write(uploaded_image.getbuffer())
                
                bacteria, confidence = predict_bacteria(image_path, timepoint, model = None)
                
                patient_data = patient_df[patient_df['subject_id'] == selected_patient].drop(columns=['subject_id', 'charttime'])
                antibiotic, a_confidences, f_importances = predict_antibiotic(bacteria, patient_data)

                st.success(f"Predicted Bacteria: {bacteria}, Confidence: {confidence:.2%}")
                st.session_state['bacteria_classified'] = bacteria
                st.session_state['bacteria_confidence'] = confidence
                st.session_state['antibiotic_susceptibility'] = antibiotic
                st.session_state['antibiotic_confidence'] = a_confidences
                st.session_state['f_importance'] = f_importances
                
                st.switch_page("pages/output.py")

if __name__ == "__main__":
    main()
