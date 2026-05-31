"""
utils/analytics.py
Generates charts for the dashboard using Matplotlib (base64 PNG embedded in HTML).
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import base64
import io

COLORS = ['#00ff88', '#00bfff', '#ff6b6b', '#ffd93d', '#c77dff', '#ff9a3c']
BG_COLOR  = '#0d0d15'
CARD_COLOR = '#111120'
GRID_COLOR = '#1e1e35'
TEXT_COLOR = '#a0a0b0'
TITLE_COLOR = '#ffffff'


def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', facecolor=BG_COLOR, dpi=120)
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f'<img src="data:image/png;base64,{img}" style="width:100%;border-radius:8px;" />'


def no_data_html(msg="No workout data yet. Add workouts to see analytics!"):
    return f'<div style="padding:3rem;text-align:center;color:#a0a0b0;">📊 {msg}</div>'


def setup_axes(ax, title, xlabel='', ylabel=''):
    ax.set_facecolor(BG_COLOR)
    ax.set_title(title, color=TITLE_COLOR, fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel(xlabel, color=TEXT_COLOR, fontsize=9)
    ax.set_ylabel(ylabel, color=TEXT_COLOR, fontsize=9)
    ax.tick_params(colors=TEXT_COLOR, labelsize=8)
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines['left'].set_color(GRID_COLOR)
    ax.spines['bottom'].set_color(GRID_COLOR)
    ax.grid(True, color=GRID_COLOR, alpha=0.7, linewidth=0.8)


def calories_chart(workouts):
    if not workouts:
        return no_data_html()
    df = pd.DataFrame(workouts)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    fig, ax = plt.subplots(figsize=(9, 4), facecolor=BG_COLOR)
    ax.plot(df['date'], df['calories'], color=COLORS[0], linewidth=2.5, marker='o', markersize=6, zorder=5)
    ax.fill_between(df['date'], df['calories'], alpha=0.12, color=COLORS[0])
    setup_axes(ax, 'Calories Burned Over Time', 'Date', 'Calories')
    plt.xticks(rotation=30)
    plt.tight_layout()
    return fig_to_base64(fig)


def workout_frequency_chart(workouts):
    if not workouts:
        return no_data_html()
    df = pd.DataFrame(workouts)
    counts = df['workout_type'].value_counts()
    fig, ax = plt.subplots(figsize=(9, 4), facecolor=BG_COLOR)
    bars = ax.bar(counts.index, counts.values, color=COLORS[:len(counts)], alpha=0.85, width=0.6, zorder=3)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(int(bar.get_height())), ha='center', va='bottom', color=TITLE_COLOR, fontsize=9, fontweight='bold')
    setup_axes(ax, 'Workout Frequency by Type', 'Type', 'Sessions')
    plt.xticks(rotation=20, ha='right')
    plt.tight_layout()
    return fig_to_base64(fig)


def duration_chart(workouts):
    if not workouts:
        return no_data_html()
    df = pd.DataFrame(workouts)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    fig, ax = plt.subplots(figsize=(9, 4), facecolor=BG_COLOR)
    ax.plot(df['date'], df['duration_min'], color=COLORS[3], linewidth=2.5, marker='s', markersize=6)
    ax.fill_between(df['date'], df['duration_min'], alpha=0.12, color=COLORS[3])
    avg = df['duration_min'].mean()
    ax.axhline(y=avg, color=COLORS[2], linestyle='--', linewidth=1.5, alpha=0.7, label=f'Avg: {avg:.1f} min')
    ax.legend(facecolor=CARD_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    setup_axes(ax, 'Workout Duration Over Time', 'Date', 'Minutes')
    plt.xticks(rotation=30)
    plt.tight_layout()
    return fig_to_base64(fig)


def weekly_progress_chart(workouts):
    if not workouts or len(workouts) < 2:
        return no_data_html("Need more workouts to show weekly progress.")
    df = pd.DataFrame(workouts)
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.strftime('W%U')
    weekly = df.groupby('week').agg(total_calories=('calories', 'sum'), sessions=('id', 'count')).reset_index()
    fig, ax1 = plt.subplots(figsize=(9, 4), facecolor=BG_COLOR)
    ax2 = ax1.twinx()
    x = np.arange(len(weekly))
    ax1.bar(x - 0.2, weekly['total_calories'], width=0.4, color=COLORS[0], alpha=0.8, label='Calories', zorder=3)
    ax2.plot(x + 0.2, weekly['sessions'], color=COLORS[2], linewidth=2.5, marker='o', markersize=8, label='Sessions')
    ax1.set_xticks(x)
    ax1.set_xticklabels(weekly['week'], rotation=20)
    setup_axes(ax1, 'Weekly Progress', 'Week', 'Calories')
    ax2.tick_params(colors=TEXT_COLOR, labelsize=8)
    ax2.set_ylabel('Sessions', color=TEXT_COLOR, fontsize=9)
    ax2.spines[['top', 'right']].set_color(GRID_COLOR)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, facecolor=CARD_COLOR, edgecolor=GRID_COLOR, labelcolor=TEXT_COLOR)
    plt.tight_layout()
    return fig_to_base64(fig)
