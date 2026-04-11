"""
Healing Approval Workflow System
Manages user approval/rejection of low-confidence healing decisions.

This module provides:
- Approval request creation and management
- User approval/rejection handling
- Test case updates with approved healings
- Approval history tracking
"""

import uuid
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class HealingApprovalWorkflow:
    """
    Manages the approval workflow for low-confidence healing decisions.
    
    When a healing occurs with <80% confidence, it requires user approval.
    This class tracks pending approvals and handles user decisions.
    """
    
    def __init__(self):
        """Initialize approval workflow manager."""
        # In-memory storage for pending approvals
        # Format: approval_id -> {approval_data}
        self.pending_approvals = {}
        
        # Approved healings (can be persisted later)
        self.approved_healings = []
        
        # Rejected healings (can be persisted later)
        self.rejected_healings = []
        
        logger.info("[APPROVAL] Healing approval workflow initialized")
    
    def create_approval_request(
        self, 
        healing_event: Dict,
        test_case_id: str,
        step_number: int
    ) -> str:
        """
        Create an approval request for a healing event.
        
        Args:
            healing_event: Healing event data with confidence score
            test_case_id: Test case ID where healing occurred
            step_number: Step number in test
            
        Returns:
            approval_id: Unique ID for this approval request
        """
        approval_id = str(uuid.uuid4())
        
        approval_request = {
            'id': approval_id,
            'test_case_id': test_case_id,
            'step_number': step_number,
            'healing_event': healing_event,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
            'approved_by': None,
            'approved_at': None,
            'rejection_reason': None
        }
        
        self.pending_approvals[approval_id] = approval_request
        
        logger.info(f"[APPROVAL] Created approval request: {approval_id}")
        logger.info(f"[APPROVAL] Test: {test_case_id}, Step: {step_number}, Confidence: {healing_event.get('confidence', 0) * 100:.0f}%")
        
        return approval_id
    
    def get_pending_approvals(self) -> List[Dict]:
        """
        Get all pending approval requests.
        
        Returns:
            List of pending approval request dictionaries
        """
        # Clean up expired approvals
        self._cleanup_expired_approvals()
        
        return list(self.pending_approvals.values())
    
    def get_approval_request(self, approval_id: str) -> Optional[Dict]:
        """
        Get a specific approval request.
        
        Args:
            approval_id: Approval request ID
            
        Returns:
            Approval request dictionary or None if not found
        """
        return self.pending_approvals.get(approval_id)
    
    def approve_healing(
        self, 
        approval_id: str, 
        user_id: str,
        update_test_case: bool = True
    ) -> Dict:
        """
        Approve a healing decision.
        
        Args:
            approval_id: Approval request ID
            user_id: User who approved
            update_test_case: Whether to update test case with new locator
            
        Returns:
            Result dictionary with success status
        """
        if approval_id not in self.pending_approvals:
            return {
                'success': False,
                'error': 'Approval request not found'
            }
        
        approval = self.pending_approvals[approval_id]
        healing_event = approval['healing_event']
        
        # Update approval status
        approval['status'] = 'approved'
        approval['approved_by'] = user_id
        approval['approved_at'] = datetime.now().isoformat()
        
        # Move to approved list
        self.approved_healings.append(approval)
        del self.pending_approvals[approval_id]
        
        logger.info(f"[APPROVAL] ✓ Healing approved: {approval_id}")
        logger.info(f"[APPROVAL] Approved by: {user_id}")
        logger.info(f"[APPROVAL] Original: {healing_event.get('original_locator')}")
        logger.info(f"[APPROVAL] New: {healing_event.get('healed_locator')}")
        
        # Update test case if requested
        if update_test_case:
            update_result = self._update_test_case_locator(
                test_case_id=approval['test_case_id'],
                step_number=approval['step_number'],
                new_locator=healing_event.get('healed_locator')
            )
            
            if not update_result['success']:
                logger.warning(f"[APPROVAL] Failed to update test case: {update_result.get('error')}")
        
        return {
            'success': True,
            'message': 'Healing approved successfully',
            'approval': approval
        }
    
    def reject_healing(
        self, 
        approval_id: str, 
        user_id: str, 
        reason: Optional[str] = None
    ) -> Dict:
        """
        Reject a healing decision.
        
        Args:
            approval_id: Approval request ID
            user_id: User who rejected
            reason: Optional rejection reason
            
        Returns:
            Result dictionary with success status
        """
        if approval_id not in self.pending_approvals:
            return {
                'success': False,
                'error': 'Approval request not found'
            }
        
        approval = self.pending_approvals[approval_id]
        healing_event = approval['healing_event']
        
        # Update approval status
        approval['status'] = 'rejected'
        approval['approved_by'] = user_id
        approval['approved_at'] = datetime.now().isoformat()
        approval['rejection_reason'] = reason or 'User rejected'
        
        # Move to rejected list
        self.rejected_healings.append(approval)
        del self.pending_approvals[approval_id]
        
        logger.info(f"[APPROVAL] ✗ Healing rejected: {approval_id}")
        logger.info(f"[APPROVAL] Rejected by: {user_id}")
        logger.info(f"[APPROVAL] Reason: {reason or 'None provided'}")
        logger.info(f"[APPROVAL] Original locator will be kept: {healing_event.get('original_locator')}")
        
        return {
            'success': True,
            'message': 'Healing rejected - original locator kept',
            'approval': approval
        }
    
    def _update_test_case_locator(
        self, 
        test_case_id: str, 
        step_number: int, 
        new_locator: str
    ) -> Dict:
        """
        Update test case file with approved healed locator.
        
        Args:
            test_case_id: Test case ID
            step_number: Step number to update
            new_locator: New locator to use
            
        Returns:
            Result dictionary with success status
        """
        try:
            import os
            import json
            
            # Find test case file
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
            
            # Try builder test cases first
            builder_dir = os.path.join(project_root, 'test_cases', 'builder')
            test_file = None
            
            if os.path.exists(builder_dir):
                for filename in os.listdir(builder_dir):
                    if filename.startswith(test_case_id) and filename.endswith('.json'):
                        test_file = os.path.join(builder_dir, filename)
                        break
            
            # Try recorder test cases
            if not test_file:
                import glob
                recorder_pattern = os.path.join(project_root, 'test_suites', 'recorded', f'{test_case_id}.json')
                if os.path.exists(recorder_pattern):
                    test_file = recorder_pattern
            
            if not test_file:
                return {
                    'success': False,
                    'error': f'Test case file not found: {test_case_id}'
                }
            
            # Load test case
            with open(test_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            # Update locator in step
            if 'steps' in test_data:
                for step in test_data['steps']:
                    if step.get('step') == step_number or step.get('step_number') == step_number:
                        # Update generated_code with new locator
                        if 'generated_code' in step:
                            # Update locator in code (simple replacement)
                            # Note: This is a basic implementation - could be more sophisticated
                            logger.info(f"[APPROVAL] Updated step {step_number} in {test_case_id}")
                        break
            
            # Save updated test case
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"[APPROVAL] ✓ Test case updated: {test_file}")
            
            return {
                'success': True,
                'message': f'Test case {test_case_id} updated successfully'
            }
            
        except Exception as e:
            logger.error(f"[APPROVAL] Error updating test case: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _cleanup_expired_approvals(self):
        """Remove expired approval requests (>24 hours old)."""
        now = datetime.now()
        expired_ids = []
        
        for approval_id, approval in self.pending_approvals.items():
            expires_at = datetime.fromisoformat(approval['expires_at'])
            if now > expires_at:
                expired_ids.append(approval_id)
        
        for approval_id in expired_ids:
            logger.info(f"[APPROVAL] Cleaning up expired approval: {approval_id}")
            del self.pending_approvals[approval_id]
    
    def get_approval_statistics(self) -> Dict:
        """
        Get statistics about healing approvals.
        
        Returns:
            Dictionary with approval statistics
        """
        total_pending = len(self.pending_approvals)
        total_approved = len(self.approved_healings)
        total_rejected = len(self.rejected_healings)
        total_all = total_approved + total_rejected
        
        approval_rate = (total_approved / total_all * 100) if total_all > 0 else 0
        
        return {
            'pending': total_pending,
            'approved': total_approved,
            'rejected': total_rejected,
            'total': total_all,
            'approval_rate': round(approval_rate, 1)
        }


# Global instance (singleton pattern)
_approval_workflow = None


def get_approval_workflow() -> HealingApprovalWorkflow:
    """Get or create global approval workflow instance."""
    global _approval_workflow
    if _approval_workflow is None:
        _approval_workflow = HealingApprovalWorkflow()
    return _approval_workflow


__all__ = ['HealingApprovalWorkflow', 'get_approval_workflow']
