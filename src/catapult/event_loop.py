import asyncio
import time
import threading
from typing import Optional, Callable
import logging

class EventLoop:
    def __init__(self, check_interval: int = 15):
        self.check_interval = check_interval
        self.is_running = False
        self.loop_thread: Optional[threading.Thread] = None
        self.state_check_callback: Optional[Callable] = None
        self.logger = logging.getLogger(__name__)
        
    def set_state_check_callback(self, callback: Callable):
        """Set the callback function to be called during state checks"""
        self.state_check_callback = callback
        
    def start(self):
        """Start the event loop in a separate thread"""
        if self.is_running:
            self.logger.warning("Event loop is already running")
            return
            
        self.is_running = True
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.loop_thread.start()
        self.logger.info(f"Event loop started with {self.check_interval} second interval")
        
    def stop(self):
        """Stop the event loop"""
        self.is_running = False
        if self.loop_thread:
            self.loop_thread.join(timeout=5)
        self.logger.info("Event loop stopped")
        
    def _run_loop(self):
        """Main loop that runs every check_interval seconds"""
        while self.is_running:
            try:
                self._check_state()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Error in event loop: {e}")
                time.sleep(self.check_interval)
                
    def _check_state(self):
        """Perform state check - can be overridden or use callback"""
        if self.state_check_callback:
            try:
                self.state_check_callback()
            except Exception as e:
                self.logger.error(f"Error in state check callback: {e}")
        else:
            # Default state check - can be overridden
            self.logger.debug("Performing default state check")
            
    def get_status(self) -> dict:
        """Get current status of the event loop"""
        return {
            "is_running": self.is_running,
            "check_interval": self.check_interval,
            "thread_alive": self.loop_thread.is_alive() if self.loop_thread else False
        } 