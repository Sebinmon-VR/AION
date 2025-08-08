"""
Updated Analytics Functions - Real Data Only
These functions replace the mock data versions in tools.py
"""

def get_onboarding_insights_real() -> str:
    """Analyzes onboarding process based on real candidate data"""
    try:
        candidates = load_json_data("candidates.json")
        
        hired_candidates = [c for c in candidates if c.get('status') == 'Hired']
        
        if not hired_candidates:
            return " **Onboarding Insights**: No hired candidates found for analysis"
        
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


def get_probation_insights_real() -> str:
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


def get_market_salary_comparison_real() -> str:
    """Compares company salary offerings with market rates using internet research"""
    try:
        from salary_research import salary_researcher
        
        candidates = load_json_data("candidates.json")
        jobs = load_json_data("jobs.json")
        
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
            return "💰 **Market Salary Comparison**: No salary data available for hired candidates"
        
        # Analyze each position with market research
        comparison_results = []
        
        for position, salaries in salary_by_position.items():
            if len(salaries) >= 1:  # At least one salary data point
                internal_avg = sum(salaries) / len(salaries)
                internal_min = min(salaries)
                internal_max = max(salaries)
                
                # Research market salary for this position
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
                    
                    comparison_results.append({
                        'position': position,
                        'internal_avg': internal_avg,
                        'market_avg': market_avg,
                        'competitiveness': competitiveness,
                        'status': status,
                        'count': len(salaries),
                        'market_trend': market_data.get('market_trend', 'stable')
                    })
        
        if not comparison_results:
            return " **Market Salary Comparison**: Unable to complete market research"
        
        # Generate comparison report
        position_breakdown = "\n".join([
            f"• {result['position']}: ${result['internal_avg']:,.0f} vs ${result['market_avg']:,.0f} market ({result['competitiveness']:.1f}%) {result['status']}"
            for result in comparison_results
        ])
        
        # Overall recommendations
        below_market = [r for r in comparison_results if r['competitiveness'] < 90]
        above_market = [r for r in comparison_results if r['competitiveness'] >= 110]
        
        recommendations = []
        if below_market:
            recommendations.append(f"Consider salary adjustments for: {', '.join([r['position'] for r in below_market])}")
        if above_market:
            recommendations.append(f"Excellent competitive positioning for: {', '.join([r['position'] for r in above_market])}")
        
        avg_competitiveness = sum([r['competitiveness'] for r in comparison_results]) / len(comparison_results)
        
        return f""" **Market Salary Comparison** (Internet Research + Real Data)

**Overall Competitiveness**: {avg_competitiveness:.1f}% of market rate

**Position Analysis**:
{position_breakdown}

**Market Trends**:
• Research conducted using current market data
• Salaries compared against industry standards
• Regional market factors considered

**Recommendations**:
{chr(10).join([f"• {rec}" for rec in recommendations]) if recommendations else "• Current salary offerings are well-positioned"}

**Action Items**:
• Review below-market positions for adjustment
• Monitor market trends quarterly
• Consider performance-based increases
• Benchmark against direct competitors

*Data sources: Market research + {sum([r['count'] for r in comparison_results])} internal salary data points*
"""
    except Exception as e:
        return f"⚠️ Error analyzing market salary comparison: {e}"


def get_salary_trend_insights_real() -> str:
    """Analyzes salary trends using real data with market comparison"""
    try:
        from salary_research import salary_researcher
        
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
            return " **Salary Trend Analysis**: Insufficient salary data for trend analysis"
        
        # Sort by date
        salary_data.sort(key=lambda x: x['date'])
        
        # Calculate trend
        if len(salary_data) >= 6:
            recent_avg = np.mean([s['salary'] for s in salary_data[-6:]])  # Last 6 hires
            older_avg = np.mean([s['salary'] for s in salary_data[:-6]])   # Previous hires
        else:
            # If less than 6 data points, split in half
            mid_point = len(salary_data) // 2
            recent_avg = np.mean([s['salary'] for s in salary_data[mid_point:]])
            older_avg = np.mean([s['salary'] for s in salary_data[:mid_point]])
        
        trend_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        trend_direction = "📈 INCREASING" if trend_pct > 0 else "📉 DECREASING"
        
        # Analyze by position
        position_trends = {}
        for position in set([s['position'] for s in salary_data]):
            pos_data = [s for s in salary_data if s['position'] == position]
            if len(pos_data) >= 2:
                pos_avg = np.mean([s['salary'] for s in pos_data])
                position_trends[position] = pos_avg
        
        # Research market trend for most common position
        most_common_position = max(set([s['position'] for s in salary_data]), 
                                 key=lambda x: len([s for s in salary_data if s['position'] == x]))
        
        market_research = salary_researcher.research_market_salary(most_common_position)
        market_insight = ""
        if market_research['status'] == 'success':
            market_trend = market_research['salary_data'].get('market_trend', 'stable')
            market_insight = f"\n**Market Trend for {most_common_position}**: {market_trend.upper()}"
        
        # Create trend chart data
        monthly_data = {}
        for s in salary_data:
            month_key = s['date'].strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = []
            monthly_data[month_key].append(s['salary'])
        
        # Average salary by month
        monthly_avg = {month: np.mean(salaries) for month, salaries in monthly_data.items()}
        
        # Create trend chart
        create_line_chart(
            monthly_avg,
            "salary_trends.png",
            "Salary Trend Analysis (Real Data)",
            "Month",
            "Average Salary"
        )
        
        position_breakdown = "\n".join([f"• {pos}: ${avg:,.0f} average" for pos, avg in position_trends.items()])
        
        return f"""💰 **Salary Trend Analysis** (Real Data)

**Overall Trend**: {trend_direction} by {abs(trend_pct):.1f}%
**Current Average**: ${recent_avg:,.0f}
**Previous Average**: ${older_avg:,.0f}
**Data Points**: {len(salary_data)} hired candidates{market_insight}

**Position Breakdown**:
{position_breakdown}

**Insights**:
• Salary progression {'aligns with growth strategy' if trend_pct > 0 else 'may need review'}
• {'Competitive increases' if trend_pct > 5 else 'Modest adjustments' if trend_pct > 0 else 'Declining trend requires attention'}
• Market research indicates informed salary decisions

**Recommendations**:
• {'Continue current strategy' if trend_pct > 0 else 'Review compensation packages'}
• Regular market benchmarking
• Document salary decision factors

*Analysis based on {len(salary_data)} real salary data points*
"""
    except Exception as e:
        return f"⚠️ Error analyzing salary trends: {e}"
