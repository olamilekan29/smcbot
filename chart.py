import mplfinance as mpf
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def generate_chart(signal, filename="chart.png"):
    df   = signal["df_15m"].set_index("time").tail(80)
    ob   = signal["ob"]
    fvg  = ob["fvg"]

    # Dark background style
    mc   = mpf.make_marketcolors(up="#26a69a", down="#ef5350",
                                  wick="inherit", edge="inherit")
    style = mpf.make_mpf_style(marketcolors=mc, facecolor="#0d0d0d",
                                gridcolor="#1e1e1e", figcolor="#0d0d0d")

    fig, axes = mpf.plot(
        df,
        type="candle",
        style=style,
        figsize=(14, 7),
        returnfig=True
    )

    ax = axes[0]

    # Draw OB zone
    ob_color = "#00e676" if "Bullish" in ob["type"] else "#ff1744"
    ob_patch = mpatches.FancyArrowPatch
    ax.axhspan(ob["bottom"], ob["top"],
               alpha=0.25, color=ob_color, label=f'{ob["type"]}')

    # Draw FVG zone
    ax.axhspan(fvg["bottom"], fvg["top"],
               alpha=0.15, color="cyan", label="Fair Value Gap")

    # Entry / SL / TP lines
    ax.axhline(signal["entry"], color="white",  ls="--", lw=1.2,
               label=f'Entry: {signal["entry"]:.5f}')
    ax.axhline(signal["sl"],    color="#ff1744", ls="--", lw=1.2,
               label=f'SL: {signal["sl"]:.5f}')
    ax.axhline(signal["tp"],    color="#00e676", ls="--", lw=1.2,
               label=f'TP: {signal["tp"]:.5f}')

    ax.legend(loc="upper left", fontsize=8,
              facecolor="#1a1a1a", labelcolor="white")
    ax.set_title(
        f'{signal["symbol"]} 15M  |  {signal["signal"]}  |  '
        f'Bias: {signal["bias"].upper()}',
        color="white", fontsize=12, pad=10
    )

    plt.savefig(filename, bbox_inches="tight", dpi=150, facecolor="#0d0d0d")
    plt.close()
    return filename