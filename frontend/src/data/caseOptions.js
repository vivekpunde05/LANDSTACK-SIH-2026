export const caseStatuses = [
  'Open', 'Under Review', 'Field Verification Requested',
  'More Information Required', 'Ready for Decision', 'Resolved', 'Closed',
]

export const reviewStages = [
  'Intake', 'Initial Review', 'Evidence Review', 'Field Verification',
  'Decision Review', 'Finalized',
]

export const priorityLevels = ['Routine', 'Review Recommended', 'High Priority Review', 'Urgent Review']

export const resolutionTypes = [
  'No Further Action Required', 'Record Review Recommended',
  'Field Verification Completed', 'Additional Documentation Required',
  'Referred for Further Administrative Review', 'Information Updated in Case Record',
  'Unable to Conclude from Available Evidence',
]

export const actionLabels = {
  start_review: 'Start Review',
  request_field_verification: 'Request Field Verification',
  request_more_information: 'Request More Information',
  mark_ready_for_decision: 'Mark Ready for Decision',
  resolve_case: 'Resolve Case',
  close_case: 'Close Case',
}
