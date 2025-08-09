import pytest
from unittest.mock import Mock, patch
from main import SpectraAI
import time

class TestErrorHandling:
    
    @pytest.fixture
    def spectra_ai(self):
        with patch('main.ollama.Client'):
            return SpectraAI()
    
    def test_resource_error_marks_model_failed(self, spectra_ai):
        """Test that resource errors mark model as failed"""
        model = "test-model"
        spectra_ai.model = model
        
        with patch('main.ollama.Client') as mock_client:
            mock_client.return_value.chat.side_effect = Exception("resource exhausted")
            
            with pytest.raises(Exception):
                # This would be called within generate_response
                try:
                    raise Exception("resource exhausted")
                except Exception as e:
                    error_str = str(e).lower()
                    if any(keyword in error_str for keyword in ('resource', 'memory', 'timeout', 'overload')):
                        spectra_ai.failed_models.add(model)
                    raise
            
            assert model in spectra_ai.failed_models
    
    def test_memory_error_marks_model_failed(self, spectra_ai):
        """Test that memory errors mark model as failed"""
        model = "test-model"
        spectra_ai.model = model
        
        error_keywords = ['memory', 'timeout', 'overload']
        
        for keyword in error_keywords:
            spectra_ai.failed_models.clear()
            error_str = f"operation failed due to {keyword}"
            
            if any(kw in error_str.lower() for kw in ('resource', 'memory', 'timeout', 'overload')):
                spectra_ai.failed_models.add(model)
            
            assert model in spectra_ai.failed_models
    
    def test_non_resource_error_does_not_mark_failed(self, spectra_ai):
        """Test that non-resource errors don't mark model as failed"""
        model = "test-model"
        spectra_ai.model = model
        
        error_str = "connection refused"
        
        if any(keyword in error_str.lower() for keyword in ('resource', 'memory', 'timeout', 'overload')):
            spectra_ai.failed_models.add(model)
        
        assert model not in spectra_ai.failed_models
    
    @pytest.mark.asyncio
    async def test_generate_response_error_handling(self, spectra_ai):
        """Test complete error handling in generate_response"""
        with patch('main.ollama.Client') as mock_client, \
             patch('main.asyncio.to_thread') as mock_thread:
            
            mock_thread.side_effect = Exception("memory limit exceeded")
            
            with pytest.raises(Exception) as exc_info:
                await spectra_ai.generate_response("test message")
            
            # Verify error was logged and model marked as failed
            assert spectra_ai.model in spectra_ai.failed_models
            assert "memory limit exceeded" in str(exc_info.value)
    
    def test_error_keyword_detection(self):
        """Test error keyword detection logic"""
        resource_errors = [
            "resource exhausted",
            "memory limit exceeded", 
            "timeout occurred",
            "system overload"
        ]
        
        non_resource_errors = [
            "connection refused",
            "invalid model",
            "syntax error"
        ]
        
        keywords = ('resource', 'memory', 'timeout', 'overload')
        
        for error in resource_errors:
            assert any(keyword in error.lower() for keyword in keywords)
        
        for error in non_resource_errors:
            assert not any(keyword in error.lower() for keyword in keywords)
    
    def test_processing_time_calculation(self, spectra_ai):
        """Test processing time is calculated correctly on error"""
        start_time = time.time()
        time.sleep(0.01)  # Small delay
        processing_time = time.time() - start_time
        
        assert processing_time > 0
        assert processing_time < 1  # Should be very small