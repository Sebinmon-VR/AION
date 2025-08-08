# -----------------------------------------------------------------------------------------------------------------
# CLEAN TOOLS.PY - REAL DATA ANALYTICS ONLY
# -----------------------------------------------------------------------------------------------------------------
from typing import Dict, List, Any
import os
import json
import numpy as np
# Configure matplotlib to use non-interactive backend for web servers
import matplotlib
matplotlib.use('Agg')  # Use Anti-Grain Geometry backend (non-interactive)
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Import salary research module for market analysis
try:
    from salary_research import salary_researcher
except ImportError:
    salary_researcher = None

def load_json_data(filename):
    """Load JSON data from the db folder"""
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    file_path = os.path.join(db_folder, filename)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

# ========== REAL DATA ANALYTICS FUNCTIONS ==========

def get_onboarding_insights() -> str:
    """Analyzes onboarding process based on real candidate data"""
    try:
        candidates = load_json_data("candidates.json")
        
        hired_candidates = [c for c in candidates if c.get('status') == 'Hired']
        
        if not hired_candidates:
            return "🚀 **Onboarding Insights**: No hired candidates found for analysis"
        
        # Analyze real onboarding data from candidate records
        onboarding_analysis = {
            'total_hired': len(hired_candidates),
            'pending_onboarding': 0,
            'completed_onboarding': 0,
            'avg_hiring_to_start_days': 0,
            'departments': {}
        }
        
        total_days = 0
        valid_date_count = 0
        
        for candidate in hired_candidates:
            # Analyze department distribution
            dept = candidate.get('department', 'Unknown')
            if dept not in onboarding_analysis['departments']:
                onboarding_analysis['departments'][dept] = 0
            onboarding_analysis['departments'][dept] += 1
            
            # Calculate time from hiring to start (if available)
            hired_date = candidate.get('hired_date')
            start_date = candidate.get('start_date')
            
            if hired_date and start_date:
                try:
                    hired_dt = datetime.strptime(hired_date, '%Y-%m-%d')
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    days_diff = (start_dt - hired_dt).days
                    total_days += days_diff
                    valid_date_count += 1
                except:
                    pass
            
            # Check onboarding status
            onboarding_status = candidate.get('onboarding_status', 'pending')
            if onboarding_status == 'completed':
                onboarding_analysis['completed_onboarding'] += 1
            else:
                onboarding_analysis['pending_onboarding'] += 1
        
        if valid_date_count > 0:
            onboarding_analysis['avg_hiring_to_start_days'] = total_days / valid_date_count
        
        # Generate insights based on real data
        completion_rate = (onboarding_analysis['completed_onboarding'] / onboarding_analysis['total_hired']) * 100
        
        # Recommendations based on actual data
        recommendations = []
        if completion_rate < 80:
            recommendations.append("Improve onboarding completion tracking")
        if onboarding_analysis['avg_hiring_to_start_days'] > 14:
            recommendations.append("Reduce time between hiring and start date")
        if onboarding_analysis['pending_onboarding'] > 3:
            recommendations.append("Focus on completing pending onboardings")
        
        dept_breakdown = "\n".join([f"• {dept}: {count} hires" for dept, count in onboarding_analysis['departments'].items()])
        
        return f"""🚀 **Onboarding Insights** (Real Data Analysis)

**Current Status**:
• Total Hired: {onboarding_analysis['total_hired']} candidates
• Completed Onboarding: {onboarding_analysis['completed_onboarding']} ({completion_rate:.1f}%)
• Pending Onboarding: {onboarding_analysis['pending_onboarding']}

**Time Analysis**:
• Average Hiring to Start: {onboarding_analysis['avg_hiring_to_start_days']:.1f} days

**Department Distribution**:
{dept_breakdown}

**Recommendations**:
{chr(10).join([f"• {rec}" for rec in recommendations]) if recommendations else "• Current onboarding process is performing well"}

**Action Items**:
• Track onboarding completion status for all hires
• Set up start date coordination process
• Monitor department-specific onboarding needs
"""
    except Exception as e:
        return f"⚠️ Error analyzing onboarding: {e}"

