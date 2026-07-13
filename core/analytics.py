"""
Analytics Engine - Heavy Aggregation & Executive Metrics
Calculates critical KPIs and performance indicators
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

from config.settings import KPI_TARGETS, REVENUE_CONFIG, PERFORMANCE_THRESHOLDS


class AnalyticsEngine:
    """
    Advanced analytics processing for executive insights
    """
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.currency_symbol = REVENUE_CONFIG['currency_symbol']
        
    def calculate_executive_kpis(self) -> Dict[str, any]:
        """
        Calculate top-level executive KPI summary
        
        Returns:
            Dictionary containing all critical executive metrics
        """
        
        total_candidates = len(self.data)
        placed = self.data[self.data['status'] == 'Placed']
        
        kpis = {
            # Core Metrics
            'total_placements': len(placed),
            'total_revenue': placed['revenue_lkr'].sum(),
            'total_candidates': total_candidates,
            'active_pipeline': len(self.data[self.data['status'].isin(['Interviewing', 'Screening'])]),
            
            # Performance Metrics
            'avg_time_to_hire': placed['days_in_pipeline'].mean() if len(placed) > 0 else 0,
            'avg_revenue_per_placement': placed['revenue_lkr'].mean() if len(placed) > 0 else 0,
            
            # Conversion Metrics
            'placement_rate': len(placed) / total_candidates if total_candidates > 0 else 0,
            'interviewing_count': len(self.data[self.data['status'] == 'Interviewing']),
            'screening_count': len(self.data[self.data['status'] == 'Screening']),
            'rejected_count': len(self.data[self.data['status'] == 'Rejected']),
            
            # Time-based Metrics
            'median_time_to_hire': placed['days_in_pipeline'].median() if len(placed) > 0 else 0,
            'fastest_hire': placed['days_in_pipeline'].min() if len(placed) > 0 else 0,
            'slowest_hire': placed['days_in_pipeline'].max() if len(placed) > 0 else 0,
        }
        
        # Calculate target achievement percentages
        kpis['placement_target_achievement'] = (
            kpis['total_placements'] / KPI_TARGETS['monthly_placements']
        ) if KPI_TARGETS['monthly_placements'] > 0 else 0
        
        kpis['revenue_target_achievement'] = (
            kpis['total_revenue'] / KPI_TARGETS['monthly_revenue']
        ) if KPI_TARGETS['monthly_revenue'] > 0 else 0
        
        # Time efficiency (lower is better, so invert)
        if kpis['avg_time_to_hire'] > 0:
            kpis['time_efficiency_score'] = (
                KPI_TARGETS['avg_time_to_hire_days'] / kpis['avg_time_to_hire']
            )
        else:
            kpis['time_efficiency_score'] = 0
            
        return kpis
    
    def calculate_trend_analysis(self, period: str = 'M') -> pd.DataFrame:
        """
        Calculate time-series trend analysis
        
        Args:
            period: Pandas frequency string ('D', 'W', 'M', 'Q')
            
        Returns:
            DataFrame with time-series metrics
        """
        
        df = self.data.copy()
        df['period'] = pd.to_datetime(df['application_date']).dt.to_period(period)
        
        trends = df.groupby('period').agg({
            'candidate_id': 'count',
            'revenue_lkr': 'sum',
            'days_in_pipeline': 'mean'
        }).rename(columns={
            'candidate_id': 'candidates',
            'revenue_lkr': 'revenue',
            'days_in_pipeline': 'avg_days'
        })
        
        # Calculate placements per period
        placed = df[df['status'] == 'Placed']
        placements = placed.groupby('period').size()
        trends['placements'] = placements
        trends['placements'] = trends['placements'].fillna(0).astype(int)
        
        # Calculate growth rates
        trends['revenue_growth'] = trends['revenue'].pct_change() * 100
        trends['placement_growth'] = trends['placements'].pct_change() * 100
        
        trends = trends.reset_index()
        trends['period'] = trends['period'].astype(str)
        
        return trends
    
    def calculate_client_performance(self) -> pd.DataFrame:
        """
        Detailed client performance analysis
        
        Returns:
            DataFrame with client-level metrics and rankings
        """
        
        client_metrics = self.data.groupby('client').agg({
            'candidate_id': 'count',
            'revenue_lkr': 'sum',
            'days_in_pipeline': 'mean'
        }).rename(columns={
            'candidate_id': 'total_candidates',
            'revenue_lkr': 'total_revenue',
            'days_in_pipeline': 'avg_days_in_pipeline'
        })
        
        # Placement count
        placed = self.data[self.data['status'] == 'Placed']
        placements = placed.groupby('client').size()
        client_metrics['placements'] = placements
        client_metrics['placements'] = client_metrics['placements'].fillna(0).astype(int)
        
        # Conversion rate
        client_metrics['conversion_rate'] = (
            client_metrics['placements'] / client_metrics['total_candidates'] * 100
        )
        
        # Average revenue per placement
        client_metrics['avg_revenue_per_placement'] = client_metrics.apply(
            lambda row: row['total_revenue'] / row['placements'] if row['placements'] > 0 else 0,
            axis=1
        )
        
        # Performance ranking
        client_metrics['revenue_rank'] = client_metrics['total_revenue'].rank(ascending=False)
        client_metrics['placement_rank'] = client_metrics['placements'].rank(ascending=False)
        
        # Overall performance score (weighted)
        client_metrics['performance_score'] = (
            client_metrics['total_revenue'] * 0.5 +
            client_metrics['placements'] * 50000 * 0.3 +
            (100 - client_metrics['avg_days_in_pipeline']) * 1000 * 0.2
        )
        
        return client_metrics.sort_values('performance_score', ascending=False).reset_index()
    
    def calculate_department_performance(self) -> pd.DataFrame:
        """
        Department-level performance metrics
        
        Returns:
            DataFrame with department insights
        """
        
        dept_metrics = self.data.groupby('department').agg({
            'candidate_id': 'count',
            'revenue_lkr': 'sum',
            'days_in_pipeline': 'mean'
        }).rename(columns={
            'candidate_id': 'total_candidates',
            'revenue_lkr': 'total_revenue',
            'days_in_pipeline': 'avg_days_in_pipeline'
        })
        
        # Placement metrics
        placed = self.data[self.data['status'] == 'Placed']
        placements = placed.groupby('department').size()
        dept_metrics['placements'] = placements
        dept_metrics['placements'] = dept_metrics['placements'].fillna(0).astype(int)
        
        # Active pipeline
        active = self.data[self.data['status'].isin(['Interviewing', 'Screening'])]
        active_count = active.groupby('department').size()
        dept_metrics['active_pipeline'] = active_count
        dept_metrics['active_pipeline'] = dept_metrics['active_pipeline'].fillna(0).astype(int)
        
        # Conversion rate
        dept_metrics['conversion_rate'] = (
            dept_metrics['placements'] / dept_metrics['total_candidates'] * 100
        )
        
        return dept_metrics.sort_values('total_revenue', ascending=False).reset_index()
    
    def calculate_recruiter_performance(self) -> pd.DataFrame:
        """
        Individual recruiter performance analysis
        
        Returns:
            DataFrame with recruiter metrics
        """
        
        recruiter_metrics = self.data.groupby('assigned_recruiter').agg({
            'candidate_id': 'count',
            'revenue_lkr': 'sum',
            'days_in_pipeline': 'mean'
        }).rename(columns={
            'candidate_id': 'total_candidates',
            'revenue_lkr': 'total_revenue',
            'days_in_pipeline': 'avg_days_in_pipeline'
        })
        
        # Placements
        placed = self.data[self.data['status'] == 'Placed']
        placements = placed.groupby('assigned_recruiter').size()
        recruiter_metrics['placements'] = placements
        recruiter_metrics['placements'] = recruiter_metrics['placements'].fillna(0).astype(int)
        
        # Efficiency score (placements per candidate)
        recruiter_metrics['efficiency'] = (
            recruiter_metrics['placements'] / recruiter_metrics['total_candidates'] * 100
        )
        
        # Performance grade
        def assign_grade(row):
            if row['placements'] >= 15 and row['avg_days_in_pipeline'] <= 25:
                return 'A+'
            elif row['placements'] >= 10 and row['avg_days_in_pipeline'] <= 30:
                return 'A'
            elif row['placements'] >= 7:
                return 'B'
            elif row['placements'] >= 4:
                return 'C'
            else:
                return 'D'
        
        recruiter_metrics['grade'] = recruiter_metrics.apply(assign_grade, axis=1)
        
        return recruiter_metrics.sort_values('total_revenue', ascending=False).reset_index()
    
    def calculate_source_effectiveness(self) -> pd.DataFrame:
        """
        Analyze effectiveness of different sourcing channels
        
        Returns:
            DataFrame with source channel metrics
        """
        
        source_metrics = self.data.groupby('source_channel').agg({
            'candidate_id': 'count',
            'revenue_lkr': 'sum',
            'days_in_pipeline': 'mean'
        }).rename(columns={
            'candidate_id': 'total_candidates',
            'revenue_lkr': 'total_revenue',
            'days_in_pipeline': 'avg_days_in_pipeline'
        })
        
        placed = self.data[self.data['status'] == 'Placed']
        placements = placed.groupby('source_channel').size()
        source_metrics['placements'] = placements
        source_metrics['placements'] = source_metrics['placements'].fillna(0).astype(int)
        
        # Conversion rate
        source_metrics['conversion_rate'] = (
            source_metrics['placements'] / source_metrics['total_candidates'] * 100
        )
        
        # Cost efficiency (lower days + higher conversion = better)
        source_metrics['efficiency_score'] = (
            source_metrics['conversion_rate'] * 100 / source_metrics['avg_days_in_pipeline']
        )
        
        return source_metrics.sort_values('efficiency_score', ascending=False).reset_index()
    
    def calculate_pipeline_health(self) -> Dict[str, any]:
        """
        Overall pipeline health metrics
        
        Returns:
            Dictionary with health indicators
        """
        
        active = self.data[self.data['status'].isin(['Interviewing', 'Screening'])]
        
        health = {
            'active_candidates': len(active),
            'interviewing_count': len(self.data[self.data['status'] == 'Interviewing']),
            'screening_count': len(self.data[self.data['status'] == 'Screening']),
            'avg_age_of_pipeline': active['days_in_pipeline'].mean() if len(active) > 0 else 0,
            'oldest_candidate_days': active['days_in_pipeline'].max() if len(active) > 0 else 0,
        }
        
        # Projected placements (simple heuristic: 25% of interviewing)
        health['projected_placements_30d'] = int(health['interviewing_count'] * 0.25)
        
        # Pipeline velocity (candidates moving through per week)
        total_days = (self.data['application_date'].max() - self.data['application_date'].min()).days
        health['pipeline_velocity'] = len(self.data) / (total_days / 7) if total_days > 0 else 0
        
        # Health score (0-100)
        health_score = 0
        if health['active_candidates'] >= KPI_TARGETS['active_pipeline_min']:
            health_score += 40
        else:
            health_score += (health['active_candidates'] / KPI_TARGETS['active_pipeline_min']) * 40
            
        if health['avg_age_of_pipeline'] <= KPI_TARGETS['avg_time_to_hire_days']:
            health_score += 30
        else:
            health_score += max(0, 30 - (health['avg_age_of_pipeline'] - KPI_TARGETS['avg_time_to_hire_days']))
            
        if health['pipeline_velocity'] >= 10:
            health_score += 30
        else:
            health_score += (health['pipeline_velocity'] / 10) * 30
            
        health['overall_health_score'] = min(100, health_score)
        
        return health
    
    def get_revenue_breakdown(self) -> pd.DataFrame:
        """
        Detailed revenue breakdown and analysis
        
        Returns:
            DataFrame with revenue segments
        """
        
        placed = self.data[self.data['status'] == 'Placed'].copy()
        
        if len(placed) == 0:
            return pd.DataFrame()
        
        # Revenue segments
        placed['revenue_segment'] = pd.cut(
            placed['revenue_lkr'],
            bins=[0, 300000, 500000, 700000, float('inf')],
            labels=['Standard', 'Premium', 'Executive', 'Elite']
        )
        
        revenue_breakdown = placed.groupby('revenue_segment').agg({
            'candidate_id': 'count',
            'revenue_lkr': 'sum',
            'days_in_pipeline': 'mean'
        }).rename(columns={
            'candidate_id': 'placements',
            'revenue_lkr': 'total_revenue',
            'days_in_pipeline': 'avg_days'
        })
        
        revenue_breakdown['avg_fee'] = (
            revenue_breakdown['total_revenue'] / revenue_breakdown['placements']
        )
        
        revenue_breakdown['revenue_percentage'] = (
            revenue_breakdown['total_revenue'] / revenue_breakdown['total_revenue'].sum() * 100
        )
        
        return revenue_breakdown.reset_index()
    
    def generate_executive_summary(self) -> str:
        """
        Generate text-based executive summary
        
        Returns:
            Formatted executive summary string
        """
        
        kpis = self.calculate_executive_kpis()
        health = self.calculate_pipeline_health()
        
        summary = f"""
GAMAGE RECRUITERS - EXECUTIVE SUMMARY
{'='*60}

CORE PERFORMANCE METRICS:
- Total Placements: {kpis['total_placements']}
- Total Revenue: {self.currency_symbol} {kpis['total_revenue']:,.2f}
- Average Time-to-Hire: {kpis['avg_time_to_hire']:.1f} days
- Active Pipeline: {kpis['active_pipeline']} candidates

TARGET ACHIEVEMENT:
- Placement Target: {kpis['placement_target_achievement']*100:.1f}%
- Revenue Target: {kpis['revenue_target_achievement']*100:.1f}%
- Time Efficiency: {kpis['time_efficiency_score']*100:.1f}%

PIPELINE HEALTH:
- Health Score: {health['overall_health_score']:.1f}/100
- Interviewing: {health['interviewing_count']}
- Screening: {health['screening_count']}
- Projected Placements (30d): {health['projected_placements_30d']}

CONVERSION FUNNEL:
- Total Candidates: {kpis['total_candidates']}
- Placement Rate: {kpis['placement_rate']*100:.1f}%
- Rejected: {kpis['rejected_count']} ({kpis['rejected_count']/kpis['total_candidates']*100:.1f}%)

{'='*60}
        """
        
        return summary.strip()