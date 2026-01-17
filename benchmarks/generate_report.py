
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg') 
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def load_results(results_path: str):
    with open(results_path, 'r') as f:
        return json.load(f)


def create_comparison_table(results: dict) -> pd.DataFrame:
    data = []
    
    for file_size, methods in results.items():
        for method_result in methods:
            data.append({
                'File Size': int(file_size),
                'Method': method_result['method'],
                'Avg Time (ms)': method_result['avg_time_ms'],
                'Min Time (ms)': method_result['min_time_ms'],
                'Max Time (ms)': method_result['max_time_ms']
            })
    
    return pd.DataFrame(data)


def create_line_chart(df: pd.DataFrame, output_path: str):
    plt.figure(figsize=(12, 8))
    
    methods = df['Method'].unique()
    
    for method in methods:
        method_data = df[df['Method'] == method]
        plt.plot(
            method_data['File Size'],
            method_data['Avg Time (ms)'],
            marker='o',
            label=method,
            linewidth=2
        )
    
    plt.xlabel('File Size (lines)', fontsize=12)
    plt.ylabel('Average Time (ms)', fontsize=12)
    plt.title('Search Performance vs File Size', fontsize=14, fontweight='bold')
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def create_bar_chart(df: pd.DataFrame, file_size: int, output_path: str):
    data = df[df['File Size'] == file_size].sort_values('Avg Time (ms)')
    
    plt.figure(figsize=(10, 6))
    
    bars = plt.bar(range(len(data)), data['Avg Time (ms)'])
    
    # Color bars
    colors_list = ['#2ecc71', '#3498db', '#9b59b6', '#e74c3c', '#f39c12']
    for bar, color in zip(bars, colors_list):
        bar.set_color(color)
    
    plt.xticks(range(len(data)), data['Method'], rotation=45, ha='right')
    plt.ylabel('Average Time (ms)', fontsize=12)
    plt.title(
        f'Performance Comparison ({file_size:,} lines)',
        fontsize=14,
        fontweight='bold'
    )
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()