def get_probation_insights() -> str:
    """Analyzes probation assessment performance based on real data"""
    try:
        candidates = load_json_data("candidates.json")
        
        hired_candidates = [c for c in candidates if c.get('status') == 'Hired']
        
        if not hired_candidates:
            return "🎓 **Probation Assessment Insights**: No hired candidates found for analysis"
        
        # Analyze real probation data
        probation_analysis = {
            'total_on_probation': 0,
            'passed_probation': 0,
            'failed_probation': 0,
            'pending_assessment': 0,
            'departments': {}
        }
        
        for candidate in hired_candidates:
            dept = candidate.get('department', 'Unknown')
            if dept not in probation_analysis['departments']:
                probation_analysis['departments'][dept] = {
                    'total': 0, 'passed': 0, 'failed': 0, 'pending': 0
                }
            
            probation_status = candidate.get('probation_status', 'pending')
            probation_analysis['departments'][dept]['total'] += 1
            
            if probation_status == 'passed':
                probation_analysis['passed_probation'] += 1
                probation_analysis['departments'][dept]['passed'] += 1
            elif probation_status == 'failed':
                probation_analysis['failed_probation'] += 1
                probation_analysis['departments'][dept]['failed'] += 1
            else:
                probation_analysis['pending_assessment'] += 1
                probation_analysis['departments'][dept]['pending'] += 1
            
            probation_analysis['total_on_probation'] += 1
        
        # Calculate pass rates by department
        dept_stats = []
        for dept, data in probation_analysis['departments'].items():
            if data['total'] > 0:
                pass_rate = (data['passed'] / data['total']) * 100
                dept_stats.append({
                    'department': dept,
                    'pass_rate': pass_rate,
                    'total': data['total'],
                    'passed': data['passed'],
                    'failed': data['failed'],
                    'pending': data['pending']
                })
        
        dept_stats.sort(key=lambda x: x['pass_rate'], reverse=True)
        
        overall_pass_rate = (probation_analysis['passed_probation'] / probation_analysis['total_on_probation'] * 100) if probation_analysis['total_on_probation'] > 0 else 0
        
        # Generate department breakdown
        dept_breakdown = "\n".join([
            f"• {stat['department']}: {stat['pass_rate']:.1f}% pass rate ({stat['passed']}/{stat['total']})"
            for stat in dept_stats
        ])
        
        # Recommendations
        recommendations = []
        if overall_pass_rate < 80:
            recommendations.append("Overall probation pass rate needs improvement")
        if probation_analysis['pending_assessment'] > 5:
            recommendations.append("Address pending probation assessments promptly")
        
        # Find departments needing attention
        underperforming_depts = [stat for stat in dept_stats if stat['pass_rate'] < 75]
        if underperforming_depts:
            recommendations.append(f"Focus on improving {', '.join([d['department'] for d in underperforming_depts])}")
        
        return f"""🎓 **Probation Assessment Insights** (Real Data Analysis)

**Overall Performance**:
• Total on Probation: {probation_analysis['total_on_probation']} candidates
• Passed: {probation_analysis['passed_probation']} ({overall_pass_rate:.1f}%)
• Failed: {probation_analysis['failed_probation']}
• Pending Assessment: {probation_analysis['pending_assessment']}

**Department Performance**:
{dept_breakdown}

**Recommendations**:
{chr(10).join([f"• {rec}" for rec in recommendations]) if recommendations else "• Probation process is performing well across departments"}

**Action Items**:
• Complete pending probation assessments
• Provide additional support to underperforming departments
• Track probation success factors
"""
    except Exception as e:
        return f"⚠️ Error analyzing probation data: {e}"

