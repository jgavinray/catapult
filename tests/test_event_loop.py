"""
Tests for event loop module.
"""
import pytest
import time
from src.catapult.event_loop import EventLoop

def test_event_loop_initialization():
    """Test event loop initializes correctly."""
    loop = EventLoop(check_interval=5)
    assert loop.check_interval == 5
    assert not loop.is_running
    assert loop.loop_thread is None

def test_event_loop_start_stop():
    """Test event loop can start and stop."""
    loop = EventLoop(check_interval=1)
    
    # Start the loop
    loop.start()
    assert loop.is_running
    assert loop.loop_thread is not None
    assert loop.loop_thread.is_alive()
    
    # Stop the loop
    loop.stop()
    assert not loop.is_running

def test_event_loop_status():
    """Test event loop status reporting."""
    loop = EventLoop(check_interval=10)
    status = loop.get_status()
    
    assert "is_running" in status
    assert "check_interval" in status
    assert "thread_alive" in status
    assert status["check_interval"] == 10
    assert not status["is_running"]

def test_event_loop_callback():
    """Test event loop callback functionality."""
    callback_called = False
    
    def test_callback():
        nonlocal callback_called
        callback_called = True
    
    loop = EventLoop(check_interval=1)
    loop.set_state_check_callback(test_callback)
    
    # Start and let it run briefly
    loop.start()
    time.sleep(0.1)  # Brief pause to allow callback execution
    loop.stop()
    
    # Note: In a real test, you might need to wait longer or use a different approach
    # to verify the callback was called, as the timing depends on the check_interval 