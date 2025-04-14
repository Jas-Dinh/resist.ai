import streamlit as st
import random
import pandas as pd
import re
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def generate_mock_antibiotic_data(predictions, confidences, f_importances):
    """table:user tier, antibiotic, susceptibility, confidence, stock, and usage. Might add spectrum and notes later"""
    
    # Create a table with antibiotic info
    data = []
    usage_levels = ['Low', 'Medium', 'High']
    tiers = ['First Line', 'Second Line', 'Last Resort', 'Other']
    use_tiers = {'rf_ESCHERICHIA COLI_AMPICILLIN': 'Other', 'rf_ESCHERICHIA COLI_AMPICILLIN/SULBACTAM': 'Second Line', 
     'rf_ESCHERICHIA COLI_CEFAZOLIN': 'Second Line', 'rf_ESCHERICHIA COLI_CEFEPIME': 'Second Line', 'rf_ESCHERICHIA COLI_CEFTAZIDIME': 'Second Line', 
     'rf_ESCHERICHIA COLI_CEFTRIAXONE': 'First Line', 'rf_ESCHERICHIA COLI_CIPROFLOXACIN': 'Second Line', 'rf_ESCHERICHIA COLI_GENTAMICIN': 'Other', 
     'rf_ESCHERICHIA COLI_MEROPENEM': 'Last Resort', 'rf_ESCHERICHIA COLI_NITROFURANTOIN': 'First Line', 'rf_ESCHERICHIA COLI_PIPERACILLIN/TAZO': 'Second Line', 
     'rf_ESCHERICHIA COLI_TOBRAMYCIN': 'Other', 'rf_ESCHERICHIA COLI_TRIMETHOPRIM/SULFA': 'First Line'}


    for antibiotic, pred in predictions.items():
        confidence = confidences[antibiotic]
        use_tier = use_tiers[antibiotic]
        top_features = f_importances[antibiotic]

        
        stock = random.randint(10, 100)
        usage = random.choice(usage_levels)
        
        data.append({
            "Use Tier": use_tier,
            "Antibiotic": antibiotic.replace('rf_ESCHERICHIA COLI_', ''),  # Clean name formatting
            "Predicted Susceptibility": pred,
            "Confidence": f"{confidence:.2f}",
            "Stock": stock,
            "Usage": usage,
            'Top Features': top_features
        })
    
    df = pd.DataFrame(data)
    df["Recommended"] = df.apply(
        lambda row: "⭐️" if row["Use Tier"] == "First Line" and row["Predicted Susceptibility"] == "Susceptible" else "",
        axis=1
    )
    df['Use Tier'] = pd.Categorical(df['Use Tier'], categories=tiers, ordered=True)
    df.sort_values(by=['Recommended', 'Use Tier', 'Predicted Susceptibility'], ascending=[False, True, False], inplace=True)
    
    return df


def randomize_stock(stock_value):
        match = re.match(r'(\d+)(.*)', str(stock_value).strip()) # takes string after digit
        num, unit = match.groups()
        random_stock = random.randint(10, 400)  # Random stock value

        return f"{random_stock}{unit}"

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
    # Apply the CSS
    st.markdown(css, unsafe_allow_html=True)
    # header
    st.markdown("""
        <style>
            .header {
                font-size: 24px;
                font-weight: bold;
                background-color: #4a6fa5;
                padding: 15px;
                border-radius: 10px;
                color: #ecf0f1;
            }
            .section {
                border-radius: 10px;
                padding: 15px;
                margin-top: 10px;
            }
            .green {
                background-color: #7fe5a7;
                color: #2c3e50;
            }
            .orange {
                background-color: #fff4e5;
            }
            .blue {
                background-color: #7abff1;
                color: #2c3e50;
            }
            .grey {
                background-color: #D6D8DB;
            }
            
        </style>
    """, unsafe_allow_html=True)


def make_page(data):
    # Page title and branding
    st.set_page_config(page_title="Personalized Antibiogram", layout="centered")
    html_customizations()

    # make output table
    antibiotics_table = generate_mock_antibiotic_data(data['antibiotic_susceptibility'], data['antibiotic_confidence'], data['f_importances'])
    stocks = pd.read_csv(".\mock_stock.csv")
    stocks['Remaining Stock'] = stocks['Remaining Stock'].apply(randomize_stock)

    final_table = pd.merge(antibiotics_table, stocks, on='Antibiotic')

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select Page", ["Overview"] + list(final_table["Antibiotic"].unique()))

    if page == "Overview":
        overview_page(data, final_table)
    else:
        switch_page(page, final_table) 


def overview_page(data, antibiotics_table):
    ### Header
    st.markdown('<div class="header">Patient-Specific Antibiotic Recommendations <span style="float:right;">resist.ai</span></div>', unsafe_allow_html=True)

    ### Bacteria Classified
    st.markdown(f"""<div class="section blue"><b>Bacteria Identification</b></div>""", unsafe_allow_html=True)
    # value = f"**{data['bacteria_classified']}**   Predicted Confidence: {data['bacteria_confidence']:.2%}"
    # st.markdown(f"""
    #     <div class="metric-container">
    #         <p class="metric-label">Predicted Susceptibility</p>
    #         <p class="metric-value">{value}</p>
    #     </div>
    # """, unsafe_allow_html=True)
    # st.write(f"**{data['bacteria_classified']}**   Predicted Confidence: {data['bacteria_confidence']:.2%}")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Bacteria Classified", value=data['bacteria_classified'])
    with col2:
        st.metric(label="Predicted Confidence", value= f"{data['bacteria_confidence']:.2%}")
    #col.markdown(f"**{data['bacteria_classified']}**   Predicted Certainty: {data['bacteria_certainty']:.2%}")

    # ### Diagnosis
    # st.markdown('<div class="section orange"><b>Diagnosis</b></div>', unsafe_allow_html=True)
    # st.write(f"{data['diagnosis']}")

    ### Recommended antibiotics
    st.markdown('<div class="section green"><b>Recommended Antibiotic Options</b></div>', unsafe_allow_html=True)
    st.write("\n")
    
    # st.data_editor(antibiotics_table.to_dict(orient='records'))
    st.data_editor(antibiotics_table[['Recommended', 'Use Tier', 'Antibiotic', 'Predicted Susceptibility', 'Confidence']].to_dict(orient='records'))
    ### Stock and Usage Information
    # st.data_editor(stocks.to_dict(orient='records'))

    ### Historical Treatment Response
    # st.markdown('<div class="section blue"><b>Historical Treatment Response</b></div>', unsafe_allow_html=True)
    # st.write(f"{data['historical_response']}")


def graph_features(feature_importance, antibiotic_name):
    primary_blue = "#4a6fa5"
    accent_red = "#FF5555"
    background_color = "#f5f9fc"
    text_color = "#2c3e50"
    plt.rcParams["font.family"] = "Arial"

    sorted_items = sorted(feature_importance.items(), key=lambda x: abs(x[1]))[:5]
    features, importances = zip(*sorted_items)

    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor(background_color)
    ax.set_facecolor("white")

    colors = [primary_blue if val > 0 else accent_red for val in importances]
    bars = ax.barh(features, importances, color=colors, edgecolor="#ecf0f1", height=0.6)

    ax.set_title(f"Top 5 Contributing Factors for {antibiotic_name}", fontsize=16, color=text_color, pad=15)
    ax.set_xlabel("Importance Score", fontsize=12)
    ax.set_ylabel("")

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(primary_blue)
    ax.spines['bottom'].set_color(primary_blue)
    ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
    ax.grid(axis='x', linestyle='--', alpha=0.4)

    plt.tight_layout()
    st.pyplot(plt)


def switch_page(page, table):
    
        st.markdown(f'<div class="header">{page} Dashboard</div>', unsafe_allow_html=True)
        #st.title(f"{page} Dashboard")
        antibiotic_data = table[table["Antibiotic"] == page].iloc[0]

        # Display key information
        st.markdown('<div class="section blue"><b>Antibiotic Resistance Metrics</b></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Predicted Susceptibility", value=antibiotic_data["Predicted Susceptibility"])
        with col2:
            st.metric(label="Confidence", value= f"{float(antibiotic_data['Confidence'])*100:.1f}%")
        st.metric(label="Hospital Susceptibility", value=f"{float(random.randint(70, 100)):.1f}%")
        st.markdown('<div class="section green"><b>Antibiotic Stock Metrics</b></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Formulation Type", value=antibiotic_data["Formulation Type"])
        with col2:
            st.metric(label="Dose per Unit", value=antibiotic_data["Dose per Unit"])
        col3, col4 = st.columns(2)
        with col3:
            st.metric(label="Remaining Stock", value=antibiotic_data["Remaining Stock"])
        with col4:
            st.metric(label="Usage", value=antibiotic_data["Usage"])
        st.markdown('<div class="section grey"><b>Antibiotic Model Metrics</b></div>', unsafe_allow_html=True)
        graph_features(dict(antibiotic_data['Top Features']), page)


def main(): # input data here from model)
    data = {
        'bacteria_classified': st.session_state['bacteria_classified'],
        'bacteria_confidence': st.session_state['bacteria_confidence'],
        'antibiotic_susceptibility': st.session_state['antibiotic_susceptibility'],
        'antibiotic_confidence': st.session_state['antibiotic_confidence'],
        'f_importances' : st.session_state['f_importance']
        # 'diagnosis': 'N39.0: Urinary tract infection, site not specified',
        # 'historical_response': 'Patient previously responded well to ceftriaxone for similar infection (8 months ago)',
        #more stuff
    }
    make_page(data)


if __name__ == "__main__":
    main()
