"""
Main Executive Dashboard UI - Streamlit Frontend
Professional corporate design with advanced drill-down capabilities
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Optional

from config.settings import UI_THEME, REVENUE_CONFIG, KPI_TARGETS, CLIENTS, DEPARTMENTS
from core.database import get_database
from core.analytics import AnalyticsEngine
# 🚀 අලුතින් හැදූ Alerts Manager එක Import කිරීම
from core.alerts import NotificationManager


# Page configuration
st.set_page_config(
    page_title="Gamage Recruiters - Executive Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown(f"""
<style>
    .main {{
        background-color: {UI_THEME['background_color']};
    }}
    
    .stMetric {{
        background-color: {UI_THEME['card_background']};
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    
    .metric-card {{
        background: {UI_THEME['card_background']};
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid {UI_THEME['primary_color']};
        margin-bottom: 15px;
    }}
    
    .kpi-title {{
        color: {UI_THEME['text_secondary']};
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 5px;
    }}
    
    .kpi-value {{
        color: {UI_THEME['primary_color']};
        font-size: 32px;
        font-weight: 700;
        margin: 5px 0;
    }}
    
    .kpi-delta {{
        font-size: 14px;
        margin-top: 5px;
    }}
    
    h1 {{
        color: {UI_THEME['primary_color']};
        font-weight: 700;
    }}
    
    h2, h3 {{
        color: {UI_THEME['primary_color']};
    }}
    
    .sidebar .sidebar-content {{
        background-color: {UI_THEME['card_background']};
    }}
    
    div[data-testid="stSidebarNav"] {{
        background-color: {UI_THEME['primary_color']};
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_data(start_date: Optional[datetime] = None, 
              end_date: Optional[datetime] = None,
              force_refresh: bool = False):
    """Load and cache recruitment data"""
    db = get_database()
    return db.fetch_recruitment_data(start_date, end_date, force_refresh)


def format_currency(value: float) -> str:
    """Format currency values"""
    return f"{REVENUE_CONFIG['currency_symbol']} {value:,.2f}"


def format_number(value: float, decimals: int = 1) -> str:
    """Format numbers with thousand separators"""
    return f"{value:,.{decimals}f}"


def create_metric_card(title: str, value: str, delta: Optional[str] = None, 
                       delta_color: str = "normal"):
    """Create a styled metric card"""
    delta_html = ""
    if delta:
        color = UI_THEME['success_color'] if delta_color == "normal" else UI_THEME['accent_color']
        if delta_color == "inverse":
            color = UI_THEME['accent_color'] if "+" in delta else UI_THEME['success_color']
        delta_html = f'<div class="kpi-delta" style="color: {color};">{delta}</div>'
    
    return f"""
    <div class="metric-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """


def main():
    """Main dashboard application"""
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📊 Gamage Recruiters Executive Dashboard")
        st.caption("Real-time Recruitment Performance Analytics")
    
    with col2:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Sidebar filters
    st.sidebar.header("🎯 Filters & Controls")
    
    # Date range filter
    st.sidebar.subheader("Date Range")
    date_preset = st.sidebar.selectbox(
        "Quick Select",
        ["Last 7 Days", "Last 30 Days", "Last 3 Months", "Last 6 Months", "Custom Range"]
    )
    
    end_date = datetime.now()
    
    if date_preset == "Last 7 Days":
        start_date = end_date - timedelta(days=7)
    elif date_preset == "Last 30 Days":
        start_date = end_date - timedelta(days=30)
    elif date_preset == "Last 3 Months":
        start_date = end_date - timedelta(days=90)
    elif date_preset == "Last 6 Months":
        start_date = end_date - timedelta(days=180)
    else:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            start_date = st.date_input("Start", end_date - timedelta(days=30))
        with col2:
            end_date = st.date_input("End", end_date)
        start_date = datetime.combine(start_date, datetime.min.time())
        end_date = datetime.combine(end_date, datetime.max.time())
    
    # Client filter
    st.sidebar.subheader("Client Filter")
    selected_clients = st.sidebar.multiselect(
        "Select Clients",
        options=["All"] + CLIENTS,
        default=["All"]
    )
    
    # Department filter
    st.sidebar.subheader("Department Filter")
    selected_departments = st.sidebar.multiselect(
        "Select Departments",
        options=["All"] + DEPARTMENTS,
        default=["All"]
    )
    
    # Status filter
    st.sidebar.subheader("Status Filter")
    selected_statuses = st.sidebar.multiselect(
        "Select Statuses",
        options=["All", "Placed", "Interviewing", "Screening", "Rejected"],
        default=["All"]
    )
    
    st.sidebar.divider()
    
    # Export options
    st.sidebar.subheader("📥 Export Options")
    if st.sidebar.button("Generate Weekly Report", use_container_width=True):
        from automation.report_worker import ReportWorker
        worker = ReportWorker()
        with st.spinner("Generating report..."):
            report_meta = worker.generate_weekly_report()
            st.sidebar.success(f"Report generated: {report_meta['report_id']}")
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data(start_date, end_date)
    
    # Apply filters
    filtered_df = df.copy()
    
    if "All" not in selected_clients:
        filtered_df = filtered_df[filtered_df['client'].isin(selected_clients)]
    
    if "All" not in selected_departments:
        filtered_df = filtered_df[filtered_df['department'].isin(selected_departments)]
    
    if "All" not in selected_statuses:
        filtered_df = filtered_df[filtered_df['status'].isin(selected_statuses)]
    
    # Initialize analytics
    analytics = AnalyticsEngine(filtered_df)
    kpis = analytics.calculate_executive_kpis()
    health = analytics.calculate_pipeline_health()
    
    # Display filter info
    st.info(f"📅 Showing data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')} | "
            f"📊 {len(filtered_df)} records")
    
    # Executive KPI Summary
    st.header("🎯 Executive KPI Summary")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        placement_delta = f"{kpis['placement_target_achievement']*100:.1f}% of target"
        st.markdown(
            create_metric_card(
                "Total Placements",
                str(kpis['total_placements']),
                placement_delta,
                "normal"
            ),
            unsafe_allow_html=True
        )
    
    with kpi_col2:
        revenue_delta = f"{kpis['revenue_target_achievement']*100:.1f}% of target"
        st.markdown(
            create_metric_card(
                "Total Revenue",
                format_currency(kpis['total_revenue']),
                revenue_delta,
                "normal"
            ),
            unsafe_allow_html=True
        )
    
    with kpi_col3:
        time_delta = f"Target: {KPI_TARGETS['avg_time_to_hire_days']} days"
        st.markdown(
            create_metric_card(
                "Avg Time-to-Hire",
                f"{kpis['avg_time_to_hire']:.1f} days",
                time_delta,
                "inverse"  # Lower is better
            ),
            unsafe_allow_html=True
        )
    
    with kpi_col4:
        pipeline_delta = f"{health['overall_health_score']:.0f}/100 health"
        st.markdown(
            create_metric_card(
                "Active Pipeline",
                str(kpis['active_pipeline']),
                pipeline_delta,
                "normal"
            ),
            unsafe_allow_html=True
        )
    
    # Secondary metrics
    st.subheader("📈 Performance Indicators")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric(
            "Placement Rate",
            f"{kpis['placement_rate']*100:.1f}%",
            f"{(kpis['placement_rate'] - 0.22)*100:.1f}%"
        )
    
    with metric_col2:
        st.metric(
            "Avg Revenue/Placement",
            format_currency(kpis['avg_revenue_per_placement']),
            ""
        )
    
    with metric_col3:
        st.metric(
            "Median Time-to-Hire",
            f"{kpis['median_time_to_hire']:.0f} days",
            ""
        )
    
    with metric_col4:
        st.metric(
            "Total Candidates",
            format_number(kpis['total_candidates'], 0),
            ""
        )
    
    st.divider()
    
    # Visualization Section
    st.header("📊 Visual Analytics")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Trends & Performance",
        "👥 Client Analysis",
        "🏢 Department Insights",
        "⚙️ Pipeline Health"
    ])
    
    # Tab 1: Trends
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Revenue Trend")
            trend_data = analytics.calculate_trend_analysis('M')
            
            fig_revenue = go.Figure()
            fig_revenue.add_trace(go.Bar(
                x=trend_data['period'],
                y=trend_data['revenue'],
                name='Revenue',
                marker_color=UI_THEME['primary_color'],
                text=trend_data['revenue'].apply(lambda x: format_currency(x)),
                textposition='outside'
            ))
            
            fig_revenue.update_layout(
                height=400,
                showlegend=False,
                plot_bgcolor='white',
                xaxis_title="Period",
                yaxis_title="Revenue (LKR)",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            st.subheader("Placement Trend")
            
            fig_placements = go.Figure()
            fig_placements.add_trace(go.Scatter(
                x=trend_data['period'],
                y=trend_data['placements'],
                mode='lines+markers',
                name='Placements',
                line=dict(color=UI_THEME['secondary_color'], width=3),
                marker=dict(size=10),
                text=trend_data['placements'],
                textposition='top center'
            ))
            
            fig_placements.add_hline(
                y=KPI_TARGETS['monthly_placements'],
                line_dash="dash",
                line_color="red",
                annotation_text="Target"
            )
            
            fig_placements.update_layout(
                height=400,
                showlegend=True,
                plot_bgcolor='white',
                xaxis_title="Period",
                yaxis_title="Placements",
                hovermode='x unified'
            )
            
            st.plotly_chart(fig_placements, use_container_width=True)
        
        # Pipeline funnel
        st.subheader("Conversion Funnel")
        
        funnel_data = pd.DataFrame({
            'Stage': ['Total Candidates', 'Screening', 'Interviewing', 'Placed'],
            'Count': [
                kpis['total_candidates'],
                kpis['screening_count'],
                kpis['interviewing_count'],
                kpis['total_placements']
            ]
        })
        
        fig_funnel = go.Figure(go.Funnel(
            y=funnel_data['Stage'],
            x=funnel_data['Count'],
            textinfo="value+percent initial",
            marker=dict(color=[UI_THEME['primary_color'], UI_THEME['secondary_color'], 
                              UI_THEME['success_color'], UI_THEME['accent_color']])
        ))
        
        fig_funnel.update_layout(height=400)
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    # Tab 2: Client Analysis
    with tab2:
        client_perf = analytics.calculate_client_performance()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top Clients by Revenue")
            
            top_clients = client_perf.head(10)
            
            fig_client_revenue = px.bar(
                top_clients,
                x='total_revenue',
                y='client',
                orientation='h',
                text='total_revenue',
                color='total_revenue',
                color_continuous_scale='Blues'
            )
            
            fig_client_revenue.update_traces(
                texttemplate='%{text:,.0f}',
                textposition='outside'
            )
            
            fig_client_revenue.update_layout(
                height=500,
                showlegend=False,
                xaxis_title="Revenue (LKR)",
                yaxis_title="",
                yaxis={'categoryorder': 'total ascending'}
            )
            
            st.plotly_chart(fig_client_revenue, use_container_width=True)
        
        with col2:
            st.subheader("Client Conversion Rates")
            
            fig_conversion = px.scatter(
                top_clients,
                x='total_candidates',
                y='conversion_rate',
                size='total_revenue',
                color='placements',
                hover_data=['client', 'placements', 'total_revenue'],
                color_continuous_scale='Viridis'
            )
            
            fig_conversion.update_layout(
                height=500,
                xaxis_title="Total Candidates",
                yaxis_title="Conversion Rate (%)",
            )
            
            st.plotly_chart(fig_conversion, use_container_width=True)
        
        # Client performance table
        st.subheader("Detailed Client Metrics")
        
        display_df = client_perf[['client', 'placements', 'total_revenue', 
                                   'conversion_rate', 'avg_days_in_pipeline']].copy()
        display_df['total_revenue'] = display_df['total_revenue'].apply(format_currency)
        display_df['conversion_rate'] = display_df['conversion_rate'].apply(lambda x: f"{x:.1f}%")
        display_df['avg_days_in_pipeline'] = display_df['avg_days_in_pipeline'].apply(lambda x: f"{x:.1f}")
        
        display_df.columns = ['Client', 'Placements', 'Total Revenue', 'Conversion Rate', 'Avg Days']
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            height=400
        )
    
    # Tab 3: Department Insights
    with tab3:
        dept_perf = analytics.calculate_department_performance()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Department Placements")
            
            fig_dept_placements = px.pie(
                dept_perf,
                values='placements',
                names='department',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Blues_r
            )
            
            fig_dept_placements.update_traces(
                textposition='inside',
                textinfo='percent+label'
            )
            
            fig_dept_placements.update_layout(height=500)
            
            st.plotly_chart(fig_dept_placements, use_container_width=True)
        
        with col2:
            st.subheader("Department Revenue Distribution")
            
            fig_dept_revenue = px.bar(
                dept_perf,
                x='department',
                y='total_revenue',
                color='conversion_rate',
                color_continuous_scale='RdYlGn'
            )
            
            fig_dept_revenue.update_layout(
                height=500,
                xaxis_title="",
                yaxis_title="Revenue (LKR)",
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_dept_revenue, use_container_width=True)
        
        # Department comparison
        st.subheader("Department Performance Matrix")
        
        fig_matrix = px.scatter(
            dept_perf,
            x='avg_days_in_pipeline',
            y='conversion_rate',
            size='total_revenue',
            color='placements',
            text='department',
            color_continuous_scale='Viridis'
        )
        
        fig_matrix.update_traces(textposition='top center')
        
        fig_matrix.update_layout(
            height=500,
            xaxis_title="Avg Days in Pipeline",
            yaxis_title="Conversion Rate (%)"
        )
        
        st.plotly_chart(fig_matrix, use_container_width=True)
    
    # Tab 4: Pipeline Health
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Pipeline Status Distribution")
            
            status_counts = filtered_df['status'].value_counts()
            
            fig_status = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                text=status_counts.values,
                color=status_counts.index,
                color_discrete_map={
                    'Placed': UI_THEME['success_color'],
                    'Interviewing': UI_THEME['secondary_color'],
                    'Screening': UI_THEME['primary_color'],
                    'Rejected': UI_THEME['accent_color']
                }
            )
            
            fig_status.update_traces(textposition='outside')
            
            fig_status.update_layout(
                height=400,
                showlegend=False,
                xaxis_title="Status",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig_status, use_container_width=True)
        
        with col2:
            st.subheader("Pipeline Health Score")
            
            # Gauge chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=health['overall_health_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Health Score", 'font': {'size': 24}},
                delta={'reference': 80},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': UI_THEME['primary_color']},
                    'steps': [
                        {'range': [0, 50], 'color': "#ffebee"},
                        {'range': [50, 75], 'color': "#fff9c4"},
                        {'range': [75, 100], 'color': "#c8e6c9"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig_gauge.update_layout(height=400)
            
            st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Health metrics
        st.subheader("Pipeline Metrics")
        
        health_col1, health_col2, health_col3, health_col4 = st.columns(4)
        
        with health_col1:
            st.metric("Active Candidates", health['active_candidates'])
        
        with health_col2:
            st.metric("Avg Pipeline Age", f"{health['avg_age_of_pipeline']:.1f} days")
        
        with health_col3:
            st.metric("Projected Placements (30d)", health['projected_placements_30d'])
        
        with health_col4:
            st.metric("Pipeline Velocity", f"{health['pipeline_velocity']:.1f}/week")
        
        # Time-to-hire distribution
        st.subheader("Time-to-Hire Distribution (Placed Candidates)")
        
        placed_df = filtered_df[filtered_df['status'] == 'Placed']
        
        if len(placed_df) > 0:
            fig_time_dist = px.histogram(
                placed_df,
                x='days_in_pipeline',
                nbins=20,
                color_discrete_sequence=[UI_THEME['primary_color']]
            )
            
            fig_time_dist.update_layout(
                height=400,
                xaxis_title="Days to Hire",
                yaxis_title="Count",
                showlegend=False
            )
            
            st.plotly_chart(fig_time_dist, use_container_width=True)
        else:
            st.info("No placement data available for the selected filters")
    
    st.divider()
    
    # Detailed Data Table
    st.header("📋 Detailed Candidate Data")
    
    # Column selector
    all_columns = filtered_df.columns.tolist()
    default_columns = ['candidate_id', 'client', 'department', 'status', 
                      'days_in_pipeline', 'revenue_lkr', 'application_date']
    
    selected_columns = st.multiselect(
        "Select Columns to Display",
        options=all_columns,
        default=default_columns
    )
    
    if selected_columns:
        display_table = filtered_df[selected_columns].copy()
        
        # Format display
        if 'revenue_lkr' in selected_columns:
            display_table['revenue_lkr'] = display_table['revenue_lkr'].apply(
                lambda x: format_currency(x) if x > 0 else "-"
            )
        
        if 'application_date' in selected_columns:
            display_table['application_date'] = pd.to_datetime(
                display_table['application_date']
            ).dt.strftime('%Y-%m-%d')
        
        st.dataframe(
            display_table,
            use_container_width=True,
            hide_index=True,
            height=500
        )
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Dataset (CSV)",
            data=csv,
            file_name=f"gamage_recruiters_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
        
    # 🚀 --- අලුතින් එකතු කළ සජීවී වාර්තා බෙදා හැරීමේ කොටස (Live Executive Report Section) ---
    st.divider()
    st.header("📩 Executive Report Distribution")
    st.caption("Instantly dispatch live data insights to the Executive Board.")
    
    # ⚠️ Dehan Sir ගේ ඊමේල් එක සහ වට්සැප් නම්බර් එක මෙතනට සෙට් කරන්න මචන්
    target_email = "virajrajaka12@gmail.com"
    target_phone = "+94775679167" 

    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("🚀 Generate & Email Report to Dehan Sir", use_container_width=True):
            with st.spinner("Compiling summary metrics and sending email..."):
                # ඩෑෂ්බෝඩ් එකෙන් සාරාංශ දත්ත ගණනය කිරීම
                total_placements = len(filtered_df[filtered_df['status'] == 'Placed'])
                total_revenue = filtered_df[filtered_df['status'] == 'Placed']['revenue_lkr'].sum()
                total_candidates = len(filtered_df)
                formatted_revenue = format_currency(total_revenue)

                # Email එකට යන HTML Layout එක
                html_email_content = f"""
                <html>
                    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
                        <h2 style="color: #1E3A8A;">Gamage Recruiters - Executive Performance Summary</h2>
                        <p>Dear Dehan Sir,</p>
                        <p>The recruitment pipeline data has been compiled. Here are the key metrics from the active dashboard session:</p>
                        <table style="border-collapse: collapse; width: 100%; max-width: 500px; margin-top: 15px;">
                            <tr style="background-color: #F3F4F6;">
                                <th style="border: 1px solid #D1D5DB; padding: 10px; text-align: left;">Metric</th>
                                <th style="border: 1px solid #D1D5DB; padding: 10px; text-align: left;">Value</th>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #D1D5DB; padding: 10px;">Total Pipeline Applications</td>
                                <td style="border: 1px solid #D1D5DB; padding: 10px; font-weight: bold;">{total_candidates}</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #D1D5DB; padding: 10px;">Successful Placements</td>
                                <td style="border: 1px solid #D1D5DB; padding: 10px; color: green; font-weight: bold;">{total_placements}</td>
                            </tr>
                            <tr>
                                <td style="border: 1px solid #D1D5DB; padding: 10px;">Total Revenue</td>
                                <td style="border: 1px solid #D1D5DB; padding: 10px; color: #1E3A8A; font-weight: bold;">{formatted_revenue}</td>
                            </tr>
                        </table>
                        <br>
                        <p style="font-size: 12px; color: #6B7280;">This is an automated system notification generated directly from the Executive Insights Dashboard container.</p>
                    </body>
                </html>
                """
                notifier = NotificationManager()
                if notifier.send_email_report(target_email, "📊 Recruitment Dashboard Executive Report", html_email_content):
                    st.success(f"🎯 Report successfully compiled and emailed to Dehan Sir ({target_email})!")
                else:
                    st.error("⚠️ Failed to send email. Please check your SMTP credentials inside `core/alerts.py`.")

    with btn_col2:
        if st.button("💬 Send Quick WhatsApp Summary to Dehan Sir", use_container_width=True):
            with st.spinner("Compiling summary and dispatching WhatsApp alert..."):
                total_placements = len(filtered_df[filtered_df['status'] == 'Placed'])
                total_revenue = filtered_df[filtered_df['status'] == 'Placed']['revenue_lkr'].sum()
                total_candidates = len(filtered_df)
                formatted_revenue = format_currency(total_revenue)

                whatsapp_msg = (
                    "📊 *Gamage Recruiters - Live Executive Insights*\n\n"
                    f"Hello Dehan Sir, here is the quick recruitment update generated just now:\n\n"
                    f"• Total Applicants: *{total_candidates}*\n"
                    f"• Successful Placements: *{total_placements}*\n"
                    f"• Total Revenue Generated: *{formatted_revenue}*\n\n"
                    "📈 Dashboard Status: Online\n"
                    "Report generated successfully via Streamlit Platform."
                )
                notifier = NotificationManager()
                # Twilio ලොජික් එක සක්‍රීය නම් විතරක් වැඩ කරයි
                if hasattr(notifier, 'send_whatsapp_report') and notifier.send_whatsapp_report(target_phone, whatsapp_msg):
                    st.success(f"🎯 Live summary dispatched to Dehan Sir via WhatsApp ({target_phone})!")
                else:
                    st.warning("⚠️ Twilio configuration not fully verified in `core/alerts.py`, but text generation is ready!")
    
    # Footer
    st.divider()
    st.caption(f"© 2024 Gamage Recruiters | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
              f"Data Range: {len(filtered_df)} records")


if __name__ == "__main__":
    main()