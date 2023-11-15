from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import numpy as np
from collections import defaultdict

class DiagramCreator:
    def __init__(self):
        pass

    def create_diagram(self, sentiment_scores):
        DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        WEEKS_NUM = 53

        heatmap_data = defaultdict(lambda: np.full((len(DAYS), WEEKS_NUM), np.nan))
        for score in sentiment_scores:
            score_date = datetime.strptime(score["date"], "%Y-%m-%d")
            week_year, week_num, day_of_week = score_date.isocalendar()
            heatmap_data[week_year][day_of_week - 1, week_num - 1] = score["score"]

        # Iterate over each year to create separate plots
        for year, yearly_data in sorted(heatmap_data.items()):
            fig, ax = plt.subplots(figsize=(20, 3))

            # Create the heatmap
            norm = mcolors.TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1)
            cax = ax.matshow(yearly_data, cmap='RdYlGn', norm=norm)

            # Add grid lines
            for (i, j), _ in np.ndenumerate(yearly_data):
                ax.add_patch(mpatches.Rectangle((j-0.5, i-0.5), 1, 1, fill=False, edgecolor='gray', lw=0.5))

            # Set ticks and labels
            month_starts = [(datetime(year, m, 1) - datetime(year, 1, 1)).days // 7 for m in range(1, 13)]
            ax.set_xticks(month_starts)
            ax.set_xticklabels(MONTHS[:len(month_starts)])
            ax.set_yticks(np.arange(len(DAYS)))
            ax.set_yticklabels(DAYS)
            plt.setp(ax.get_xticklabels(), rotation=90)

            plt.colorbar(cax, orientation='horizontal', label='Sentiment Score', fraction=0.025, pad=0.07)

            plt.subplots_adjust(
                top=0.71,
                bottom=0.19,
            )

            # Set the title for each year's plot
            ax.set_title(f'Sentiment Heatmap for {year}')

            # Show the plot
            plt.show()
