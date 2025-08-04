# Complete Approval Flow Testing Guide

## System Overview
The AION approval system now implements a comprehensive role-based approval workflow with proper status updates at each stage.

## Complete Status Flow

### 1. Initial Application Process
```
CV Upload → Status: "New"
    ↓
HR Shortlists → Status: "Shortlisted" 
    ↓ (Schedule Interview form appears)
HR Schedules Interview → Status: "Interview Scheduled"
    ↓ (Video upload form appears)
Interview Completed & Analyzed → Status: "Interviewed"
    ↓ (Send for Approval button appears for HR)
```

### 2. Approval Chain Process
```
HR Sends for Approval → Status: "Pending Approval"
    ↓ (Notification to first approver)

REGULAR POSITIONS FLOW:
Discipline Manager → Department Manager → Operation Manager (Final)

SENIOR POSITIONS FLOW:
Department Manager → Operation Manager → CEO (Final)

During approval chain: Status remains "Pending Approval"
After final approval: Status changes to "Approved"
```

### 3. Final Hiring Process
```
Final Approval Complete → Status: "Approved"
    ↓ (HR notification to proceed)
HR Updates to Selected → Status: "Selected"
    ↓ (Operation Manager can issue offer letter)
Operation Manager Issues Offer Letter → Status: "Hired"
```

## Role-Based Permissions

### HR/HR Manager
- Upload CVs and shortlist candidates
- Schedule interviews
- Send candidates for approval after interview
- Update approved candidates to "Selected"
- Send negotiation emails

### Discipline Manager
- Approve regular position candidates (first in chain)
- View candidates assigned to them

### Department Manager (MOE/MOP)
- Approve senior position candidates (first in chain)
- Approve regular position candidates (second in chain)
- Send negotiation emails

### Operation Manager
- Final approval for regular positions
- Second approval for senior positions
- Issue offer letters for "Selected" candidates

### CEO
- Final approval for senior positions only

## UI Enhancements

### Status Indicators
- Color-coded status badges
- Progress timeline showing application stages
- Current step highlighting
- Contextual messages for each status

### Role-Based Forms
- Schedule Interview (HR for Shortlisted)
- Video Upload (HR for Interview Scheduled)
- Send for Approval (HR for Interviewed)
- Approve/Reject/Hold (Approvers for Pending Approval)
- Mark as Selected (HR for Approved)
- Issue Offer Letter (Operation Manager for Selected)

### Approval History
- Complete audit trail
- Timestamps and comments
- Approver information
- Step-by-step progression

## Testing Scenarios

### Test 1: Regular Position Approval
1. Login as HR → Upload CV → Shortlist → Schedule Interview → Conduct Interview
2. Send for Approval (goes to Discipline Manager)
3. Login as Discipline Manager → Approve (goes to Department Manager)
4. Login as Department Manager → Approve (goes to Operation Manager)
5. Login as Operation Manager → Final Approve (status becomes "Approved")
6. Login as HR → Mark as Selected
7. Login as Operation Manager → Issue Offer Letter (status becomes "Hired")

### Test 2: Senior Position Approval
1. Login as HR → Upload CV for "Discipline Manager" position
2. Follow same steps until Send for Approval
3. Approval goes to Department Manager → Operation Manager → CEO
4. CEO gives final approval

### Test 3: Rejection/Hold Scenarios
1. Any approver can reject or hold candidates
2. Status updates accordingly
3. Proper notifications sent to HR

## Database Structure

### Candidate Fields Added/Updated
- `status`: Current candidate status
- `sent_for_approval_at`: Timestamp when sent for approval
- `sent_for_approval_by`: Username who sent for approval
- `approval_request_message`: Message from HR
- `approval_history`: Array of approval steps
- `final_approved_by`: Final approver role
- `final_approved_at`: Final approval timestamp
- `final_approval_comment`: Final approver's comment

### Notification Structure
- `candidate_id`: Link to candidate
- `for_role`: Target role for notification
- `from_role`: Source role
- `type`: approval_request, final_approval_complete, etc.
- `status`: Sent, Approved, Rejected, On Hold
- `step_number`: Current step in approval chain
- `total_steps`: Total steps in the chain

## Key Features Implemented

1. ✅ **Complete Status Progression**
2. ✅ **Role-Based Approval Chains**
3. ✅ **Proper Final Approval Handling**
4. ✅ **Comprehensive Audit Trail**
5. ✅ **Status-Based UI Elements**
6. ✅ **Notification System**
7. ✅ **Visual Progress Indicators**
8. ✅ **Approval History Tracking**
9. ✅ **Role-Based Permissions**
10. ✅ **Error Handling and Validation**

The system now provides a complete, professional-grade approval workflow that ensures no candidate falls through the cracks and maintains clear accountability at every stage.
