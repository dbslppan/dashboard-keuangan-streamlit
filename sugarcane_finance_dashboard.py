import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(page_title="Dashboard Monitoring Pembiayaan Petani Tebu", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
    }
    .alert-good {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
    }
    .section-header {
        font-size: 1.5em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Generate sample data
@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    
    # Monthly portfolio data
    months = pd.date_range(start='2024-01-01', end='2025-11-01', freq='MS')
    portfolio_data = pd.DataFrame({
        'Bulan': months,
        'KUR_Disbursed': np.random.randint(5000, 15000, len(months)) * 1000000,
        'KUR_Khusus_Disbursed': np.random.randint(3000, 8000, len(months)) * 1000000,
        'KUR_Outstanding': np.cumsum(np.random.randint(3000, 10000, len(months)) * 1000000),
        'KUR_Khusus_Outstanding': np.cumsum(np.random.randint(2000, 6000, len(months)) * 1000000),
        'NPL_Rate': np.random.uniform(1.5, 4.5, len(months)),
        'Collection_Rate': np.random.uniform(85, 97, len(months))
    })
    
    # Regional data
    regions = ['Jawa Timur', 'Jawa Tengah', 'Lampung', 'Sumatera Selatan', 'Sulawesi Selatan']
    regional_data = pd.DataFrame({
        'Region': regions,
        'Total_Kredit': np.random.randint(50000, 200000, len(regions)) * 1000000,
        'Jumlah_Debitur': np.random.randint(500, 2000, len(regions)),
        'NPL_Rate': np.random.uniform(1.0, 5.0, len(regions)),
        'Luas_Lahan_Ha': np.random.randint(1000, 5000, len(regions)),
        'Rata_Kredit_per_Petani': np.random.randint(20, 80, len(regions)) * 1000000
    })
    
    # Loan aging data
    aging_data = pd.DataFrame({
        'Kategori': ['Lancar', '1-30 Hari', '31-60 Hari', '61-90 Hari', '>90 Hari'],
        'KUR': [850000000000, 45000000000, 25000000000, 15000000000, 35000000000],
        'KUR_Khusus': [520000000000, 28000000000, 18000000000, 10000000000, 24000000000]
    })
    
    # Farmer segmentation
    segment_data = pd.DataFrame({
        'Segmen': ['Petani Individu', 'Kelompok Tani', 'Pemula (<2 tahun)', 'Berpengalaman (>2 tahun)'],
        'Jumlah': [3200, 1800, 1500, 3500],
        'Total_Kredit': [640000000000, 480000000000, 280000000000, 840000000000],
        'NPL_Rate': [3.2, 1.8, 4.5, 2.1]
    })
    
    return portfolio_data, regional_data, aging_data, segment_data

portfolio_data, regional_data, aging_data, segment_data = generate_sample_data()

# Header
st.title("📊 Dashboard Monitoring Pembiayaan Petani Tebu KUR")
st.markdown("**Sistem Monitoring Kredit Usaha Rakyat untuk Petani Tebu Indonesia**")

# Filters
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    selected_month = st.date_input("Periode", datetime.now())
with col2:
    selected_region = st.selectbox("Region", ["Semua Region"] + list(regional_data['Region']))
with col3:
    selected_loan_type = st.selectbox("Jenis Kredit", ["Semua", "KUR", "KUR Khusus"])
with col4:
    selected_masa_tanam = st.selectbox("Masa Tanam", ["Semua", "Musim Tanam 1", "Musim Tanam 2"])
with col5:
    selected_bank = st.selectbox("Bank", ["Semua Bank", "BRI", "BNI", "Mandiri", "BTN"])

# Refresh button
if st.button("🔄 Refresh Data", type="primary"):
    st.cache_data.clear()
    st.rerun()

st.divider()

# ===== SECTION 1: KEY PERFORMANCE INDICATORS =====
st.markdown('<div class="section-header">📈 Indikator Kinerja Utama (KPI)</div>', unsafe_allow_html=True)

current_month_data = portfolio_data.iloc[-1]
prev_month_data = portfolio_data.iloc[-2]

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    total_outstanding = current_month_data['KUR_Outstanding'] + current_month_data['KUR_Khusus_Outstanding']
    st.metric(
        "Total Kredit Berjalan",
        f"Rp {total_outstanding/1e9:.2f} M",
        f"{((total_outstanding - (prev_month_data['KUR_Outstanding'] + prev_month_data['KUR_Khusus_Outstanding']))/1e9):.2f} M"
    )

with col2:
    total_disbursed = current_month_data['KUR_Disbursed'] + current_month_data['KUR_Khusus_Disbursed']
    st.metric(
        "Total Kredit Selesai",
        f"Rp {total_disbursed/1e9:.2f} M",
        f"{((total_disbursed - (prev_month_data['KUR_Disbursed'] + prev_month_data['KUR_Khusus_Disbursed']))/1e9):.2f} M"
    )

with col3:
    target_kredit = 15000000000000  # 15 Trillion target
    achievement = (total_outstanding / target_kredit) * 100
    st.metric(
        "Pencapaian Target",
        f"{achievement:.1f}%",
        f"{(achievement - 85):.1f}%"
    )

with col4:
    npl_rate = current_month_data['NPL_Rate']
    npl_delta = npl_rate - prev_month_data['NPL_Rate']
    st.metric(
        "NPL Rate",
        f"{npl_rate:.2f}%",
        f"{npl_delta:.2f}%",
        delta_color="inverse"
    )

with col5:
    collection_rate = current_month_data['Collection_Rate']
    collection_delta = collection_rate - prev_month_data['Collection_Rate']
    st.metric(
        "Collection Rate",
        f"{collection_rate:.1f}%",
        f"{collection_delta:.1f}%"
    )

with col6:
    total_debitur = regional_data['Jumlah_Debitur'].sum()
    st.metric(
        "Jumlah Debitur Aktif",
        f"{total_debitur:,}",
        "+127"
    )

# Additional KPIs
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    avg_loan = total_outstanding / total_debitur
    st.metric(
        "Rata² Kredit/Petani",
        f"Rp {avg_loan/1e6:.1f} Jt"
    )

with col2:
    total_lahan = regional_data['Luas_Lahan_Ha'].sum()
    st.metric(
        "Total Lahan (Ha)",
        f"{total_lahan:,}"
    )

with col3:
    restructured_rate = 2.3
    st.metric(
        "Restrukturisasi",
        f"{restructured_rate:.1f}%"
    )

with col4:
    utilization_rate = 87.5
    st.metric(
        "Tingkat Utilisasi",
        f"{utilization_rate:.1f}%"
    )

with col5:
    coverage_ratio = 145
    st.metric(
        "Collateral Coverage",
        f"{coverage_ratio}%"
    )

with col6:
    subsidy_amount = 12500000000
    st.metric(
        "Subsidi Bunga",
        f"Rp {subsidy_amount/1e9:.1f} M"
    )

st.divider()

# ===== SECTION 2: PORTFOLIO ANALYSIS =====
st.markdown('<div class="section-header">💼 Analisis Portfolio Kredit</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Comparison Chart: KUR vs KUR Khusus
    fig_comparison = go.Figure()
    
    fig_comparison.add_trace(go.Bar(
        name='KUR',
        x=portfolio_data['Bulan'],
        y=portfolio_data['KUR_Outstanding']/1e9,
        marker_color='#1f77b4'
    ))
    
    fig_comparison.add_trace(go.Bar(
        name='KUR Khusus',
        x=portfolio_data['Bulan'],
        y=portfolio_data['KUR_Khusus_Outstanding']/1e9,
        marker_color='#ff7f0e'
    ))
    
    fig_comparison.update_layout(
        title='Grafik Perbandingan KUR vs KUR Khusus (Outstanding)',
        xaxis_title='Bulan',
        yaxis_title='Nilai Kredit (Miliar Rp)',
        barmode='group',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True)

with col2:
    # Portfolio Trend
    fig_trend = go.Figure()
    
    portfolio_data['Total_Outstanding'] = (portfolio_data['KUR_Outstanding'] + 
                                           portfolio_data['KUR_Khusus_Outstanding'])/1e9
    
    fig_trend.add_trace(go.Scatter(
        x=portfolio_data['Bulan'],
        y=portfolio_data['Total_Outstanding'],
        mode='lines+markers',
        name='Total Outstanding',
        line=dict(color='#2ca02c', width=3),
        fill='tonexty'
    ))
    
    # Add target line
    fig_trend.add_hline(y=15000, line_dash="dash", line_color="red", 
                        annotation_text="Target 2025: Rp 15 T")
    
    fig_trend.update_layout(
        title='Grafik Portfolio Kredit Tahunan',
        xaxis_title='Bulan',
        yaxis_title='Total Outstanding (Miliar Rp)',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)

# Quarterly Performance
col1, col2 = st.columns(2)

with col1:
    # Disbursement by Quarter
    portfolio_data['Quarter'] = portfolio_data['Bulan'].dt.to_period('Q').astype(str)
    quarterly_data = portfolio_data.groupby('Quarter').agg({
        'KUR_Disbursed': 'sum',
        'KUR_Khusus_Disbursed': 'sum'
    }).reset_index()
    
    fig_quarterly = go.Figure()
    fig_quarterly.add_trace(go.Bar(
        name='KUR',
        x=quarterly_data['Quarter'],
        y=quarterly_data['KUR_Disbursed']/1e9,
        marker_color='#1f77b4'
    ))
    fig_quarterly.add_trace(go.Bar(
        name='KUR Khusus',
        x=quarterly_data['Quarter'],
        y=quarterly_data['KUR_Khusus_Disbursed']/1e9,
        marker_color='#ff7f0e'
    ))
    
    fig_quarterly.update_layout(
        title='Penyaluran Kredit per Kuartal',
        xaxis_title='Kuartal',
        yaxis_title='Nilai Penyaluran (Miliar Rp)',
        barmode='stack',
        height=350
    )
    
    st.plotly_chart(fig_quarterly, use_container_width=True)

with col2:
    # NPL Trend
    fig_npl = go.Figure()
    
    fig_npl.add_trace(go.Scatter(
        x=portfolio_data['Bulan'],
        y=portfolio_data['NPL_Rate'],
        mode='lines+markers',
        name='NPL Rate',
        line=dict(color='#d62728', width=2),
        marker=dict(size=6)
    ))
    
    # Add threshold lines
    fig_npl.add_hline(y=5, line_dash="dash", line_color="orange", 
                      annotation_text="Threshold: 5%", annotation_position="right")
    fig_npl.add_hline(y=3, line_dash="dot", line_color="green", 
                      annotation_text="Target: <3%", annotation_position="right")
    
    fig_npl.update_layout(
        title='Trend Non-Performing Loan (NPL)',
        xaxis_title='Bulan',
        yaxis_title='NPL Rate (%)',
        height=350,
        yaxis_range=[0, 7]
    )
    
    st.plotly_chart(fig_npl, use_container_width=True)

st.divider()

# ===== SECTION 3: REGIONAL PERFORMANCE =====
st.markdown('<div class="section-header">🗺️ Kinerja Regional</div>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    # Regional distribution map (bar chart)
    fig_regional = px.bar(
        regional_data.sort_values('Total_Kredit', ascending=True),
        y='Region',
        x='Total_Kredit',
        color='NPL_Rate',
        orientation='h',
        title='Distribusi Kredit dan NPL per Region',
        labels={'Total_Kredit': 'Total Kredit (Rp)', 'NPL_Rate': 'NPL Rate (%)'},
        color_continuous_scale='RdYlGn_r',
        height=400
    )
    
    fig_regional.update_traces(
        text=regional_data.sort_values('Total_Kredit', ascending=True)['Total_Kredit'].apply(
            lambda x: f'Rp {x/1e9:.1f} M'
        ),
        textposition='outside'
    )
    
    st.plotly_chart(fig_regional, use_container_width=True)

with col2:
    st.markdown("#### 📊 Top 3 Region")
    
    top_regions = regional_data.nlargest(3, 'Total_Kredit')
    
    for idx, row in top_regions.iterrows():
        npl_class = "alert-good" if row['NPL_Rate'] < 3 else "alert-medium" if row['NPL_Rate'] < 5 else "alert-high"
        
        st.markdown(f"""
        <div class="metric-card {npl_class}">
            <h4>{row['Region']}</h4>
            <p><strong>Total Kredit:</strong> Rp {row['Total_Kredit']/1e9:.2f} M</p>
            <p><strong>Debitur:</strong> {row['Jumlah_Debitur']:,} petani</p>
            <p><strong>NPL Rate:</strong> {row['NPL_Rate']:.2f}%</p>
            <p><strong>Luas Lahan:</strong> {row['Luas_Lahan_Ha']:,} Ha</p>
        </div>
        <br>
        """, unsafe_allow_html=True)

# Regional detailed table
st.markdown("#### 📋 Detail Kinerja per Region")
regional_display = regional_data.copy()
regional_display['Total_Kredit'] = regional_display['Total_Kredit'].apply(lambda x: f"Rp {x/1e9:.2f} M")
regional_display['Rata_Kredit_per_Petani'] = regional_display['Rata_Kredit_per_Petani'].apply(lambda x: f"Rp {x/1e6:.1f} Jt")
regional_display['NPL_Rate'] = regional_display['NPL_Rate'].apply(lambda x: f"{x:.2f}%")
regional_display['Luas_Lahan_Ha'] = regional_display['Luas_Lahan_Ha'].apply(lambda x: f"{x:,} Ha")

st.dataframe(
    regional_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Region": "Region",
        "Total_Kredit": "Total Kredit",
        "Jumlah_Debitur": "Jumlah Debitur",
        "NPL_Rate": "NPL Rate",
        "Luas_Lahan_Ha": "Luas Lahan",
        "Rata_Kredit_per_Petani": "Rata² Kredit/Petani"
    }
)

st.divider()

# ===== SECTION 4: RISK ANALYSIS =====
st.markdown('<div class="section-header">⚠️ Analisis Risiko & Collection</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Aging analysis
    fig_aging = go.Figure()
    
    fig_aging.add_trace(go.Bar(
        name='KUR',
        x=aging_data['Kategori'],
        y=aging_data['KUR']/1e9,
        marker_color='#1f77b4'
    ))
    
    fig_aging.add_trace(go.Bar(
        name='KUR Khusus',
        x=aging_data['Kategori'],
        y=aging_data['KUR_Khusus']/1e9,
        marker_color='#ff7f0e'
    ))
    
    fig_aging.update_layout(
        title='Aging Analysis - Kualitas Kredit',
        xaxis_title='Kategori Kolektibilitas',
        yaxis_title='Nilai Kredit (Miliar Rp)',
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig_aging, use_container_width=True)

with col2:
    # Collection rate trend
    fig_collection = go.Figure()
    
    fig_collection.add_trace(go.Scatter(
        x=portfolio_data['Bulan'],
        y=portfolio_data['Collection_Rate'],
        mode='lines+markers',
        name='Collection Rate',
        line=dict(color='#2ca02c', width=3),
        fill='tonexty',
        marker=dict(size=6)
    ))
    
    fig_collection.add_hline(y=90, line_dash="dash", line_color="orange", 
                             annotation_text="Minimum Target: 90%")
    
    fig_collection.update_layout(
        title='Trend Collection Rate',
        xaxis_title='Bulan',
        yaxis_title='Collection Rate (%)',
        height=400,
        yaxis_range=[80, 100]
    )
    
    st.plotly_chart(fig_collection, use_container_width=True)

# Risk indicators
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card alert-good">
        <h4>✅ Kredit Lancar</h4>
        <h2>85.2%</h2>
        <p>Rp 1,370 M</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card alert-medium">
        <h4>⚠️ Dalam Perhatian Khusus</h4>
        <h2>6.8%</h2>
        <p>Rp 110 M</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card alert-medium">
        <h4>⚠️ Kurang Lancar</h4>
        <h2>4.5%</h2>
        <p>Rp 73 M</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card alert-high">
        <h4>🚨 Macet</h4>
        <h2>3.5%</h2>
        <p>Rp 57 M</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ===== SECTION 5: FARMER SEGMENTATION =====
st.markdown('<div class="section-header">👥 Segmentasi Debitur</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Farmer segmentation pie chart
    fig_segment = px.pie(
        segment_data,
        values='Jumlah',
        names='Segmen',
        title='Distribusi Debitur per Segmen',
        color_discrete_sequence=px.colors.qualitative.Set3,
        height=400
    )
    
    fig_segment.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig_segment, use_container_width=True)

with col2:
    # NPL by segment
    fig_segment_npl = px.bar(
        segment_data.sort_values('NPL_Rate'),
        x='Segmen',
        y='NPL_Rate',
        title='NPL Rate per Segmen Debitur',
        color='NPL_Rate',
        color_continuous_scale='RdYlGn_r',
        height=400
    )
    
    fig_segment_npl.update_traces(text=segment_data.sort_values('NPL_Rate')['NPL_Rate'].apply(lambda x: f'{x:.1f}%'))
    fig_segment_npl.add_hline(y=3, line_dash="dash", line_color="green", annotation_text="Target NPL: 3%")
    
    st.plotly_chart(fig_segment_npl, use_container_width=True)

# Segmentation details
st.markdown("#### 📋 Detail Segmentasi Debitur")

segment_display = segment_data.copy()
segment_display['Total_Kredit'] = segment_display['Total_Kredit'].apply(lambda x: f"Rp {x/1e9:.2f} M")
segment_display['NPL_Rate'] = segment_display['NPL_Rate'].apply(lambda x: f"{x:.2f}%")
segment_display['Rata_Kredit'] = segment_data.apply(lambda x: f"Rp {(x['Total_Kredit']/x['Jumlah'])/1e6:.1f} Jt", axis=1)

st.dataframe(
    segment_display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Segmen": "Segmen Debitur",
        "Jumlah": "Jumlah Debitur",
        "Total_Kredit": "Total Kredit",
        "NPL_Rate": "NPL Rate",
        "Rata_Kredit": "Rata² Kredit"
    }
)

st.divider()

# ===== SECTION 6: SEASONAL & AGRICULTURAL INSIGHTS =====
st.markdown('<div class="section-header">🌾 Analisis Musim Tanam & Produktivitas</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Harvest cycle alignment
    harvest_data = pd.DataFrame({
        'Bulan': ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des'],
        'Panen_Expected': [15, 18, 25, 30, 20, 15, 10, 12, 20, 28, 32, 25],
        'Pembayaran_Aktual': [14, 17, 24, 28, 19, 14, 9, 11, 19, 26, 30, 23]
    })
    
    fig_harvest = go.Figure()
    
    fig_harvest.add_trace(go.Scatter(
        x=harvest_data['Bulan'],
        y=harvest_data['Panen_Expected'],
        mode='lines+markers',
        name='Perkiraan Panen (%)',
        line=dict(color='#2ca02c', width=2)
    ))
    
    fig_harvest.add_trace(go.Scatter(
        x=harvest_data['Bulan'],
        y=harvest_data['Pembayaran_Aktual'],
        mode='lines+markers',
        name='Pembayaran Aktual (%)',
        line=dict(color='#1f77b4', width=2)
    ))
    
    fig_harvest.update_layout(
        title='Alignment Musim Panen vs Pembayaran Kredit',
        xaxis_title='Bulan',
        yaxis_title='Persentase dari Total Tahunan (%)',
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_harvest, use_container_width=True)

with col2:
    # Productivity vs loan performance
    productivity_data = pd.DataFrame({
        'Produktivitas': ['<60 ton/ha', '60-80 ton/ha', '80-100 ton/ha', '>100 ton/ha'],
        'Jumlah_Petani': [850, 1920, 1680, 550],
        'NPL_Rate': [5.2, 2.8, 1.9, 1.2],
        'Avg_Loan': [45, 62, 78, 95]
    })
    
    fig_productivity = go.Figure()
    
    fig_productivity.add_trace(go.Bar(
        name='Jumlah Petani',
        x=productivity_data['Produktivitas'],
        y=productivity_data['Jumlah_Petani'],
        marker_color='#2ca02c',
        yaxis='y',
        offsetgroup=1
    ))
    
    fig_productivity.add_trace(go.Scatter(
        name='NPL Rate',
        x=productivity_data['Produktivitas'],
        y=productivity_data['NPL_Rate'],
        marker_color='#d62728',
        yaxis='y2',
        mode='lines+markers',
        line=dict(width=3)
    ))
    
    fig_productivity.update_layout(
        title='Produktivitas Lahan vs Kinerja Kredit',
        xaxis_title='Tingkat Produktivitas',
        yaxis=dict(title='Jumlah Petani', side='left'),
        yaxis2=dict(title='NPL Rate (%)', side='right', overlaying='y'),
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_productivity, use_container_width=True)

st.divider()

# ===== SECTION 7: EARLY WARNING SYSTEM =====
st.markdown('<div class="section-header">🚨 Early Warning System</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card alert-high">
        <h4>🌧️ Risiko Cuaca</h4>
        <h3>TINGGI</h3>
        <p><strong>345 debitur</strong> di area rawan banjir</p>
        <p>Potensi dampak: Rp 28 M</p>
        <p style="margin-top: 10px;"><small>⚠️ Perlu monitoring intensif</small></p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card alert-medium">
        <h4>📉 Risiko Harga</h4>
        <h3>SEDANG</h3>
        <p><strong>Harga tebu:</strong> Rp 680/kg</p>
        <p>Turun 8.5% dari bulan lalu</p>
        <p style="margin-top: 10px;"><small>⚠️ Monitoring pembayaran</small></p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card alert-medium">
        <h4>⏰ Jatuh Tempo</h4>
        <h3>PERHATIAN</h3>
        <p><strong>682 debitur</strong> jatuh tempo 30 hari</p>
        <p>Total: Rp 54.6 M</p>
        <p style="margin-top: 10px;"><small>📞 Lakukan reminder call</small></p>
    </div>
    """, unsafe_allow_html=True)

# Alert details
st.markdown("#### 📋 Detail Alert Risiko")

alert_data = pd.DataFrame({
    'Prioritas': ['🔴 Tinggi', '🔴 Tinggi', '🟡 Sedang', '🟡 Sedang', '🟢 Rendah'],
    'Jenis Risiko': ['NPL > 5% di Jawa Timur', 'Delay pembayaran 30+ hari', 
                     'Produktivitas menurun 15%', 'Harga tebu turun 8.5%', 
                     'Keterlambatan 1-15 hari'],
    'Jumlah Debitur': [156, 234, 445, 'Area-based', 387],
    'Potensi Dampak': ['Rp 18.5 M', 'Rp 23.4 M', 'Rp 38.2 M', 'Rp 15.6 M', 'Rp 12.8 M'],
    'Tindakan': ['Site visit & restrukturisasi', 'Collection intensif', 
                 'Pendampingan teknis', 'Monitor harga pasar', 'Reminder call']
})

st.dataframe(alert_data, use_container_width=True, hide_index=True)

st.divider()

# ===== SECTION 8: COMPLIANCE & REPORTING =====
st.markdown('<div class="section-header">📊 Compliance & Reporting BI</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card alert-good">
        <h4>✅ PSR Compliance</h4>
        <h2>98.5%</h2>
        <p>Laporan lengkap dan tepat waktu</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card alert-good">
        <h4>✅ SLIK Integration</h4>
        <h2>100%</h2>
        <p>Data tersinkronisasi</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card alert-good">
        <h4>✅ GCG Score</h4>
        <h2>92/100</h2>
        <p>Good Corporate Governance</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card alert-medium">
        <h4>⚠️ Audit Finding</h4>
        <h2>3 Item</h2>
        <p>Dalam proses perbaikan</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ===== FOOTER & EXPORT =====
st.markdown('<div class="section-header">📥 Export & Actions</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Export Excel Report", use_container_width=True):
        st.success("✅ Report exported successfully!")

with col2:
    if st.button("📄 Generate PDF Summary", use_container_width=True):
        st.success("✅ PDF generated successfully!")

with col3:
    if st.button("📧 Email to Management", use_container_width=True):
        st.success("✅ Email sent successfully!")

with col4:
    if st.button("🔔 Set Alert Rules", use_container_width=True):
        st.info("Alert rules configuration opened!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Dashboard Monitoring Pembiayaan Petani Tebu KUR</strong></p>
    <p>LPP Agro Nusantara - Digital Transformation Team | Data updated: {}</p>
    <p style='font-size: 0.9em;'>Compliance: Bank Indonesia, OJK, & Internal Audit Standards</p>
</div>
""".format(datetime.now().strftime("%d %B %Y, %H:%M WIB")), unsafe_allow_html=True)
