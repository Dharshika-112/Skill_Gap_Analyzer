#!/usr/bin/env python3
"""
Analyze the job dataset to understand its structure
"""

import pandas as pd
import numpy as np

def analyze_dataset():
    df = pd.read_csv('backend/data/raw/job_dataset.csv')
    
    print("📊 JOB DATASET ANALYSIS")
    print("=" * 50)
    print(f"Total jobs: {len(df)}")
    print(f"Unique titles: {df['Title'].nunique()}")
    print(f"Experience levels: {df['ExperienceLevel'].unique()}")
    print(f"Columns: {list(df.columns)}")
    
    print("\n🎯 SAMPLE JOB TITLES:")
    unique_titles = df['Title'].unique()
    for i, title in enumerate(unique_titles[:15]):
        print(f"  {i+1}. {title}")
    
    print(f"\n📈 EXPERIENCE LEVEL DISTRIBUTION:")
    exp_counts = df['ExperienceLevel'].value_counts()
    for level, count in exp_counts.items():
        print(f"  {level}: {count} jobs")
    
    print(f"\n🔧 SAMPLE SKILLS FROM FIRST FEW JOBS:")
    for i in range(min(3, len(df))):
        skills = df.iloc[i]['Skills']
        title = df.iloc[i]['Title']
        print(f"  {title}: {skills[:100]}...")
    
    return df

if __name__ == "__main__":
    df = analyze_dataset()