from bokeh.models.annotations import Title

# Note: The functions below are written for intraday data and assumes date, high, open, close, low columns.

def draw_price(p, df, width = 40000):
    inc = df.close > df.open
    dec = df.open > df.close
    mids = (df.open + df.close)/2
    spans = abs(df.close - df.open)
    p.segment(df.date, df.high, df.date, df.low, color="black")
    p.rect(df.date[inc], mids[inc], width, spans[inc], fill_color="#26A69A", line_color="black")
    p.rect(df.date[dec], mids[dec], width, spans[dec], fill_color="#EF5350", line_color="black")
    return(p)

def draw_volume(p, df, centered=False, width = 40000):
    inc = df.close > df.open
    dec = df.open > df.close
    df['sclaed_volume'] = df.volume * (((df.high.max() - df.low.min()) / 1.2) / df.volume.max())
    y_inc = y_dec = df.low.min()
    centered = True
    if not centered:
        y_inc +=  df.sclaed_volume[inc] / 2 + 0.0001
        y_dec +=  df.sclaed_volume[dec] / 2 + 0.0001
    p.rect(df.date[inc], y_inc, width, df.sclaed_volume[inc], fill_color="#26A69A", line_color="black", alpha=0.3)
    p.rect(df.date[dec], y_dec, width, df.sclaed_volume[dec], fill_color="#EF5350", line_color="black", alpha=0.3)
    return(p)
    
def set_title(p, ticker):
    t = Title()
    t.text = ticker
    p.title = t
    return(p)