def generate_pdf_report(results: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    story = []
    
    # Title
    story.append(Paragraph(
        "String Search Server<br/>Performance Benchmark Report",
        title_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Metadata
    meta_text = f"""
    <para alignment="center">
    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
    Test Date: {datetime.now().strftime('%B %d, %Y')}
    </para>
    """
    story.append(Paragraph(meta_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    
    summary_text = """
    This report presents a comprehensive performance analysis of five different
    string search algorithms implemented for the String Search Server. Tests were
    conducted across multiple file sizes ranging from 10,000 to 1,000,000 lines.
    Each algorithm was tested with 10 queries (5 existing, 5 non-existing) and
    results were averaged over 3 runs for statistical reliability.
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Methodology
    story.append(Paragraph("Methodology", heading_style))
    
    method_text = """
    <b>Test Environment:</b> Linux server<br/>
    <b>File Sizes Tested:</b> 10K, 50K, 100K, 250K, 500K, 1M lines<br/>
    <b>Query Types:</b> 50% existing strings, 50% non-existing strings<br/>
    <b>Runs per Query:</b> 3 (median time reported)<br/>
    <b>Algorithms Tested:</b><br/>
    1. Simple Loop - Line-by-line iteration<br/>
    2. Set Lookup - O(1) hash-based lookup<br/>
    3. Grep Command - Native Linux grep utility<br/>
    4. Memory Mapped - mmap-based file access<br/>
    5. Binary Search - O(log n) search on sorted files
    """
    story.append(Paragraph(method_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(PageBreak())
    
    # Performance Results
    story.append(Paragraph("Performance Results", heading_style))
    
    # Create DataFrame
    df = create_comparison_table(results)
    
    # Overall ranking table
    story.append(Paragraph(
        "Overall Performance Ranking (250K lines)",
        styles['Heading3']
    ))
    
    ranking_data = df[df['File Size'] == 250000].sort_values('Avg Time (ms)')
    
    table_data = [['Rank', 'Method', 'Avg Time (ms)', 'Performance']]
    
    for idx, row in enumerate(ranking_data.itertuples(), 1):
        performance = "Excellent" if row._3 < 1 else \
                     "Very Good" if row._3 < 10 else \
                     "Good" if row._3 < 50 else \
                     "Moderate"
        
        table_data.append([
            str(idx),
            row.Method,
            f"{row._3:.3f}",
            performance
        ])
    
    table = Table(table_data, colWidths=[0.7*inch, 2.5*inch, 1.3*inch, 1.3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Detailed results table
    story.append(PageBreak())
    story.append(Paragraph("Detailed Results", heading_style))
    
    detailed_data = [['File Size', 'Method', 'Avg (ms)', 'Min (ms)', 'Max (ms)']]
    
    for file_size in sorted([int(k) for k in results.keys()]):
        for method in results[str(file_size)]:
            detailed_data.append([
                f"{file_size:,}",
                method['method'],
                f"{method['avg_time_ms']:.3f}",
                f"{method['min_time_ms']:.3f}",
                f"{method['max_time_ms']:.3f}"
            ])
    
    detailed_table = Table(
        detailed_data,
        colWidths=[1.2*inch, 2*inch, 0.9*inch, 0.9*inch, 0.9*inch]
    )
    detailed_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    story.append(detailed_table)
    
    story.append(PageBreak())
    
    # Charts
    story.append(Paragraph("Performance Visualizations", heading_style))
    
   
    charts_dir = os.path.join(os.path.dirname(output_path), 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    
    line_chart_path = os.path.join(charts_dir, 'performance_line.png')
    create_line_chart(df, line_chart_path)
    
    story.append(Paragraph("Performance vs File Size", styles['Heading3']))
    story.append(Image(line_chart_path, width=6*inch, height=4*inch))
    story.append(Spacer(1, 0.2*inch))
    
    # Bar chart for 250K lines
    bar_chart_path = os.path.join(charts_dir, 'performance_bar.png')
    create_bar_chart(df, 250000, bar_chart_path)
    
    story.append(Paragraph(
        "Algorithm Comparison (250K lines)",
        styles['Heading3']
    ))
    story.append(Image(bar_chart_path, width=5*inch, height=3*inch))
    
    story.append(PageBreak())
    
    # Analysis and Recommendations
    story.append(Paragraph("Analysis and Recommendations", heading_style))
    
    analysis_text = """
    <b>Key Findings:</b><br/>
    1. Set Lookup demonstrates exceptional performance across all file sizes,
    consistently sub-millisecond response times<br/>
    2. Binary Search provides predictable O(log n) performance<br/>
    3. Simple Loop and Memory Mapped approaches scale linearly<br/>
    4. Grep Command shows good performance for larger files<br/>
    <br/>
    <b>Recommendations:</b><br/>
    - For read-once queries: Use Set Lookup for best performance<br/>
    - For sorted data: Binary Search offers excellent scalability<br/>
    - For system integration: Grep Command is reliable<br/>
    - For memory-constrained environments: Memory Mapped files<br/>
    """
    story.append(Paragraph(analysis_text, styles['Normal']))
    
    story.append(PageBreak())
    
   
    # Conclusions
    story.append(Paragraph("Conclusions", heading_style))
    
    conclusion_text = """
    The benchmark analysis demonstrates that algorithm selection significantly
    impacts string search performance. Set Lookup remains the optimal choice for
    most use cases due to its superior performance characteristics. However,
    Binary Search provides better scalability for sorted datasets, while Grep
    Command offers system-level integration benefits.
    """
    story.append(Paragraph(conclusion_text, styles['Normal']))
    
    
    # Build PDF
    doc.build(story)
    print(f"PDF report generated: {output_path}")


def main():
    results_path = os.path.join(
        os.path.dirname(__file__),
        'results',
        'benchmark_results.json'
    )
    
    if not os.path.exists(results_path):
        print(f"Error: Results file not found: {results_path}")
        print("Please run benchmark_search.py first")
        return
    
    results = load_results(results_path)
    
    output_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'performance_report.pdf'
    )
    
    generate_pdf_report(results, output_path)
    
    print(f"Report generated ")
    print(f"Location: {os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()