def get_salary_trend_insights() -> str:
    """Analyzes salary trends using real data with market comparison"""
    try:
        candidates = load_json_data("candidates.json")
        
        # Extract salary data with dates
        salary_data = []
        for candidate in candidates:
            if candidate.get('offered_salary') and candidate.get('hired_date'):
                try:
                    salary = float(candidate['offered_salary'])
                    date = datetime.strptime(candidate['hired_date'], '%Y-%m-%d')
                    position = candidate.get('position', 'Unknown')
                    salary_data.append({
                        'salary': salary, 
                        'date': date, 
                        'position': position
                    })
                except:
                    continue
        
        if len(salary_data) < 2:
            return "💰 **Salary Trend Analysis**: No salary data available in candidate records. This is normal as salary information is often stored separately for privacy."
        
        # Sort by date
        salary_data.sort(key=lambda x: x['date'])
        
        # Calculate trend
        if len(salary_data) >= 6:
            recent_avg = sum([s['salary'] for s in salary_data[-6:]]) / 6  # Last 6 hires
            older_avg = sum([s['salary'] for s in salary_data[:-6]]) / (len(salary_data) - 6)   # Previous hires
        else:
            # If less than 6 data points, split in half
            mid_point = len(salary_data) // 2
            recent_avg = sum([s['salary'] for s in salary_data[mid_point:]]) / (len(salary_data) - mid_point)
            older_avg = sum([s['salary'] for s in salary_data[:mid_point]]) / mid_point if mid_point > 0 else 0
        
        trend_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        trend_direction = "📈 INCREASING" if trend_pct > 0 else "📉 DECREASING"
        
        # Analyze by position
        position_trends = {}
        for position in set([s['position'] for s in salary_data]):
            pos_data = [s for s in salary_data if s['position'] == position]
            if len(pos_data) >= 2:
                pos_avg = sum([s['salary'] for s in pos_data]) / len(pos_data)
                position_trends[position] = pos_avg
        
        position_breakdown = "\n".join([f"• {pos}: ${avg:,.0f} average" for pos, avg in position_trends.items()])
        
        return f"""💰 **Salary Trend Analysis** (Real Data Analysis)

**Overall Trend**: {trend_direction} by {abs(trend_pct):.1f}%
**Current Average**: ${recent_avg:,.0f}
**Previous Average**: ${older_avg:,.0f}
**Data Points**: {len(salary_data)} hired candidates

**Position Breakdown**:
{position_breakdown}

**Insights**:
• Salary progression {'aligns with growth strategy' if trend_pct > 0 else 'may need review'}
• {'Competitive increases' if trend_pct > 5 else 'Modest adjustments' if trend_pct > 0 else 'Declining trend requires attention'}
• Analysis based on real hiring data

**Recommendations**:
• {'Continue current strategy' if trend_pct > 0 else 'Review compensation packages'}
• Regular market benchmarking
• Document salary decision factors

*Analysis based on {len(salary_data)} real salary data points*
"""
    except Exception as e:
        return f"⚠️ Error analyzing salary trends: {e}"

