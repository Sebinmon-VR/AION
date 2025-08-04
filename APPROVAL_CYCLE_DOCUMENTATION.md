## AION Recruitment - Role-Based Approval Cycle

### Complete Approval Flow Overview

#### 1. **Initial Process** (Before Approval Cycle)
- **CV Upload** → **Shortlisted** → **Interview Scheduled** → **Interview Analyzed**

#### 2. **Send for Approval** (HR Action)
- **Trigger**: When candidate status is `Interview Analyzed` and user role is `HR`
- **Action**: HR fills approval message and clicks "Send for Approval"
- **Result**: 
  - Candidate status changes to `Pending Approval`
  - Notification sent to first approver based on position level
  - Approval cycle begins

#### 3. **Approval Cycle Paths**

##### **Regular Positions** (3-step approval)
```
HR → Discipline Manager → Department Manager (MOE/MOP) → Operation Manager → FINAL APPROVAL
```

##### **Senior Positions** (Discipline Manager/Project Manager - 3-step approval)
```
HR → Department Manager (MOE/MOP) → Operation Manager → CEO → FINAL APPROVAL
```

#### 4. **Approval Actions Available to Each Role**
- **✅ Approve**: Move to next step in approval chain
- **❌ Reject**: End approval cycle, candidate status becomes "Rejected"
- **⏸️ Hold**: Pause approval, candidate status becomes "On Hold"

#### 5. **Final Approval Process**
- **Regular Positions**: Operation Manager gives final approval
- **Senior Positions**: CEO gives final approval
- **After Final Approval**:
  - Candidate status changes to `Approved`
  - HR receives notification to generate offer letter
  - Approval history is recorded

#### 6. **Notification System**
- **Step Notifications**: Each approver receives notification when it's their turn
- **HR Updates**: HR receives updates at each step
- **Final Approval**: Special notification to HR when cycle completes

#### 7. **Role-Based Viewing**
- **HR/HR Manager**: Can see all candidates and approval flows
- **Discipline Manager**: Sees candidates requiring discipline manager approval
- **Department Manager**: Sees candidates requiring department manager approval  
- **Operation Manager**: Sees candidates requiring operation manager approval
- **CEO**: Sees senior position candidates requiring CEO approval

#### 8. **Key Features**
1. **Role-Based Permissions**: Users only see relevant candidates
2. **Real-Time Status**: Visual indication of current approval step
3. **Approval History**: Complete audit trail of all approval actions
4. **Notification System**: Automated notifications for pending approvals
5. **Final Approval Tracking**: Clear indication when approval cycle completes

#### 9. **Status Progression**
```
Interview Analyzed → Pending Approval → Approved/Rejected/On Hold
```

#### 10. **User Interface Features**
- **Dashboard Statistics**: Shows pending approvals count
- **Visual Approval Flow**: Color-coded steps with current user highlighting
- **Action Buttons**: Approve/Reject buttons only for relevant users
- **Approval History**: Timeline of all approval actions
- **Auto-refresh**: Real-time updates every 30 seconds

This system ensures proper role-based approval with complete audit trail and notifications.
