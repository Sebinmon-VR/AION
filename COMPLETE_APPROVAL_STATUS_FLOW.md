# Complete Approval Status Flow Documentation

## Overview
The AION system implements a comprehensive candidate approval workflow with specific status updates at each stage. Here's the complete flow from candidate application to final hiring.

## Complete Status Progression

### 1. INITIAL STAGES (HR/Manager Actions)
```
New → Shortlisted → Interview Scheduled → Interviewed → [Send for Approval]
```

#### Status Updates:
- **New**: Initial status when candidate CV is uploaded
- **Shortlisted**: HR/Manager selects candidate for interview
  - Triggers: Schedule Interview form appears
- **Interview Scheduled**: Date/time set for interview
  - Triggers: Interview Video Upload form appears
- **Interviewed**: Interview completed and video analyzed
  - Triggers: "Send for Approval" button appears for HR

### 2. APPROVAL WORKFLOW (Multi-Role Approval)
```
Interviewed → [HR sends for approval] → Pending Approval → [Role-based approvals] → Approved → Selected → Hired
```

#### Status Updates During Approval:

**A. Send for Approval (HR Action)**
- Candidate status: `"Interviewed"` → `"Pending Approval"`
- Creates notification for first approver based on position:
  - **Regular Positions**: Discipline Manager (first)
  - **Senior Positions**: Department Manager (first)

**B. First Level Approval**
- **Regular Positions**: Discipline Manager approves
  - Status remains: `"Pending Approval"`
  - Creates notification for Department Manager
- **Senior Positions**: Department Manager approves
  - Status remains: `"Pending Approval"`
  - Creates notification for Operation Manager

**C. Second Level Approval**
- **Regular Positions**: Department Manager approves
  - Status remains: `"Pending Approval"`
  - Creates notification for Operation Manager
- **Senior Positions**: Operation Manager approves
  - Status remains: `"Pending Approval"`
  - Creates notification for CEO

**D. Final Approval**
- **Regular Positions**: Operation Manager gives final approval
  - Status: `"Pending Approval"` → `"Approved"`
  - Notifies HR to proceed with offer letter
- **Senior Positions**: CEO gives final approval
  - Status: `"Pending Approval"` → `"Approved"`
  - Notifies HR to proceed with offer letter

### 3. POST-APPROVAL STAGES
```
Approved → Selected → [Offer Letter] → Hired → Onboarding
```

#### Status Updates:
- **Approved**: Final approval completed by last approver
  - HR can now update to "Selected"
- **Selected**: HR updates after final approval
  - Operation Manager can issue offer letter
- **Hired**: After offer letter is issued and accepted
  - Onboarding process can begin

## Detailed Code Implementation

### 1. Initial Status Updates (update_candidate_status function)
```python
# HR/Manager can update status through dropdown
candidate['status'] = new_status  # Direct status update
# Available statuses: Selected, Shortlisted, Interview Scheduled, Interviewed, etc.
```

### 2. Send for Approval (send_for_approval function)
```python
# HR sends candidate for approval after interview
candidate['status'] = 'Pending Approval'
candidate['sent_for_approval_at'] = datetime.datetime.now().isoformat()
candidate['sent_for_approval_by'] = request.cookies.get('username', '')
candidate['approval_request_message'] = approval_message

# Create notification for first approver based on position
```

### 3. Role-Based Approvals (approve_candidate function)
```python
# Each approver in chain can approve/reject/hold
if action == 'approve':
    # Check if this is final approval
    if is_final_approval:
        candidate['status'] = 'Approved'
        candidate['final_approved_by'] = current_user_role
        candidate['final_approved_at'] = datetime.datetime.now().isoformat()
    else:
        # Create notification for next approver
        # Status remains 'Pending Approval'
```

### 4. Approval History Tracking
```python
# Each approval step is recorded
candidate['approval_history'].append({
    'step': len(candidate['approval_history']) + 1,
    'approved_by_role': current_user_role,
    'approved_by_user': request.cookies.get('username', ''),
    'approved_at': datetime.datetime.now().isoformat(),
    'comment': approval_comment,
    'is_final': is_final_approval
})
```

## Role-Based Approval Paths

### Regular Positions Flow:
1. **HR** → Send for Approval → Status: "Pending Approval"
2. **Discipline Manager** → Approve → Status: "Pending Approval" (notifies Dept Manager)
3. **Department Manager** → Approve → Status: "Pending Approval" (notifies Operation Manager)
4. **Operation Manager** → Final Approve → Status: "Approved" (notifies HR)
5. **HR** → Update to "Selected" → **Operation Manager** → Issue Offer Letter → Status: "Hired"

### Senior Positions Flow (Discipline/Project Manager roles):
1. **HR** → Send for Approval → Status: "Pending Approval"
2. **Department Manager** → Approve → Status: "Pending Approval" (notifies Operation Manager)
3. **Operation Manager** → Approve → Status: "Pending Approval" (notifies CEO)
4. **CEO** → Final Approve → Status: "Approved" (notifies HR)
5. **HR** → Update to "Selected" → **Operation Manager** → Issue Offer Letter → Status: "Hired"

## UI Elements and Triggers

### Status-Based Form Display:
- **Shortlisted**: Schedule Interview form appears
- **Interview Scheduled**: Video upload form appears  
- **Interviewed**: "Send for Approval" button (HR only)
- **Pending Approval**: Approve/Reject/Hold buttons (current approver only)
- **Approved**: HR can update to "Selected"
- **Selected**: Operation Manager can issue offer letter
- **Hired**: Onboarding forms appear

### Notifications System:
- Each approval step creates notifications
- HR gets updates at each stage
- Final approval notifies HR to proceed with offer letter
- All actions are logged with timestamps and comments

## Key Features:

1. **Audit Trail**: Complete approval history with timestamps and comments
2. **Role-Based Permissions**: Only current approver can act
3. **Automatic Routing**: System determines next approver based on position
4. **Status Consistency**: Clear status progression with no gaps
5. **Notification System**: All stakeholders informed of progress
6. **Final Approval Handling**: Clear distinction between intermediate and final approvals

## Status Validation Rules:

- Candidates must be "Interviewed" before sending for approval
- Only HR can send for approval initially
- Each role can only approve candidates assigned to them
- Final approval automatically changes status to "Approved"
- Operation Manager issues offer letters only for "Selected" candidates
- Complete audit trail maintained throughout process

This comprehensive flow ensures no candidate falls through cracks and maintains clear accountability at each stage.