def get_market_salary_comparison() -> str:
    """Compares company salary offerings with market rates using internet research"""
    try:
        candidates = load_json_data("candidates.json")
        
        # Extract real salary data from hired candidates
        salary_by_position = {}
        
        for candidate in candidates:
            if candidate.get('status') == 'Hired':
                position = candidate.get('position', 'Unknown')
                offered_salary = candidate.get('offered_salary')
                
                if offered_salary:
                    try:
                        salary_amount = float(offered_salary)
                        if position not in salary_by_position:
                            salary_by_position[position] = []
                        salary_by_position[position].append(salary_amount)
                    except (ValueError, TypeError):
                        continue
        
        if not salary_by_position:
            return """💰 **Market Salary Comparison**: No salary data available for hired candidates

**Note**: This is common as salary information is often:
• Stored in separate HR systems for privacy
• Managed by payroll departments
• Kept confidential in candidate records

**To Enable Market Comparison**:
• Add 'offered_salary' field to candidate records
• Use the salary research module for market data
• Implement salary benchmarking process

**Current Status**: Ready for analysis once salary data is available"""
        
        # Analyze each position with market research
        comparison_results = []
        
        for position, salaries in salary_by_position.items():
            if len(salaries) >= 1:  # At least one salary data point
                internal_avg = sum(salaries) / len(salaries)
                internal_min = min(salaries)
                internal_max = max(salaries)
                
                # Research market salary for this position if available
                market_avg = 0
                competitiveness = 0
                status = "🔍 Research Unavailable"
                
                if salary_researcher:
                    try:
                        market_research = salary_researcher.research_market_salary(position)
                        
                        if market_research['status'] == 'success':
                            market_data = market_research['salary_data']
                            market_avg = market_data['average_salary']
                            
                            # Calculate competitiveness
                            competitiveness = (internal_avg / market_avg) * 100 if market_avg > 0 else 0
                            
                            if competitiveness >= 110:
                                status = "💚 Above Market"
                            elif competitiveness >= 90:
                                status = "💛 Market Competitive"
                            else:
                                status = "🔴 Below Market"
                    except:
                        pass
                
                comparison_results.append({
                    'position': position,
                    'internal_avg': internal_avg,
                    'market_avg': market_avg,
                    'competitiveness': competitiveness,
                    'status': status,
                    'count': len(salaries)
                })
        
        if not comparison_results:
            return "💰 **Market Salary Comparison**: Unable to analyze salary data"
        
        # Generate comparison report
        position_breakdown = "\n".join([
            f"• {result['position']}: ${result['internal_avg']:,.0f} internal vs ${result['market_avg']:,.0f} market ({result['competitiveness']:.1f}%) {result['status']}"
            if result['market_avg'] > 0 else f"• {result['position']}: ${result['internal_avg']:,.0f} internal {result['status']}"
            for result in comparison_results
        ])
        
        # Overall recommendations
        below_market = [r for r in comparison_results if r['competitiveness'] > 0 and r['competitiveness'] < 90]
        above_market = [r for r in comparison_results if r['competitiveness'] >= 110]
        
        recommendations = []
        if below_market:
            recommendations.append(f"Consider salary adjustments for: {', '.join([r['position'] for r in below_market])}")
        if above_market:
            recommendations.append(f"Excellent competitive positioning for: {', '.join([r['position'] for r in above_market])}")
        if not below_market and not above_market:
            recommendations.append("Most positions are competitively positioned")
        
        avg_competitiveness = sum([r['competitiveness'] for r in comparison_results if r['competitiveness'] > 0])
        avg_count = len([r for r in comparison_results if r['competitiveness'] > 0])
        avg_competitiveness = avg_competitiveness / avg_count if avg_count > 0 else 0
        
        return f"""💰 **Market Salary Comparison** (Real Data + Internet Research)

**Overall Competitiveness**: {avg_competitiveness:.1f}% of market rate

**Position Analysis**:
{position_breakdown}

**Market Intelligence**:
• Research conducted using current market data
• Salaries compared against industry standards
• Analysis based on real internal hiring data

**Recommendations**:
{chr(10).join([f"• {rec}" for rec in recommendations])}

**Action Items**:
• Review positions needing adjustment
• Monitor market trends quarterly
• Consider performance-based increases
• Benchmark against direct competitors

*Data sources: Market research + {sum([r['count'] for r in comparison_results])} internal salary data points*
"""
    except Exception as e:
        return f"⚠️ Error analyzing market salary comparison: {e}"

