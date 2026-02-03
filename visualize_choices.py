import pandas as pd
import json
import ast
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style
sns.set_theme(style="whitegrid")

# File paths
INPUT_FILE = 'output/choices数据.json'
OUTPUT_DIR = 'plots'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_and_process_data():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # helper to parse string list
    def parse_choices(x):
        try:
            return ast.literal_eval(x)
        except:
            return []

    # Explode choices so each row is a single choice instance
    # This makes counting and grouping easy
    # We keep original columns for grouping
    df['choices_list'] = df['choices'].apply(parse_choices)
    df_exploded = df.explode('choices_list')
    df_exploded = df_exploded.rename(columns={'choices_list': 'choice'})
    
    return df_exploded

def plot_normalized_distribution(df, x_col, group_col=None, title="", filename="plot.png", layout=None):
    """
    Plots normalized distribution of x_col.
    If group_col is provided, creates subplots or grouped bar chart.
    Here we specifically want separate subplots for the "side by side" requirement.
    """
    
    # Calculate counts
    if group_col:
        # Calculate frequency per group
        # count of (group, choice) / count of (group)
        counts = df.groupby([group_col, x_col]).size().reset_index(name='count')
        total_counts = df.groupby([group_col]).size().reset_index(name='total')
        counts = counts.merge(total_counts, on=group_col)
        counts['frequency'] = counts['count'] / counts['total']
        
        # Get unique groups to order them
        groups = sorted(df[group_col].dropna().unique())
        
        # Setup plot
        if layout:
            nrows, ncols = layout
        else:
            nrows, ncols = 1, len(groups)
            
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(5*ncols, 5*nrows), sharey=True)
        if nrows * ncols == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
            
        for i, group in enumerate(groups):
            ax = axes[i]
            subset = counts[counts[group_col] == group]
            sns.barplot(data=subset, x=x_col, y='frequency', hue=x_col, ax=ax, palette='viridis', legend=False)
            ax.set_title(f"{group_col}: {group}")
            ax.set_ylim(0, 1) # Normalized 0-1
            ax.set_ylabel("Frequency")
            
        # Hide empty subplots
        for j in range(len(groups), len(axes)):
            axes[j].axis('off')
            
        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, filename))
        print(f"Saved {filename}")
        
    else:
        # Overall
        counts = df[x_col].value_counts(normalize=True).reset_index()
        counts.columns = [x_col, 'frequency']
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=counts, x=x_col, y='frequency', hue=x_col, palette='viridis', legend=False)
        plt.title(title)
        plt.ylabel("Frequency")
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, filename))
        print(f"Saved {filename}")

def plot_interaction(df):
    # Annotator x Crisis Level
    # We want a 3x3 grid (assuming 3 annotators, 3 levels)
    # Rows: Annotator (completed_by), Cols: Crisis Level (crisis_level)
    
    # Calculate frequencies per (completed_by, crisis_level)
    counts = df.groupby(['completed_by', 'crisis_level', 'choice']).size().reset_index(name='count')
    totals = df.groupby(['completed_by', 'crisis_level']).size().reset_index(name='total')
    counts = counts.merge(totals, on=['completed_by', 'crisis_level'])
    counts['frequency'] = counts['count'] / counts['total']
    
    annotators = sorted(df['completed_by'].unique())
    levels = sorted(df['crisis_level'].unique())
    
    nrows = len(annotators)
    ncols = len(levels)
    
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(4*ncols, 4*nrows), sharey=True, sharex=True)
    
    for i, ann in enumerate(annotators):
        for j, lvl in enumerate(levels):
            if nrows > 1 and ncols > 1:
                ax = axes[i, j]
            elif nrows > 1: # Single column
                ax = axes[i]
            elif ncols > 1: # Single row
                ax = axes[j]
            else:
                ax = axes
                
            subset = counts[(counts['completed_by'] == ann) & (counts['crisis_level'] == lvl)]
            
            if not subset.empty:
                sns.barplot(data=subset, x='choice', y='frequency', hue='choice', ax=ax, palette='viridis', legend=False)
            
            ax.set_title(f"Ann: {ann}, Lvl: {lvl}")
            if j == 0:
                ax.set_ylabel("Frequency")
            else:
                ax.set_ylabel("")
            if i == nrows - 1:
                ax.set_xlabel("Choice")
            else:
                ax.set_xlabel("")
            ax.set_ylim(0, 1)

    plt.suptitle("Choice Distribution by Annotator and Crisis Level")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "plot4_interaction.png"))
    print("Saved plot4_interaction.png")

def main():
    print("Loading data...")
    df = load_and_process_data()
    print(f"Loaded {len(df)} rows (exploded choices)")
    
    # 1. Overall
    print("Generating Plot 1...")
    plot_normalized_distribution(df, x_col='choice', title="Overall Choice Distribution", filename="plot1_overall.png")
    
    # 2. By Annotator (completed_by)
    print("Generating Plot 2...")
    # Assuming 3 annotators, layout 1x3
    plot_normalized_distribution(df, x_col='choice', group_col='completed_by', title="Distribution by Annotator", filename="plot2_by_annotator.png", layout=(1, 3))
    
    # 3. By Crisis Level (crisis_level)
    print("Generating Plot 3...")
    # Assuming 3 levels, layout 1x3
    plot_normalized_distribution(df, x_col='choice', group_col='crisis_level', title="Distribution by Crisis Level", filename="plot3_by_crisis.png", layout=(1, 3))
    
    # 4. Interaction
    print("Generating Plot 4...")
    plot_interaction(df)
    
    print("Done. Check 'plots' directory.")

if __name__ == "__main__":
    main()
