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
        self.last_window_handle = None
        self.last_window_count = 0
    
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
                
            recorder_script_path = os.path.join(self.web_dir, 'js', 'features', 'recorder-inject.js')
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
                    # Handle window/tab changes
                    try:
                        current_handles = self.browser_executor.driver.window_handles
                        current_handle = self.browser_executor.driver.current_window_handle
                        handle_count = len(current_handles)
                        
                        # Detect if a NEW tab/window was opened
                        if handle_count > self.last_window_count:
                            new_window = current_handles[-1]  # Get the latest window handle
                            logging.info(f"[Recorder Monitor] 🪟 NEW TAB DETECTED! Count: {self.last_window_count} → {handle_count}")
                            logging.info(f"[Recorder Monitor] 🔄 Auto-switching to new tab: {new_window}")
                            
                            # Switch to the new window/tab
                            self.browser_executor.driver.switch_to.window(new_window)
                            current_handle = new_window
                            self.last_window_handle = new_window
                            self.last_window_count = handle_count
                            
                            logging.info("[Recorder Monitor] ✅ Switched to new tab successfully")
                            
                            # Wait for new window to load
                            time.sleep(2)
                            
                            # Inject recorder into new window
                            logging.info("[Recorder Monitor] 💉 Injecting recorder into new tab...")
                            self.reinject_recorder_script()
                        
                        # Detect if tab/window was closed
                        elif handle_count < self.last_window_count:
                            logging.info(f"[Recorder Monitor] Tab/window closed. Count: {self.last_window_count} → {handle_count}")
                            self.last_window_count = handle_count
                            
                            # If we were on the closed tab, we're automatically switched to another
                            # Update our tracking
                            try:
                                current_handle = self.browser_executor.driver.current_window_handle
                                self.last_window_handle = current_handle
                                
                                # Check if recorder is active on current tab
                                is_recorder_active = self.browser_executor.driver.execute_script(
                                    "return typeof window.startRecorderCapture === 'function' && window.isRecording === true;"
                                )
                                if not is_recorder_active:
                                    logging.info("[Recorder Monitor] Recorder not active after tab close, re-injecting...")
                                    time.sleep(1)
                                    self.reinject_recorder_script()
                            except:
                                pass
                        
                        # Check if user manually switched tabs (same count, different handle)
                        elif self.last_window_handle and current_handle != self.last_window_handle:
                            logging.info(f"[Recorder Monitor] User switched tabs manually")
                            self.last_window_handle = current_handle
                            
                            # Check if recorder needs re-injection in this tab
                            try:
                                is_recorder_active = self.browser_executor.driver.execute_script(
                                    "return typeof window.startRecorderCapture === 'function' && window.isRecording === true;"
                                )
                                if not is_recorder_active:
                                    logging.info("[Recorder Monitor] Recorder not active in this tab, re-injecting...")
                                    time.sleep(1)
                                    self.reinject_recorder_script()
                            except:
                                pass
                        
                        # Update last known count
                        self.last_window_count = handle_count
                        
                    except Exception as e:
                        logging.error(f"[Recorder Monitor] Window handling error: {str(e)}")
                    
                    current_url = self.browser_executor.driver.current_url
                    
                    # Check if recorder is still active on the page
                    try:
                        is_recorder_active = self.browser_executor.driver.execute_script(
                            "return typeof window.startRecorderCapture === 'function' && window.isRecording === true;"
                        )
                    except:
                        is_recorder_active = False
                    
                    # Check if URL changed OR if recorder became inactive (page refresh)
                    url_changed = self.last_known_url and current_url != self.last_known_url
                    recorder_lost = self.last_known_url and not is_recorder_active
                    
                    if url_changed:
                        logging.info(f"[Recorder Monitor] URL changed: {self.last_known_url} -> {current_url}")
                        logging.info("[Recorder Monitor] Re-injecting recorder script...")
                        
                        # Wait for page to load
                        time.sleep(2)
                        
                        # Re-inject recorder script
                        self.reinject_recorder_script()
                    elif recorder_lost:
                        logging.info("[Recorder Monitor] Recorder lost (page refresh detected)")
                        logging.info("[Recorder Monitor] Re-injecting recorder script...")
                        
                        # Wait for page to load
                        time.sleep(1)
                        
                        # Re-inject recorder script
                        self.reinject_recorder_script()
                    
                    self.last_known_url = current_url
                    
            except Exception as e:
                logging.error(f"[Recorder Monitor] Error in URL monitoring: {str(e)}")
            
            # Check every 0.5 seconds for quick detection of new tabs/windows
            time.sleep(0.5)
        
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
        self.last_window_handle = None
        self.last_window_count = 0
        logging.info("[Recorder Monitor] Stopped")