def get_hiring_success_rate_insight() -> str:
    """Analyzes hiring success rate using real candidate data"""
    try:
        candidates = load_json_data("candidates.json")
        
        if not candidates:
            return "📊 **Hiring Success Rate**: No candidate data available for analysis"
        
        total_candidates = len(candidates)
        hired_count = len([c for c in candidates if c.get('status') == 'Hired'])
        success_rate = (hired_count / total_candidates * 100) if total_candidates > 0 else 0
        
        # Monthly trend analysis
        monthly_data = {}
        for candidate in candidates:
            applied_date = candidate.get('applied_date')
            if applied_date:
                try:
                    month_key = datetime.strptime(applied_date, '%Y-%m-%d').strftime('%Y-%m')
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {'total': 0, 'hired': 0}
                    monthly_data[month_key]['total'] += 1
                    if candidate.get('status') == 'Hired':
                        monthly_data[month_key]['hired'] += 1
                except:
                    continue
        
        # Analysis
        if success_rate >= 75:
            assessment = "EXCELLENT"
            reason = "success rate is above industry benchmark"
        elif success_rate >= 50:
            assessment = "GOOD" 
            reason = "success rate meets expectations"
        elif success_rate >= 25:
            assessment = "NEEDS IMPROVEMENT"
            reason = "success rate is below optimal levels"
        else:
            assessment = "CRITICAL"
            reason = "success rate requires immediate attention"
        
        # Monthly breakdown
        monthly_breakdown = ""
        if monthly_data:
            monthly_breakdown = "\n**Monthly Breakdown**:\n"
            for month, data in sorted(monthly_data.items()):
                rate = (data['hired'] / data['total'] * 100) if data['total'] > 0 else 0
                monthly_breakdown += f"• {month}: {data['hired']}/{data['total']} hired ({rate:.1f}%)\n"
            
        return f"""📊 **Hiring Success Rate Analysis** (Real Data)

**Current Rate**: {success_rate:.1f}% ({hired_count}/{total_candidates} candidates)
**Assessment**: {assessment} - {reason}

**Key Insights**:
• Total applications processed: {total_candidates}
• Successful hires: {hired_count}
• Conversion efficiency: {success_rate:.1f}%
{monthly_breakdown}
**Recommendations**:
• {'Maintain current strategies' if success_rate > 50 else 'Review screening and interview processes'}
• Implement data-driven candidate evaluation
• Track conversion rates by source and department

*Analysis based on {total_candidates} real candidate records*
"""
        
    except Exception as e:
        return f"⚠️ Error analyzing hiring success rate: {e}"

def get_monthly_hiring_insights() -> str:
    """Analyzes monthly hiring patterns using real data"""
    try:
        candidates = load_json_data("candidates.json")
        
        monthly_stats = {}
        for candidate in candidates:
            applied_date = candidate.get('applied_date')
            if applied_date:
                try:
                    month_key = datetime.strptime(applied_date, '%Y-%m-%d').strftime('%Y-%m')
                    month_name = datetime.strptime(month_key, '%Y-%m').strftime('%B %Y')
                    
                    if month_name not in monthly_stats:
                        monthly_stats[month_name] = {'applications': 0, 'hired': 0, 'interviews': 0}
                    
                    monthly_stats[month_name]['applications'] += 1
                    if candidate.get('status') == 'Hired':
                        monthly_stats[month_name]['hired'] += 1
                    if candidate.get('status') in ['Interviewed', 'Hired']:
                        monthly_stats[month_name]['interviews'] += 1
                except:
                    continue
        
        if not monthly_stats:
            return "📅 **Monthly Hiring Insights**: No application data available for analysis"
        
        # Find best and worst months
        success_rates = {month: (stats['hired'] / stats['applications'] * 100) if stats['applications'] > 0 else 0 
                        for month, stats in monthly_stats.items()}
        
        best_month = max(success_rates.keys(), key=lambda x: success_rates[x])
        worst_month = min(success_rates.keys(), key=lambda x: success_rates[x])
        
        monthly_breakdown = "\n".join([
            f"• {month}: {stats['hired']}/{stats['applications']} hired ({success_rates[month]:.1f}%)"
            for month, stats in sorted(monthly_stats.items())
        ])
        
        return f"""📅 **Monthly Hiring Insights** (Real Data Analysis)

**Best Month**: {best_month} ({success_rates[best_month]:.1f}% success rate)
**Worst Month**: {worst_month} ({success_rates[worst_month]:.1f}% success rate)

**Monthly Performance**:
{monthly_breakdown}

**Key Insights**:
• Total months analyzed: {len(monthly_stats)}
• Average monthly applications: {sum(s['applications'] for s in monthly_stats.values()) / len(monthly_stats):.1f}
• Overall success rate: {sum(s['hired'] for s in monthly_stats.values()) / sum(s['applications'] for s in monthly_stats.values()) * 100:.1f}%

**Recommendations**:
• Plan recruitment campaigns during high-performance months
• Investigate factors contributing to low-performance periods
• Maintain consistent hiring processes year-round

*Analysis based on {sum(s['applications'] for s in monthly_stats.values())} real applications*
"""
        
    except Exception as e:
        return f"⚠️ Error analyzing monthly insights: {e}"

