
import argparse
import random
import string
import os
from typing import List


def generate_random_string(min_length: int = 20, max_length: int = 50) -> str:
    length = random.randint(min_length, max_length)
    return ''.join(
        random.choices(
            string.ascii_letters + string.digits,
            k=length
        )
    )


def generate_test_file(
    output_path: str,
    num_lines: int,
    sorted_output: bool = False,
    include_duplicates: bool = False,
    seed: int = None
) -> None:
    if seed is not None:
        random.seed(seed)
    
    print(f"Generating {num_lines:,} lines...")
    print(f"Output: {output_path}")
    
    lines = []
    generated = set()
    
    for i in range(num_lines):
        if i % 10000 == 0 and i > 0:
            print(f"  Progress: {i:,} / {num_lines:,}")
        
        while True:
            line = generate_random_string()
            if include_duplicates or line not in generated:
                lines.append(line)
                generated.add(line)
                break
    
    if sorted_output:
        print("Sorting lines...")
        lines.sort()
    
    print("Writing to file...")
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
    
    file_size = os.path.getsize(output_path)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"Done!")
    print(f"  Lines: {num_lines:,}")
    print(f"  File size: {file_size_mb:.2f} MB")
    print(f"  Sorted: {sorted_output}")
    print(f"  Duplicates: {include_duplicates}")


def generate_test_suite(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    
    test_sizes = [
        (100, "test_100.txt"),
        (1000, "test_1k.txt"),
        (10000, "test_10k.txt"),
        (50000, "test_50k.txt"),
        (100000, "test_100k.txt"),
        (250000, "test_250k.txt"),
        (500000, "test_500k.txt"),
        (1000000, "test_1m.txt"),
    ]
    
    print("=" * 60)
    print("GENERATING TEST SUITE")
    print("=" * 60)
    
    for num_lines, filename in test_sizes:
        print(f"\n{filename}:")
        output_path = os.path.join(output_dir, filename)
        generate_test_file(
            output_path,
            num_lines,
            sorted_output=False,
            include_duplicates=False,
            seed=42  
        )
    
    print(f"\ntest_250k_sorted.txt:")
    output_path = os.path.join(output_dir, "test_250k_sorted.txt")
    generate_test_file(
        output_path,
        250000,
        sorted_output=True,
        include_duplicates=False,
        seed=42
    )
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    print(f"Files generated in: {output_dir}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate test data files for String Search Server'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    single_parser = subparsers.add_parser(
        'single',
        help='Generate single test file'
    )
    single_parser.add_argument(
        'output',
        help='Output file path'
    )
    single_parser.add_argument(
        'lines',
        type=int,
        help='Number of lines'
    )
    single_parser.add_argument(
        '--sorted',
        action='store_true',
        help='Sort lines alphabetically'
    )
    single_parser.add_argument(
        '--duplicates',
        action='store_true',
        help='Allow duplicate lines'
    )
    single_parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility'
    )
    
    # Test suite generation
    suite_parser = subparsers.add_parser(
        'suite',
        help='Generate complete test suite'
    )
    suite_parser.add_argument(
        '--output-dir',
        default='tests/data',
        help='Output directory (default: tests/data)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'single':
        generate_test_file(
            args.output,
            args.lines,
            sorted_output=args.sorted,
            include_duplicates=args.duplicates,
            seed=args.seed
        )
    elif args.command == 'suite':
        generate_test_suite(args.output_dir)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
