"""
Test Session Manager - Manages multi-prompt test creation sessions

Allows users to:
1. Start a new test creation session
2. Add multiple prompts to build a complete test flow
3. Preview generated code for entire sequence
4. Save as executable test case
5. Execute saved test cases

Integrates with smart_prompt_handler for natural language understanding.
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestSession:
    """Represents an active test creation session."""
    
    def __init__(self, session_id: str, name: str, description: str = ""):
        self.session_id = session_id
        self.name = name
        self.description = description
        self.created_at = datetime.now().isoformat()
        self.prompts = []  # List of prompt steps
        self.current_url = None
        self.test_case_id = None  # Linked test case ID (when saved)
        
    def add_prompt(self, prompt: str, url: Optional[str] = None, 
                   value: Optional[str] = None,  # NEW: Data value for input actions
                   parsed: Optional[Dict] = None, 
                   resolved_element: Optional[Dict] = None,
                   generated_code: Optional[str] = None) -> int:
        """
        Add a prompt step to the session.
        
        Smart URL handling:
        - Only stores URL if it's different from current_url (prevents unnecessary page refreshes)
        - None URL means "stay on current page"
        - First step with URL sets the current_url
        
        Args:
            prompt: Natural language action
            url: Optional URL to navigate to
            value: Optional data value (e.g., username, password)
            parsed: NLP parsed result
            resolved_element: Found element details
            generated_code: Generated code for this step
        
        Returns: step number (1-indexed)
        """
        step_number = len(self.prompts) + 1
        
        # Smart URL handling: Only include URL if it's NEW or CHANGED
        should_include_url = False
        url_to_store = None
        
        if url:
            # If this is the first step OR URL changed from current
            if not self.current_url or url != self.current_url:
                should_include_url = True
                url_to_store = url
                self.current_url = url  # Update current URL
                logger.info(f"[SESSION {self.session_id}] URL changed to: {url}")
            else:
                # URL is same as current - don't include it (stay on page)
                logger.info(f"[SESSION {self.session_id}] URL unchanged, staying on: {self.current_url}")
        
        step = {
            'step': step_number,
            'prompt': prompt,
            'url': url_to_store,  # Only set if URL is new/changed
            'value': value,  # NEW: Data value for input actions
            'timestamp': datetime.now().isoformat(),
            'parsed': parsed,  # NLP parsed result
            'resolved_element': resolved_element,  # Found element details
            'generated_code': generated_code  # Code snippet for this step
        }
        
        self.prompts.append(step)
        logger.info(f"[SESSION {self.session_id}] Added step {step_number}: {prompt}")
        return step_number
    
    def remove_prompt(self, step_number: int) -> bool:
        """Remove a prompt step and renumber subsequent steps."""
        if 0 < step_number <= len(self.prompts):
            removed = self.prompts.pop(step_number - 1)
            
            # Renumber remaining steps
            for i, step in enumerate(self.prompts, start=1):
                step['step'] = i
            
            logger.info(f"[SESSION {self.session_id}] Removed step {step_number}")
            return True
        return False
    
    def update_prompt(self, step_number: int, prompt: str, url: Optional[str] = None, value: Optional[str] = None) -> bool:
        """Update an existing prompt step."""
        if 0 < step_number <= len(self.prompts):
            self.prompts[step_number - 1]['prompt'] = prompt
            if url is not None:  # Allow empty string to clear URL
                self.prompts[step_number - 1]['url'] = url
            if value is not None:  # Allow empty string to clear value
                self.prompts[step_number - 1]['value'] = value
            
            logger.info(f"[SESSION {self.session_id}] Updated step {step_number}")
            return True
        return False
    
    def reorder_prompt(self, from_step: int, to_step: int) -> bool:
        """Move a prompt from one position to another."""
        if 0 < from_step <= len(self.prompts) and 0 < to_step <= len(self.prompts):
            step = self.prompts.pop(from_step - 1)
            self.prompts.insert(to_step - 1, step)
            
            # Renumber all steps
            for i, s in enumerate(self.prompts, start=1):
                s['step'] = i
            
            logger.info(f"[SESSION {self.session_id}] Moved step {from_step} to {to_step}")
            return True
        return False
    
    def get_all_prompts(self) -> List[Dict]:
        """Get all prompts in the session."""
        return self.prompts
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary."""
        return {
            'session_id': self.session_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'prompt_count': len(self.prompts),
            'prompts': self.prompts,
            'current_url': self.current_url,
            'test_case_id': self.test_case_id  # Include linked test case ID
        }


class TestSessionManager:
    """
    Manages test creation sessions.
    
    Features:
    - Create/delete sessions
    - Add/remove/update prompts in session
    - Preview full test code
    - Save session as test case
    - Load existing sessions
    """
    
    def __init__(self, sessions_dir: str = None):
        """
        Initialize session manager with storage directory.
        
        WORKFLOW:
        1. Recording sessions kept in memory (TEMPORARY)
        2. User can execute tests in sessions before saving (preview)
        3. User clicks "Save" → session saved to test_cases/{user}/recorder/
        4. Session deleted from memory after save (cleanup)
        
        Sessions are memory-only by default. Optional sessions_dir for persistence.
        """
        if sessions_dir is None:
            # Memory-only mode - no disk storage for temp sessions
            self.sessions_dir = None
        else:
            self.sessions_dir = sessions_dir
            os.makedirs(self.sessions_dir, exist_ok=True)
        
        # Active sessions in memory (session_id -> TestSession)
        self.active_sessions: Dict[str, TestSession] = {}
        
        logger.info(f"[SESSION MANAGER] Initialized with directory: {self.sessions_dir}")
    
    def create_session(self, name: str, description: str = "") -> TestSession:
        """
        Create a new test creation session.
        
        Args:
            name: Test name (e.g., "User Login Flow")
            description: Optional test description
            
        Returns:
            TestSession object
        """
        session_id = str(uuid.uuid4())
        session = TestSession(session_id, name, description)
        self.active_sessions[session_id] = session
        
        logger.info(f"[SESSION MANAGER] Created session: {session_id} - {name}")
        return session
    
    def get_session(self, session_id: str) -> Optional[TestSession]:
        """Get an active session by ID."""
        return self.active_sessions.get(session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete an active session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"[SESSION MANAGER] Deleted session: {session_id}")
            return True
        return False
    
    def list_active_sessions(self) -> List[Dict]:
        """List all active sessions."""
        return [
            session.to_dict()  # Return full session data including test_case_id
            for sid, session in self.active_sessions.items()
        ]
    
    def save_session(self, session_id: str, filename: str = None) -> str:
        """
        Save session to file (for recovery or sharing).
        
        Args:
            session_id: Session to save
            filename: Optional custom filename
            
        Returns:
            Path to saved file
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if filename is None:
            # Generate filename from session name
            safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' 
                               for c in session.name)
            filename = f"session_{safe_name}_{session_id[:8]}.json"
        
        filepath = os.path.join(self.sessions_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
        
        logger.info(f"[SESSION MANAGER] Saved session to: {filepath}")
        return filepath
    
    def load_session(self, filepath: str) -> TestSession:
        """
        Load session from file.
        
        Args:
            filepath: Path to session file
            
        Returns:
            TestSession object (also adds to active sessions)
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create new session with loaded data
        session = TestSession(
            session_id=data['session_id'],
            name=data['name'],
            description=data.get('description', '')
        )
        session.created_at = data['created_at']
        session.prompts = data['prompts']
        session.current_url = data.get('current_url')
        
        # Add to active sessions
        self.active_sessions[session.session_id] = session
        
        logger.info(f"[SESSION MANAGER] Loaded session: {session.session_id} - {session.name}")
        return session
    
    def preview_code(self, session_id: str, language: str = 'python') -> Optional[str]:
        """
        Generate preview of complete test code.
        
        Args:
            session_id: Session to preview
            language: Target language (python, java, javascript, cypress)
            
        Returns:
            Complete test code as string
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        # Log the current step order for debugging
        logger.info(f"[PREVIEW] Session {session_id} step order: {[f'{p['step']}: {p['prompt'][:30]}...' for p in session.prompts]}")
        
        # Use TestCaseBuilder to generate proper multi-language code
        try:
            from .test_case_builder import get_test_case_builder
            
            builder = get_test_case_builder()
            
            # Build test case from session (without saving)
            # OPTIMIZATION: Only generate the requested language!
            session_dict = session.to_dict()
            test_case_name = session_dict.get('name', 'Untitled Test')
            test_case = builder.build_from_session(
                session_dict,
                test_case_id=f"Preview: {test_case_name}",
                tags=['preview'],
                priority='medium',
                languages=[language]  # Only generate the requested language
            )
            
            # Return code for requested language
            return test_case.generated_code.get(language, '')
            
        except Exception as e:
            logger.error(f"[SESSION MANAGER] Error generating preview for {language}: {e}")
            # Fallback to simple Python preview
            return self._generate_simple_python_preview(session)
    
    def _generate_simple_python_preview(self, session: 'TestSession') -> str:
        """Generate simple Python code preview (fallback)."""
        code_lines = []
        code_lines.append("# Auto-generated test case")
        code_lines.append(f"# Test: {session.name}")
        code_lines.append(f"# Generated: {datetime.now().isoformat()}")
        code_lines.append("")
        code_lines.append("from selenium import webdriver")
        code_lines.append("from selenium.webdriver.common.by import By")
        code_lines.append("import time")
        code_lines.append("")
        code_lines.append(f"def test_{session.name.lower().replace(' ', '_')}():")
        code_lines.append("    driver = webdriver.Chrome()")
        code_lines.append("    try:")
        
        for prompt_step in session.prompts:
            code_lines.append(f"        # Step {prompt_step['step']}: {prompt_step['prompt']}")
            if prompt_step.get('generated_code'):
                # Indent the generated code
                for line in prompt_step['generated_code'].split('\n'):
                    if line.strip() and not line.startswith('#'):
                        code_lines.append(f"        {line}")
            code_lines.append("")
        
        code_lines.append("    finally:")
        code_lines.append("        driver.quit()")
        
        return '\n'.join(code_lines)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about active sessions."""
        total_prompts = sum(len(s.prompts) for s in self.active_sessions.values())
        
        return {
            'active_sessions': len(self.active_sessions),
            'total_prompts': total_prompts,
            'average_prompts_per_session': total_prompts / len(self.active_sessions) if self.active_sessions else 0,
            'sessions': self.list_active_sessions()
        }


# Global session manager instance
_session_manager = None

def get_session_manager() -> TestSessionManager:
    """Get or create global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = TestSessionManager()
    return _session_manager


# Example usage
if __name__ == "__main__":
    # Test the session manager
    manager = TestSessionManager()
    
    # Create a session
    session = manager.create_session("User Login Test", "Test login functionality")
    
    # Add prompts
    session.add_prompt("Navigate to login page", url="https://example.com/login")
    session.add_prompt("Enter username", parsed={'action': 'type', 'element': 'username'})
    session.add_prompt("Enter password", parsed={'action': 'type', 'element': 'password'})
    session.add_prompt("Click login button", parsed={'action': 'click', 'element': 'loginButton'})
    session.add_prompt("Verify welcome message", parsed={'action': 'verify', 'element': 'welcomeMsg'})
    
    # Preview code
    print("\n" + "="*80)
    print("PREVIEW CODE:")
    print("="*80)
    print(manager.preview_code(session.session_id))
    
    # Save session
    filepath = manager.save_session(session.session_id)
    print(f"\nSession saved to: {filepath}")
    
    # Get statistics
    stats = manager.get_statistics()
    print(f"\nStatistics: {json.dumps(stats, indent=2)}")
