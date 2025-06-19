import base64
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
from matplotlib.cm import get_cmap
from IPython.display import Image
from PIL import Image as PILImage

def pie_chart(ax, top_x, top_y):
    cmap = get_cmap("tab20")
    labels = [f'{x} ({y:.2f})' for x, y in zip(top_x, top_y)]
    ax.pie(top_y, labels=labels, colors=cmap.colors[:len(top_x)], textprops={'color': 'white'})
    ax.set_facecolor('black')
    ax.set_ylabel('', visible=False)

def plot_and_encode_dashboard(plot_funcs, x_values, y_values, chart_types):
    num_charts = len(plot_funcs)
    if num_charts == 0:
        return None

    rows, cols = (1, num_charts) if num_charts <= 2 else (2, (num_charts + 1) // 2)
    fig = plt.figure(figsize=(12, 6))
    fig.patch.set_facecolor('black')
    gs = gridspec.GridSpec(rows, cols)

    for i in range(num_charts):
        ax = plt.Subplot(fig, gs[i])
        ax.set_facecolor('black')
        ax.tick_params(axis='x', colors='white', rotation=45)
        ax.tick_params(axis='y', colors='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.2f'))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(prune='lower'))

        chart_type = chart_types[i]
        x = x_values[i]
        y = y_values[i]
        plot_funcs[i](ax)

        if chart_type in ("bar", "line", "barh"):
            for j, val in enumerate(y):
                ax.text(x[j] if chart_type != "barh" else val,
                        val if chart_type != "barh" else x[j],
                        f'{val:.2f}',
                        ha='center' if chart_type != "barh" else 'left',
                        va='bottom' if chart_type != "barh" else 'center',
                        color='white', fontsize=8)

        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
        for spine in ['bottom', 'left']:
            ax.spines[spine].set_color('white')

        fig.add_subplot(ax)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode()
    buffer.seek(0)

    # ✅ Return a PIL image for compatibility with Streamlit
    return PILImage.open(buffer)