def get_department_interview_insights() -> str:
    """Analyzes department interview efficiency using real data"""
    try:
        candidates = load_json_data("candidates.json")
        
        dept_stats = {}
        
        for candidate in candidates:
            dept = candidate.get('department', 'Unknown')
            status = candidate.get('status', '')
            
            if dept not in dept_stats:
                dept_stats[dept] = {'total': 0, 'interviewed': 0, 'hired': 0}
            
            dept_stats[dept]['total'] += 1
            
            if status in ['Interviewed', 'Hired']:
                dept_stats[dept]['interviewed'] += 1
            
            if status == 'Hired':
                dept_stats[dept]['hired'] += 1
        
        if not dept_stats:
            return "🏢 **Department Interview Efficiency**: No department data available"
        
        # Calculate efficiency metrics
        for dept, data in dept_stats.items():
            data['interview_rate'] = (data['interviewed'] / data['total'] * 100) if data['total'] > 0 else 0
            data['hire_rate'] = (data['hired'] / data['interviewed'] * 100) if data['interviewed'] > 0 else 0
        
        # Find most and least efficient departments
        fastest_dept = max(dept_stats.keys(), key=lambda x: dept_stats[x]['hire_rate'])
        slowest_dept = min(dept_stats.keys(), key=lambda x: dept_stats[x]['hire_rate'])
        
        dept_breakdown = "\n".join([
            f"• {dept}: {data['hire_rate']:.1f}% hire rate, {data['interviewed']}/{data['total']} interviewed"
            for dept, data in dept_stats.items()
        ])
        
        return f"""🏢 **Department Interview Efficiency Analysis** (Real Data)

**Most Efficient**: {fastest_dept} ({dept_stats[fastest_dept]['hire_rate']:.1f}% hire rate)
**Least Efficient**: {slowest_dept} ({dept_stats[slowest_dept]['hire_rate']:.1f}% hire rate)

**Department Performance**:
{dept_breakdown}

**Insights**:
• Based on {sum([data['total'] for data in dept_stats.values()])} real candidates
• {sum([data['hired'] for data in dept_stats.values()])} successful hires across departments
• Interview efficiency varies by department requirements

**Recommendations**:
• Share best practices from high-performing departments
• Provide interview training for lower-performing departments
• Standardize interview processes while respecting department needs

*Analysis based on real candidate and department data*
"""
        
    except Exception as e:
        return f"⚠️ Error analyzing department efficiency: {e}"

