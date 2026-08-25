#!/usr/bin/env python
# coding: utf-8

# In[5]:


import io
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def load_raw_excel(file_path):
    df_raw = pd.read_excel(file_path)
    if df_raw.shape[1] == 1:
        text_data = "\n".join(
            [str(df_raw.columns[0])] + df_raw.iloc[:, 0].astype(str).tolist()
        )
        return pd.read_csv(io.StringIO(text_data))
    return df_raw


# Pop up file picker windows to select your 3 Excel files manually
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

print("Select 'multi_channel_traffic.xlsx':")
df_traffic = load_raw_excel(
    filedialog.askopenfilename(title="Select multi_channel_traffic.xlsx")
)

print("Select 'monthly_organic_performance.xlsx':")
df_organic = load_raw_excel(
    filedialog.askopenfilename(title="Select monthly_organic_performance.xlsx")
)

print("Select 'technical_audit.xlsx':")
df_audit = load_raw_excel(
    filedialog.askopenfilename(title="Select technical_audit.xlsx")
)

# Clean column headers
for df in [df_traffic, df_organic, df_audit]:
    df.columns = df.columns.str.strip()

print("All files loaded and cleaned successfully!")


# In[18]:


import warnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

get_ipython().run_line_magic('matplotlib', 'inline')
warnings.filterwarnings("ignore")

# 1. Clean Data & Sort
df_traffic.columns = [str(col).strip().lower() for col in df_traffic.columns]


def get_col(df, possible_names):
    for name in possible_names:
        for col in df.columns:
            if name in col:
                return col
    return None


channel_col = get_col(df_traffic, ["channel group", "channel_group", "channel"])
revenue_col = get_col(df_traffic, ["total revenue", "revenue", "total_revenue"])

df_traffic[revenue_col] = (
    df_traffic[revenue_col]
    .astype(str)
    .str.replace(",", "", regex=False)
    .str.replace("$", "", regex=False)
)
df_traffic[revenue_col] = pd.to_numeric(df_traffic[revenue_col], errors="coerce")
df_traffic[channel_col] = (
    df_traffic[channel_col].astype(str).str.strip().str.title()
)

df_traffic = df_traffic.sort_values(by=revenue_col, ascending=False).reset_index(
    drop=True
)

# 2. Setup Figure
fig, ax = plt.subplots(figsize=(10, 7.5), dpi=300)

colors = [
    "#2b5c8f",
    "#d95f02",
    "#7570b3",
    "#e7298a",
    "#66a61e",
    "#e6ab02",
    "#a6761d",
    "#1b9e77",
    "#666666",
    "#17becf",
]

wedges, texts = ax.pie(
    df_traffic[revenue_col],
    startangle=140,
    colors=colors[: len(df_traffic)],
    wedgeprops=dict(width=0.35, edgecolor="white", linewidth=2),
)

total_rev = df_traffic[revenue_col].sum()

# 3. Add Line Pointers for Every Channel (including Paid Other)
kw = dict(arrowprops=dict(arrowstyle="-", color="#666666", lw=1.2), zorder=0)

for i, p in enumerate(wedges):
    ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
    y = np.sin(np.deg2rad(ang))
    x = np.cos(np.deg2rad(ang))

    horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
    connectionstyle = f"angle,angleA=0,angleB={ang:.1f}"
    kw["arrowprops"]["connectionstyle"] = connectionstyle

    channel_name = df_traffic[channel_col].iloc[i]
    percentage = (df_traffic[revenue_col].iloc[i] / total_rev) * 100
    label_text = f"{channel_name}: {percentage:.1f}%"

    ax.annotate(
        label_text,
        xy=(x * 0.82, y * 0.82),
        xytext=(1.25 * np.sign(x), 1.25 * y),
        horizontalalignment=horizontalalignment,
        fontsize=10,
        fontweight="bold",
        color="#222222",
        **kw,
    )

# Prominent Top Title
ax.set_title(
    "Total Revenue Share by Marketing Channel",
    fontsize=16,
    fontweight="bold",
    pad=40,
)
plt.tight_layout()

# Save FIRST, then SHOW
plt.savefig("visual_1_final_labeled.png", dpi=300, bbox_inches="tight")
plt.show()


