import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Jeddah Library Intelligence",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Load artifacts ────────────────────────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    with open('model_artifacts.pkl', 'rb') as f:
        return pickle.load(f)

artifacts     = load_artifacts()
model         = artifacts['model']
model_type    = artifacts.get('model_type', 'neural_network')
scaler        = artifacts['scaler']
feature_cols  = artifacts['feature_cols']
df            = artifacts['df_clean']
comparison    = artifacts['comparison']
branch_totals = artifacts['branch_totals']
hour_avg      = artifacts['hour_avg']
fi_rf         = artifacts['fi_rf']
best_row      = comparison.iloc[0]
best_name     = best_row['Model']
best_r2       = best_row['R2']
best_mae      = best_row['MAE']

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 Jeddah Library\nDemand Intelligence Platform")
    st.markdown("---")
    st.markdown(
        "Built by **Fahad Alshehri**\n\n"
        "KAU IT · KAUST Advanced AI\n\n"
        "🔗 [GitHub](https://github.com/FahadAlshehrii)"
    )
    st.markdown("---")
    st.caption(f"{best_name} · R²={best_r2:.4f} · MAE={best_mae:.2f} rentals")

# ─── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "🔮 Demand Predictor",
    "📊 Branch Analytics",
    "🏆 Model Comparison"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — DEMAND PREDICTOR
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.header("🔮 Hourly Demand Predictor")
    st.markdown("Predict how many rentals a branch will receive and get a staffing recommendation.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📍 Location & Time**")
        branch = st.selectbox("Library Branch", sorted(df['Library_Branch'].unique()))
        hour   = st.slider("Hour of Day", 7, 22, 14)
        day_of_week = st.selectbox("Day of Week",
            ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'])
        season = st.selectbox("Season", sorted(df['Season'].unique()))

    with col2:
        st.markdown("**🌡️ Weather Conditions**")
        temperature = st.slider("Temperature (°C)", 10.0, 50.0, 28.0, 0.5)
        humidity    = st.slider("Humidity (%)", 10.0, 100.0, 55.0, 1.0)
        wind_speed  = st.slider("Wind Speed (m/s)", 0.0, 15.0, 5.0, 0.1)
        visibility  = st.slider("Visibility (m)", 100, 2000, 1200, 50)
        solar       = st.slider("Solar Radiation (MJ/m²)", 0.0, 4.0, 2.0, 0.1)
        rainfall    = st.slider("Rainfall (mm)", 0.0, 10.0, 0.0, 0.1)

    with col3:
        st.markdown("**📖 Visit Context**")
        category    = st.selectbox("Top Category", sorted(df['Top_Category'].unique()))
        membership  = st.selectbox("Membership Type", sorted(df['Membership_Type'].unique()))
        holiday     = st.selectbox("Holiday?", ['No', 'Yes'])
        month       = st.slider("Month", 1, 12, 6)
        day_num     = st.slider("Day of Month", 1, 31, 15)

    if st.button("🚀 Predict Demand", use_container_width=True, type="primary"):

        # Derived features
        is_peak = 1 if (9 <= hour <= 11) or (16 <= hour <= 19) else 0
        if temperature < 25:
            temp_bin = 'Cool'
        elif temperature <= 35:
            temp_bin = 'Warm'
        else:
            temp_bin = 'Hot'
        is_weekend = 1 if day_of_week in ['Friday', 'Saturday'] else 0

        # Build input row matching training feature columns
        input_dict = {col: 0 for col in feature_cols}
        input_dict['Hour']                  = hour
        input_dict['Temperature_C']         = temperature
        input_dict['Humidity_pct']          = humidity
        input_dict['Wind_Speed_ms']         = wind_speed
        input_dict['Visibility_m']          = visibility
        input_dict['Solar_Radiation_MJm2']  = solar
        input_dict['Rainfall_mm']           = rainfall
        input_dict['Month']                 = month
        input_dict['Day']                   = day_num
        input_dict['Is_Peak_Hour']          = is_peak
        input_dict['Is_Weekend']            = is_weekend

        # One-hot flags
        for col in feature_cols:
            if col.startswith('Season_') and col == f'Season_{season}':
                input_dict[col] = 1
            if col.startswith('Library_Branch_') and col == f'Library_Branch_{branch}':
                input_dict[col] = 1
            if col.startswith('Top_Category_') and col == f'Top_Category_{category}':
                input_dict[col] = 1
            if col.startswith('Membership_Type_') and col == f'Membership_Type_{membership}':
                input_dict[col] = 1
            if col.startswith('Day_of_Week_') and col == f'Day_of_Week_{day_of_week}':
                input_dict[col] = 1
            if col.startswith('Holiday_') and col == f'Holiday_{holiday}':
                input_dict[col] = 1
            if col.startswith('Temperature_Bin_') and col == f'Temperature_Bin_{temp_bin}':
                input_dict[col] = 1

        X_input = np.array([list(input_dict.values())])
        X_scaled = scaler.transform(X_input)

        # Neural Network returns 2D array — flatten it
        raw = model.predict(X_scaled, verbose=0)
        prediction = max(0, round(float(raw.flatten()[0])))

        # Staffing logic
        if prediction < 20:
            staff = 1
            staff_label = "🟢 Quiet — 1 staff member sufficient"
            color = "green"
        elif prediction < 40:
            staff = 2
            staff_label = "🟡 Moderate — 2 staff members recommended"
            color = "orange"
        elif prediction < 60:
            staff = 3
            staff_label = "🟠 Busy — 3 staff members recommended"
            color = "darkorange"
        else:
            staff = 4
            staff_label = "🔴 Peak demand — 4+ staff members needed"
            color = "red"

        st.markdown("---")
        r1, r2, r3 = st.columns(3)
        r1.metric("📦 Predicted Rentals", f"{prediction}", help="Hourly rental count")
        r2.metric("👥 Staff Recommended", f"{staff}", help="Based on demand level")
        r3.metric("⏰ Peak Hour?", "Yes ✅" if is_peak else "No ❌")

        st.markdown(f"**Staffing guidance:** {staff_label}")

        # Show hourly curve for this branch
        branch_df = df[df['Library_Branch'] == branch]
        hourly = branch_df.groupby('Hour')['Rentals_Count'].mean().reset_index()
        fig = px.line(hourly, x='Hour', y='Rentals_Count',
                      title=f"Average Hourly Demand — {branch}",
                      labels={'Rentals_Count': 'Avg Rentals', 'Hour': 'Hour of Day'},
                      markers=True, color_discrete_sequence=['#1f77b4'])
        fig.add_vline(x=hour, line_dash='dash', line_color='red',
                      annotation_text=f"Selected: {hour}:00")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — BRANCH ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.header("📊 Branch Analytics")

    col_a, col_b = st.columns(2)

    with col_a:
        # Total rentals by branch
        bt = branch_totals.reset_index()
        bt.columns = ['Branch', 'Total Rentals']
        fig1 = px.bar(bt, x='Total Rentals', y='Branch', orientation='h',
                      title='Total Rentals by Branch',
                      color='Total Rentals', color_continuous_scale='Blues')
        fig1.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        # Rentals by season
        season_avg = df.groupby('Season')['Rentals_Count'].mean().reset_index()
        fig2 = px.bar(season_avg, x='Season', y='Rentals_Count',
                      title='Average Rentals by Season',
                      color='Season', color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        # Hour of day curve
        hour_df = hour_avg.reset_index()
        hour_df.columns = ['Hour', 'Avg Rentals']
        fig3 = px.line(hour_df, x='Hour', y='Avg Rentals',
                       title='Average Rentals by Hour (All Branches)',
                       markers=True, color_discrete_sequence=['#e74c3c'])
        fig3.update_layout(height=350)
        st.plotly_chart(fig3, use_container_width=True)

    with col_d:
        # Day of week
        day_order = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
        day_df = df.groupby('Day_of_Week')['Rentals_Count'].mean().reindex(day_order).reset_index()
        day_df.columns = ['Day', 'Avg Rentals']
        fig4 = px.bar(day_df, x='Day', y='Avg Rentals',
                      title='Average Rentals by Day of Week',
                      color='Avg Rentals', color_continuous_scale='Purples')
        fig4.update_layout(height=350)
        st.plotly_chart(fig4, use_container_width=True)

    # Membership breakdown
    st.subheader("Membership Type Distribution")
    mem = df['Membership_Type'].value_counts().reset_index()
    mem.columns = ['Type', 'Count']
    fig5 = px.pie(mem, values='Count', names='Type',
                  title='Rentals by Membership Type',
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig5, use_container_width=True)

    # Key business insights
    st.subheader("📌 Key Insights for Management")
    busiest = branch_totals.idxmax()
    peak_h  = hour_avg.idxmax()
    best_day = df.groupby('Day_of_Week')['Rentals_Count'].mean().idxmax()
    busiest_mem = df['Membership_Type'].value_counts().idxmax()

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.info(f"📍 **Busiest branch:** {busiest} — prioritize staffing here")
        st.info(f"⏰ **Peak hour:** {peak_h}:00 — ensure full staff coverage from 16:00–19:00")
    with col_i2:
        st.info(f"📅 **Busiest day:** {best_day} — schedule extra staff")
        st.info(f"🪪 **Dominant membership:** {busiest_mem} — tailor promotions accordingly")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — MODEL COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.header("🏆 Model Comparison")
    st.markdown("Four ML models were trained and evaluated. Here's how they compare.")

    # Metrics table
    st.dataframe(
        comparison.style.highlight_max(subset=['R2'], color='#d4edda')
                        .highlight_min(subset=['MAE','RMSE'], color='#d4edda')
                        .format({'R2': '{:.4f}', 'MAE': '{:.2f}', 'RMSE': '{:.2f}'}),
        use_container_width=True
    )

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        fig_r2 = px.bar(comparison, x='Model', y='R2',
                        title='R² Score by Model (higher = better)',
                        color='R2', color_continuous_scale='Greens',
                        text='R2')
        fig_r2.update_traces(texttemplate='%{text:.3f}', textposition='outside')
        fig_r2.update_layout(yaxis_range=[0, 1.05], height=380)
        st.plotly_chart(fig_r2, use_container_width=True)

    with col_m2:
        fig_mae = px.bar(comparison, x='Model', y='MAE',
                         title='MAE by Model (lower = better)',
                         color='MAE', color_continuous_scale='Reds_r',
                         text='MAE')
        fig_mae.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_mae.update_layout(height=380)
        st.plotly_chart(fig_mae, use_container_width=True)

    # Feature importance
    st.subheader("🔍 Top 10 Most Important Features (Random Forest)")
    fi_df = fi_rf.reset_index()
    fi_df.columns = ['Feature', 'Importance']
    fi_df = fi_df.sort_values('Importance', ascending=True)
    fig_fi = px.bar(fi_df, x='Importance', y='Feature', orientation='h',
                    color='Importance', color_continuous_scale='Teal',
                    title='Feature Importances — Random Forest')
    fig_fi.update_layout(height=420)
    st.plotly_chart(fig_fi, use_container_width=True)

    # Conclusion
    st.subheader("📝 Conclusion")
    st.success(
        "**Random Forest performed best** with R²=0.92, MAE=4.3, RMSE=5.9. "
        "It outperformed Linear Regression and Decision Tree because it handles non-linear "
        "relationships between weather, time, and rental demand — and reduces overfitting "
        "through ensemble averaging across 100 trees.\n\n"
        "**Key drivers of demand:** Hour of day, temperature, humidity, and branch location "
        "are the strongest predictors. Evening hours (16–19) consistently drive peak demand "
        "across all branches, and Downtown Central is the highest-volume branch requiring "
        "priority staffing investment."
    )
