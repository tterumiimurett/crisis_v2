import json
import collections
from pathlib import Path
import numpy as np

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def calculate_time_overlaps(data):
    """
    Calculates the total duration covered by 1, 2, or 3 distinct annotators.
    """
    total_duration_by_count = collections.defaultdict(float)
    
    for item_id, entries in data.items():
        if not entries:
            continue
            
        events = []
        for entry in entries:
            if 'completed_by' not in entry:
                continue
            start = float(entry['start'])
            end = float(entry['end'])
            ann = str(entry['completed_by']) 
            
            if end <= start:
                continue
            events.append((start, 1, ann))
            events.append((end, -1, ann))
            
        if not events:
            continue
            
        events.sort()
        
        active_annotators = collections.defaultdict(int) # annotator -> count of active segments
        current_distinct_count = 0
        prev_time = events[0][0]
        
        for time, change, ann in events:
            duration = time - prev_time
            if duration > 0 and current_distinct_count > 0:
                total_duration_by_count[current_distinct_count] += duration
            
            # Update state
            active_annotators[ann] += change
            # Recalculate distinct count
            current_distinct_count = sum(1 for k, v in active_annotators.items() if v > 0)
            prev_time = time
            
    return total_duration_by_count

def classify_segments(data):
    """
    Classifies each segment as Isolated (support=0), Partial (support=1), or Full (support=2).
    Support is defined as having >0 overlap with another annotator.
    Also detects "Split Chunk" scenarios.
    """
    
    stats = {
        'total_segments': 0,
        'isolated': 0,   # No overlap with any other annotator
        'partial': 0,    # Overlap with 1 other annotator
        'full': 0,       # Overlap with 2 other annotators
        'split_cases': 0 # This segment overlaps with >= 2 segments from a SINGLE other annotator
    }
    
    split_details = []
    
    unique_annotators_found = set()

    for item_id, entries in data.items():
        # Group by annotator
        annotator_segments = collections.defaultdict(list)
        for entry in entries:
            # Skip if missing key
            if 'completed_by' not in entry:
                continue
                
            ann_id = str(entry['completed_by']) # Force string for consistency
            unique_annotators_found.add(ann_id)
            
            annotator_segments[ann_id].append({
                'start': float(entry['start']),
                'end': float(entry['end']),
                'id': entry.get('id', 'unknown') 
            })
            
        all_annotators = ['1', '2', '3'] 
        
        # Check actual keys in data
        present_annotators = list(annotator_segments.keys())
        
        for ann in present_annotators:
            others = [x for x in all_annotators if x != ann]
            
            for seg in annotator_segments[ann]:
                stats['total_segments'] += 1
                start, end = seg['start'], seg['end']
                
                overlapping_annotators = set()
                is_split = False
                
                for other_ann in others:
                    # Find overlaps with this specific other annotator
                    overlaps_with_other = []
                    if other_ann in annotator_segments:
                        for other_seg in annotator_segments[other_ann]:
                            o_start, o_end = other_seg['start'], other_seg['end']
                            # Overlap check
                            if max(start, o_start) < min(end, o_end):
                                overlaps_with_other.append(other_seg)
                        
                        if overlaps_with_other:
                            overlapping_annotators.add(other_ann)
                        
                        if len(overlaps_with_other) >= 2:
                            is_split = True
                
                support_count = len(overlapping_annotators)
                if support_count == 0:
                    stats['isolated'] += 1
                elif support_count == 1:
                    stats['partial'] += 1
                elif support_count == 2:
                    stats['full'] += 1
                    
                if is_split:
                    stats['split_cases'] += 1
                    
    print(f"\nUnique Annotators Found in segments: {unique_annotators_found}")
    return stats

def main():
    data_path = Path("output/merged_by_id.json")
    if not data_path.exists():
        print(f"Error: {data_path} not found.")
        return

    data = load_data(data_path)
    
    # 1. Time Overlap Analysis
    print("Calculating Time Overlaps...")
    duration_stats = calculate_time_overlaps(data)
    total_annotated_time = sum(duration_stats.values())
    
    print("\n--- Time Agreement Stats ---")
    print(f"Total Annotated Duration (union): {total_annotated_time:.2f} seconds")
    for count in sorted(duration_stats.keys()):
        pct = (duration_stats[count] / total_annotated_time) * 100 if total_annotated_time else 0
        print(f"Covered by exactly {count} annotators: {duration_stats[count]:.2f} s ({pct:.2f}%)")

    # 2. Segment Analysis
    print("\nCalculating Segment Stats...")
    seg_stats = classify_segments(data)
    
    print("\n--- Segment Agreement Stats ---")
    total = seg_stats['total_segments']
    print(f"Total Segments Checked: {total}")
    if total > 0:
        print(f"Isolated (No overlap): {seg_stats['isolated']} ({seg_stats['isolated']/total*100:.2f}%)")
        print(f"Partial Support (1 matching ann): {seg_stats['partial']} ({seg_stats['partial']/total*100:.2f}%)")
        print(f"Full Support (2 matching anns): {seg_stats['full']} ({seg_stats['full']/total*100:.2f}%)")
        print(f"\nSplit Cases Detected: {seg_stats['split_cases']}")
        print(f"(One segment overlaps with >=2 segments from a single other annotator)")
        print(f"Rate: {seg_stats['split_cases']/total*100:.2f}%")

if __name__ == "__main__":
    main()
