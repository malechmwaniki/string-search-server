import sys
import os
import time
import tempfile
import random
import string
from typing import List, Dict, Tuple, Callable
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from search import (
    search_method_simple,
    search_method_set,
    search_method_grep,
    search_method_mmap,
    search_method_binary
)


def generate_test_file(
    num_lines: int,
    output_path: str,
    sorted_file: bool = False
) -> List[str]:
    print(f"Generating {num_lines:,} lines...")
    
    lines = []
    for i in range(num_lines):
        length = random.randint(20, 50)
        line = ''.join(
            random.choices(string.ascii_letters + string.digits, k=length)
        )
        lines.append(line)
    
    if sorted_file:
        lines.sort()
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
    
    print(f"Generated file: {output_path}")
    return lines


def benchmark_search_method(
    method_func: Callable,
    method_name: str,
    filepath: str,
    test_queries: List[Tuple[str, bool]],
    num_runs: int = 5
) -> Dict:
   
    print(f"\nBenchmarking: {method_name}")
    
    times = []
    
    for query, should_exist in test_queries:
        query_times = []
        
        for _ in range(num_runs):
            try:
                found, elapsed = method_func(filepath, query)
                query_times.append(elapsed)
                
               
                if found != should_exist:
                    print(
                        f"  WARNING: Incorrect result for '{query}' "
                        f"(expected {should_exist}, got {found})"
                    )
            except Exception as e:
                print(f"  ERROR: {e}")
                query_times.append(float('inf'))
        
        query_times.sort()
        median_time = query_times[len(query_times) // 2]
        times.append(median_time)
    
    avg_time = sum(times) / len(times) if times else 0
    min_time = min(times) if times else 0
    max_time = max(times) if times else 0
    
    print(f"  Average: {avg_time * 1000:.3f}ms")
    print(f"  Min: {min_time * 1000:.3f}ms")
    print(f"  Max: {max_time * 1000:.3f}ms")
    
    return {
        'method': method_name,
        'avg_time_ms': avg_time * 1000,
        'min_time_ms': min_time * 1000,
        'max_time_ms': max_time * 1000,
        'times': [t * 1000 for t in times]
    }


def main():
    print("=" * 60)
    print("STRING SEARCH SERVER - PERFORMANCE BENCHMARK")
    print("=" * 60)
    
    # Test files
    file_sizes = [10000, 50000, 100000, 250000, 500000, 1000000]
    
    # Search methods 
    search_methods = [
        (search_method_simple, "Simple Loop"),
        (search_method_set, "Set Lookup"),
        (search_method_grep, "Grep Command"),
        (search_method_mmap, "Memory Mapped"),
        (search_method_binary, "Binary Search (sorted)")
    ]
    
  
    all_results = {}
    
    for file_size in file_sizes:
        print(f"\n{'=' * 60}")
        print(f"Testing with {file_size:,} lines")
        print(f"{'=' * 60}")
        
        # Generate test file
        test_file = tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            suffix='.txt'
        )
        test_file.close()
        
        lines = generate_test_file(file_size, test_file.name)
        
        #sorted file for binary search
        sorted_file = tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            suffix='_sorted.txt'
        )
        sorted_file.close()
        generate_test_file(file_size, sorted_file.name, sorted_file=True)
        
        # Prepare test queries
        test_queries = []

        #existing queries
        indices = [0, file_size // 4, file_size // 2,
                   3 * file_size // 4, file_size - 1]
        for idx in indices:
            if idx < len(lines):
                test_queries.append((lines[idx], True))
        
        # non-existing queries
        for _ in range(5):
            non_exist = "NONEXISTENT_" + ''.join(
                random.choices(string.ascii_letters, k=20)
            )
            test_queries.append((non_exist, False))
        
        # Benchmarking
        results = []
        
        for method_func, method_name in search_methods:
           
            if method_name == "Binary Search (sorted)":
                filepath = sorted_file.name
            else:
                filepath = test_file.name
            
            result = benchmark_search_method(
                method_func,
                method_name,
                filepath,
                test_queries,
                num_runs=3
            )
            result['file_size'] = file_size
            results.append(result)
        
        all_results[file_size] = results
        
        # Cleanup
        os.unlink(test_file.name)
        os.unlink(sorted_file.name)
    
 
    output_path = os.path.join(
        os.path.dirname(__file__),
        'results',
        'benchmark_results.json'
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"Results saved to: {output_path}")
    print(f"{'=' * 60}")
    
    # Print summary
    print("\nSUMMARY (Average times in ms)")
    print("-" * 60)
    print(f"{'File Size':<15} | {'Method':<25} | {'Time (ms)':<10}")
    print("-" * 60)
    
    for file_size in file_sizes:
        for result in all_results[file_size]:
            print(
                f"{file_size:<15,} | {result['method']:<25} | "
                f"{result['avg_time_ms']:<10.3f}"
            )
        print("-" * 60)
    
    return all_results


if __name__ == "__main__":
    results = main()