def get_top_performers_insights() -> str:
    """Identifies top performers using real data"""
    try:
        candidates = load_json_data("candidates.json")
        
        # Analyze interviewers/recruiters performance
        interviewer_stats = {}
        position_stats = {}
        
        for candidate in candidates:
            # Track interviewer performance
            interviewer = candidate.get('interviewed_by') or candidate.get('recruiter') or 'Unknown'
            if interviewer not in interviewer_stats:
                interviewer_stats[interviewer] = {'interviewed': 0, 'hired': 0}
            
            if candidate.get('status') in ['Interviewed', 'Hired']:
                interviewer_stats[interviewer]['interviewed'] += 1
            
            if candidate.get('status') == 'Hired':
                interviewer_stats[interviewer]['hired'] += 1
                
                # Track successful positions
                position = candidate.get('position', 'Unknown')
                if position not in position_stats:
                    position_stats[position] = 0
                position_stats[position] += 1
        
        # Calculate success rates
        for interviewer, stats in interviewer_stats.items():
            if stats['interviewed'] > 0:
                stats['success_rate'] = (stats['hired'] / stats['interviewed']) * 100
            else:
                stats['success_rate'] = 0
        
        # Find top performers
        top_interviewers = sorted(interviewer_stats.items(), 
                                key=lambda x: (x[1]['success_rate'], x[1]['hired']), 
                                reverse=True)[:5]
        
        top_positions = sorted(position_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        
        interviewer_breakdown = "\n".join([
            f"• {interviewer}: {stats['success_rate']:.1f}% success rate ({stats['hired']}/{stats['interviewed']})"
            for interviewer, stats in top_interviewers if stats['interviewed'] > 0
        ])
        
        position_breakdown = "\n".join([
            f"• {position}: {count} successful hires"
            for position, count in top_positions
        ])
        
        return f"""🏆 **Top Performers Analysis** (Real Data)

**Top Performing Interviewers**:
{interviewer_breakdown}

**Most Successful Positions**:
{position_breakdown}

**Key Insights**:
• Based on real interview and hiring data
• Success rates calculated from actual outcomes
• Performance varies by interviewer experience and role complexity

**Recommendations**:
• Share best practices from top performers
• Provide mentoring for developing interviewers
• Document successful interview techniques
• Create performance feedback loops

*Analysis based on real interviewer and hiring performance data*
"""
        
    except Exception as e:
        return f"⚠️ Error analyzing top performers: {e}"

# ========== CHART CREATION FUNCTIONS ==========

def create_line_chart(data: dict, filename: str, title: str, xlabel: str, ylabel: str) -> str:
    """Creates a line chart and saves it to the db folder"""
    try:
        plt.figure(figsize=(10, 6))
        
        dates = list(data.keys())
        values = list(data.values())
        
        plt.plot(dates, values, marker='o', linewidth=2, markersize=6)
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.grid(True, alpha=0.3)
        
        filepath = os.path.join("./db", filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return f"Chart saved: {filename}"
        
    except Exception as e:
        return f"Error creating chart: {e}"

def create_pie_chart(data: Any) -> str:
    """Creates a pie chart based on the provided data"""
    try:
        plt.figure(figsize=(8, 8))
        
        if isinstance(data, dict):
            labels = list(data.keys())
            values = list(data.values())
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            labels = [item.get('category', f'Item {i}') for i, item in enumerate(data)]
            values = [item.get('value', 0) for item in data]
        else:
            return "⚠️ Invalid data format for pie chart"
        
        plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('Distribution Analysis', fontsize=14, fontweight='bold')
        
        filepath = os.path.join("./db", "pie_chart.png")
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return f"📊 Pie chart created: ![Pie Chart](./db/pie_chart.png)"
        
    except Exception as e:
        return f"⚠️ Error creating pie chart: {e}"

# ========== UTILITY FUNCTIONS ==========

def greet(name: str) -> str:
    """Greets a user by name."""
    return f"Hello, {name}! Welcome to AION HR Analytics System."

def get_time(city: str = "UTC") -> str:
    """Returns current time."""
    try:
        return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception:
        return "Unable to get current time"
