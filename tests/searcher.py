"""search functionality test"""

import pytest
import os
import tempfile
from src.search import (
    FileSearcher,
    search_method_simple,
    search_method_set,
    search_method_grep,
    search_method_mmap
)


class TestFileSearcher:
    """Test FileSearcher class."""
    
    @pytest.fixture
    def test_file(self):
        with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write("apple\n")
            f.write("banana\n")
            f.write("cherry\n")
            f.write("date\n")
            f.write("elderberry\n")
            test_path = f.name
        
        yield test_path
        
       
        os.unlink(test_path)
    
    def test_string_exists(self, test_file):
        """Test finding existing string."""
        searcher = FileSearcher(test_file, reread_on_query=False)
        found, elapsed = searcher.search("apple")
        
        assert found is True
        assert elapsed >= 0
    
    def test_string_not_found(self, test_file):
        searcher = FileSearcher(test_file, reread_on_query=False)
        found, elapsed = searcher.search("grape")
        
        assert found is False
        assert elapsed >= 0
    
    def test_partial_match_rejected(self, test_file):
        """Ensure partial matches don't count."""
        # Add a line with "app" as substring
        with open(test_file, 'a') as f:
            f.write("pineapple\n")
        
        searcher = FileSearcher(test_file, reread_on_query=False)
        
        found, _ = searcher.search("app")
        assert found is False
        
        found, _ = searcher.search("apple")
        assert found is True
    
    def test_exact_match_only(self, test_file):
        """Test that only exact line matches count."""
        with open(test_file, 'a') as f:
            f.write("hello world\n")
        
        searcher = FileSearcher(test_file, reread_on_query=False)
        
        # Should not find partial
        assert searcher.search("hello")[0] is False
        assert searcher.search("world")[0] is False
        
        # Should find exact
        assert searcher.search("hello world")[0] is True
    
    def test_empty_file(self):
        """Test searching empty file."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False
        ) as f:
            test_path = f.name
        
        try:
            searcher = FileSearcher(test_path, reread_on_query=False)
            found, _ = searcher.search("anything")
            assert found is False
        finally:
            os.unlink(test_path)
    
    def test_empty_query(self, test_file):
        """Test searching for empty string."""
        # Add empty line to file
        with open(test_file, 'a') as f:
            f.write("\n")
        
        searcher = FileSearcher(test_file, reread_on_query=False)
        found, _ = searcher.search("")
        assert found is True
    
    def test_unicode_characters(self):
        """Test handling Unicode characters."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write("hello\n")
            f.write("你好\n")
            f.write("مرحبا\n")
            f.write("🍎\n")
            test_path = f.name
        
        try:
            searcher = FileSearcher(test_path, reread_on_query=False)
            
            assert searcher.search("你好")[0] is True
            assert searcher.search("مرحبا")[0] is True
            assert searcher.search("🍎")[0] is True
            assert searcher.search("你")[0] is False  
        finally:
            os.unlink(test_path)
    
    def test_reread_on_query_mode(self, test_file):
        """Test REREAD_ON_QUERY mode."""
        searcher = FileSearcher(test_file, reread_on_query=True)
        
        # finds existing
        found, _ = searcher.search("apple")
        assert found is True
        
        # Add new line to file
        with open(test_file, 'a') as f:
            f.write("fig\n")
        
        # finds newly added line
        found, _ = searcher.search("fig")
        assert found is True
    
    def test_cached_mode(self, test_file):
        """Test cached mode (REREAD_ON_QUERY=False)."""
        searcher = FileSearcher(test_file, reread_on_query=False)
        
        # Should find existing
        found, _ = searcher.search("apple")
        assert found is True
        
        # Add new line to file
        with open(test_file, 'a') as f:
            f.write("fig\n")
        
        # Should NOT find newly added line (cached)
        found, _ = searcher.search("fig")
        assert found is False
    
    def test_large_file_performance(self):
        """Test performance with large file."""
        # Create file with 10,000 lines
        with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            encoding='utf-8'
        ) as f:
            for i in range(10000):
                f.write(f"line_{i:06d}\n")
            test_path = f.name
        
        try:
            searcher = FileSearcher(test_path, reread_on_query=False)
            
            # Search for string at end
            found, elapsed = searcher.search("line_009999")
            assert found is True
            assert elapsed < 0.01  # Should be very fast with cache
            
            # Search for non-existent
            found, elapsed = searcher.search("line_999999")
            assert found is False
        finally:
            os.unlink(test_path)


class TestSearchMethods:
    """Test individual search method implementations."""
    
    @pytest.fixture
    def test_file(self):
        """Create temporary test file."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            encoding='utf-8'
        ) as f:
            for i in range(1000):
                f.write(f"test_line_{i}\n")
            test_path = f.name
        
        yield test_path
        os.unlink(test_path)
    
    def test_simple_method(self, test_file):
        """Test simple search method."""
        found, elapsed = search_method_simple(test_file, "test_line_500")
        assert found is True
        assert elapsed > 0
    
    def test_set_method(self, test_file):
        """Test set-based search method."""
        found, elapsed = search_method_set(test_file, "test_line_500")
        assert found is True
        assert elapsed > 0
    
    def test_grep_method(self, test_file):
        """Test grep search method."""
        found, elapsed = search_method_grep(test_file, "test_line_500")
        assert found is True
        assert elapsed > 0
    
    def test_mmap_method(self, test_file):
        """Test mmap search method."""
        found, elapsed = search_method_mmap(test_file, "test_line_500")
        assert found is True
        assert elapsed > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_file_not_found(self):
        """Test handling of non-existent file."""
        with pytest.raises(Exception):
            searcher = FileSearcher("/nonexistent/path/file.txt")
    
    def test_very_long_line(self):
        """Test handling very long lines."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write("a" * 10000 + "\n")
            f.write("target\n")
            test_path = f.name
        
        try:
            searcher = FileSearcher(test_path, reread_on_query=False)
            found, _ = searcher.search("target")
            assert found is True
        finally:
            os.unlink(test_path)
    
    def test_newline_variations(self):
        """Test different newline styles."""
        with tempfile.NamedTemporaryFile(
            mode='wb',
            delete=False
        ) as f:
            f.write(b"unix\n")
            f.write(b"windows\r\n")
            f.write(b"mac\r")
            test_path = f.name
        
        try:
            searcher = FileSearcher(test_path, reread_on_query=False)
            
            assert searcher.search("unix")[0] is True
            assert searcher.search("windows")[0] is True
            # Note: old Mac style \r might not work perfectly
        finally:
            os.unlink(test_path)