# In[19]:


import warnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

get_ipython().run_line_magic('matplotlib', 'inline')
warnings.filterwarnings("ignore")

# 1. Standardize Data & Cleanup for df_organic
df_organic.columns = [str(c).strip().lower() for c in df_organic.columns]
month_col = get_col(df_organic, ["month", "date"])
sessions_col = get_col(df_organic, ["organic sessions", "sessions", "organic"])

df_organic[sessions_col] = pd.to_numeric(
    df_organic[sessions_col].astype(str).str.replace(",", "", regex=False),
    errors="coerce",
)

# 2. Build High-End Line Chart
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)

plt.plot(
    df_organic[month_col],
    df_organic[sessions_col],
    marker="o",
    color="#d9534f",
    linewidth=3,
    markersize=8,
    markerfacecolor="#ffffff",
    markeredgewidth=2,
)

# Highlight Area Under Curve
plt.fill_between(
    df_organic[month_col], df_organic[sessions_col], color="#d9534f", alpha=0.1
)

# Title & Styling
plt.title(
    "12-Month Organic Traffic Decay Trend",
    fontsize=16,
    fontweight="bold",
    pad=25,
)
plt.xlabel("Month", fontsize=11, fontweight="bold", labelpad=10)
plt.ylabel("Organic Sessions", fontsize=11, fontweight="bold", labelpad=10)
plt.xticks(rotation=45, fontsize=10)
plt.grid(True, linestyle="--", alpha=0.5, zorder=0)

# Add exact value labels on key points
for i, txt in enumerate(df_organic[sessions_col]):
    if i % 2 == 0 or i == len(df_organic) - 1:  # Show labels sparingly
        plt.annotate(
            f"{int(txt):,}",
            (df_organic[month_col].iloc[i], df_organic[sessions_col].iloc[i]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
            fontsize=9,
            color="#222222",
            fontweight="bold",
        )

sns.despine(top=True, right=True)
plt.tight_layout()

# Save image FIRST, then SHOW
plt.savefig("visual_2_organic_decay_final.png", dpi=300, bbox_inches="tight")
plt.show()


# In[29]:


import io
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

get_ipython().run_line_magic('matplotlib', 'inline')

# 1. Clean Data
csv_raw_data = """issue_id,issue_type,category,affected_pages
1,URL Too Long,Metadata,348
2,Meta Noindex,Warnings,330
3,Description Too Long,Metadata,222
4,Missing or Invalid H1,Content,150
5,Title Too Long,Metadata,70
6,Missing Description,Metadata,53
7,Duplicate Content,Content,22
8,4xx Error,Critical,7"""

df = pd.read_csv(io.StringIO(csv_raw_data))
df = df.sort_values(by="affected_pages", ascending=False).reset_index(drop=True)

# 2. Render Figure
plt.figure(figsize=(10, 6), dpi=300)

ax = sns.barplot(
    data=df,
    x="affected_pages",
    y="issue_type",
    palette="Reds_r",
    edgecolor="none",
)

# 3. Y-Axis Labeling & Y-Axis Title Setup
plt.ylabel("Technical Issue", fontsize=11, fontweight="bold", labelpad=15)
plt.yticks(fontsize=10.5, fontweight="bold", color="#222222")

# 4. Add Page Counts cleanly at the end of each bar ONLY
for i, p in enumerate(ax.patches):
    width = p.get_width()
    ax.annotate(
        f" {int(width):,} pages",
        (width, p.get_y() + p.get_height() / 2),
        ha="left",
        va="center",
        fontsize=10,
        fontweight="bold",
        color="#333333",
    )

plt.title(
    "Technical SEO Issues Prioritized by Affected Pages",
    fontsize=15,
    fontweight="bold",
    pad=20,
)
plt.xlabel("Affected Pages Count", fontsize=11, fontweight="bold", labelpad=10)

# Expand x-limit slightly so outer labels don't cut off
plt.xlim(0, max(df["affected_pages"]) * 1.15)

sns.despine(top=True, right=True)
plt.grid(axis="x", linestyle="--", alpha=0.3)
plt.tight_layout()

plt.savefig("visual_3_perfect.png", dpi=300, bbox_inches="tight")
plt.show()


# In[ ]:




