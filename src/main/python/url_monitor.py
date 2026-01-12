"""
URL monitoring for recorder persistence across page navigations.
"""
import time
import logging
import threading
import os

class URLMonitor:
    """Monitor URL changes and re-inject recorder script when page navigates."""
    
    def __init__(self, web_dir):
        self.web_dir = web_dir
        self.monitor_thread = None
        self.monitor_running = False
        self.last_known_url = None
        self.browser_executor = None
        self.active_session_id = None
    
    def set_browser(self, browser_executor):
        """Set the browser executor to monitor."""
        self.browser_executor = browser_executor
    
    def set_active_session(self, session_id):
        """Set the active session ID."""
        self.active_session_id = session_id
    
    def reinject_recorder_script(self):
        """Re-inject recorder script into current page."""
        try:
            if not self.browser_executor or not self.browser_executor.driver:
                return False
                
            recorder_script_path = os.path.join(self.web_dir, 'recorder-inject.js')
            if not os.path.exists(recorder_script_path):
                logging.error(f"Recorder script not found: {recorder_script_path}")
                return False
                
            with open(recorder_script_path, 'r', encoding='utf-8') as f:
                recorder_script = f.read()
            
            # Check if recorder is already active
            is_active = self.browser_executor.driver.execute_script(
                "return typeof window.startRecorderCapture === 'function' && window.isRecording === true;"
            )
            
            if is_active:
                logging.info("[Recorder] Script already active, skipping re-injection")
                return True
            
            # Inject the script
            self.browser_executor.driver.execute_script(recorder_script)
            logging.info("[Recorder] Script re-injected")
            
            # Wait for initialization
            time.sleep(0.5)
            
            # Start capturing
            script_loaded = self.browser_executor.driver.execute_script(
                "return typeof window.startRecorderCapture === 'function';"
            )
            
            if script_loaded:
                self.browser_executor.driver.execute_script("window.startRecorderCapture();")
                logging.info("[Recorder] Capture restarted after navigation")
                return True
            else:
                logging.error("[Recorder] Failed to restart capture after navigation")
                return False
                
        except Exception as e:
            logging.error(f"[Recorder] Error re-injecting script: {str(e)}")
            return False
    
    def monitor_url_changes(self):
        """Monitor URL changes and re-inject recorder script when page navigates."""
        logging.info("[Recorder Monitor] URL monitoring thread started")
        
        while self.monitor_running:
            try:
                if self.browser_executor and self.browser_executor.driver and self.active_session_id:
                    current_url = self.browser_executor.driver.current_url
                    
                    # Check if URL changed
                    if self.last_known_url and current_url != self.last_known_url:
                        logging.info(f"[Recorder Monitor] URL changed: {self.last_known_url} -> {current_url}")
                        logging.info("[Recorder Monitor] Re-injecting recorder script...")
                        
                        # Wait for page to load
                        time.sleep(2)
                        
                        # Re-inject recorder script
                        self.reinject_recorder_script()
                    
                    self.last_known_url = current_url
                    
            except Exception as e:
                logging.error(f"[Recorder Monitor] Error in URL monitoring: {str(e)}")
            
            # Check every 1 second
            time.sleep(1)
        
        logging.info("[Recorder Monitor] URL monitoring thread stopped")
    
    def start(self):
        """Start the URL monitoring thread."""
        if self.monitor_thread and self.monitor_thread.is_alive():
            logging.info("[Recorder Monitor] Already running")
            return
        
        self.monitor_running = True
        self.monitor_thread = threading.Thread(target=self.monitor_url_changes, daemon=True)
        self.monitor_thread.start()
        logging.info("[Recorder Monitor] Started")
    
    def stop(self):
        """Stop the URL monitoring thread."""
        self.monitor_running = False
        self.last_known_url = None
        logging.info("[Recorder Monitor] Stopped")
