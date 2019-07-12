from scipy.stats.stats import pearsonr
import numpy as np

def exponential_ma(values, t=5):
    # AlphaVantage uses 60 or 200 data points for each EMA.
    k = 2 / (t + 1)
    exp_ma = values[0]
    for v in values[1:]:
        exp_ma = k * v + (1 - k) * exp_ma
    return(exp_ma)

def compute_closeness_avg(df):
    avgs = []
    for i, row in df.iterrows():
        if len(avgs) == 0:
            avgs.append(row.closeness)
        else:
            avgs.append((len(avgs) * avgs[-1] + row.closeness) / (len(avgs) + 1))
    df['closeness_avg'] = avgs
    
def compute_closeness_sma_bollinger_bands(df, t=5, f=2):
    # Here, t is window size and f is standard deviation which is usually 2 but could be increased for safety.
    mid_band = []
    upper_band = []
    lower_band = []
    l = len(df.index)
    for i in range(t):
        mid_band.append(0)
        upper_band.append(0)
        lower_band.append(0)
    c = 0
    while (c + t) < l:
        # Here, the mid is calculated as Simple MA over tp.
        # Be aware that Bollinger Bands does SMA of Closeness SMA here.
        mid = df.iloc[c + t].closeness_sma
        mid_band.append(mid)
        upper_band.append(mid + f * df.iloc[c : (c + t)].closeness_sma.std())
        lower_band.append(mid - f * df.iloc[c : (c + t)].closeness_sma.std())
        c += 1
    df['mid_band'] = mid_band
    df['upper_band'] = upper_band
    df['lower_band'] = lower_band    

def draw_closeness_sma_bollinger_bands(p, df):
    p.line('date', 'upper_band', source = ColumnDataSource(df), line_color="gray", alpha=0.4)
    p.line('date', 'mid_band', source = ColumnDataSource(df), line_color="orange")
    p.line('date', 'lower_band', source = ColumnDataSource(df), line_color="gray", alpha=0.4)
    return(p)

def compute_reds_and_greens(df):
    mode = ''
    reds = {'date' : [], 'value' : []}
    greens = {'date' : [], 'value' : []}
    ref_x = -1
    ref_y = s_y = b_y = -1
    angles = []
    for i, row in df.iterrows():
        if mode == '':
            ref_x = row.date
            if row.b > row.s:
                mode = 'b'
                ref_y = row.b_ema
            else:
                mode = 's'
                ref_y = row.s_ema
        if row.b > row.s:
            b_y = row.b_ema
            if mode == 's':
                mode = 'b'
                reds['date'].append(row.date)
                reds['value'].append(row.b_ema)
                ref_x = row.date
                ref_y = row.b_ema
            if (row.date - ref_x).seconds != 0:
                theta_b = math.tanh((b_y - ref_y)/(row.date - ref_x).seconds)
                theta_s = math.tanh((s_y - ref_y)/(row.date - ref_x).seconds)
                del_theta = theta_b - theta_s
                angles.append(abs(del_theta))
            else:
                angles.append(0)
        if row.s > row.b:
            s_y = row.s_ema
            if mode == 'b':
                mode = 's'
                greens['date'].append(row.date)
                greens['value'].append(row.s_ema)
                ref_x = row.date
                ref_y = row.s_ema
            if (row.date - ref_x).seconds != 0:
                theta_b = math.tanh((b_y - ref_y)/(row.date - ref_x).seconds)
                theta_s = math.tanh((s_y - ref_y)/(row.date - ref_x).seconds)
                del_theta = theta_b - theta_s
                angles.append(abs(del_theta))
            else:
                angles.append(0)
#     df['angle'] = angles
#     df.angle = (df.angle / df.angle.max()) * 100
    return(reds, greens)

def compute_reds_and_greens_on_prices(df):
    mode = ''
    reds = {'date' : [], 'value' : []}
    greens = {'date' : [], 'value' : []}
    for i, row in df.iterrows():
        if mode == '':
            if row.b > row.s:
                mode = 'b'
            else:
                mode = 's'
        if row.b > row.s and mode == 's':
            mode = 'b'
            reds['date'].append(row.date)
            reds['value'].append(row.close)
        if row.s > row.b and mode == 'b':
            mode = 's'
            greens['date'].append(row.date)
            greens['value'].append(row.close)
    return(reds, greens)

def compute_blues(df):
    blues = {'date' : [], 'value' : [], 'price' : []} 
    count = 0
    for i, row in df.iterrows():
        count += 1
        if count == len(df.index) - 1:
            break
        if df.iloc[count - 1].rolling_corr_gradients > -50 and df.iloc[count + 1].rolling_corr_gradients < -50:
            blues['date'].append(row.date)
            blues['value'].append(row.rolling_correlation)
            blues['price'].append(row.close)
        elif df.iloc[count - 1].rolling_corr_gradients < -50 and df.iloc[count + 1].rolling_corr_gradients > -50:
            blues['date'].append(row.date)
            blues['value'].append(row.rolling_correlation)
            blues['price'].append(row.close)
    return(blues)
    
def compute_river(df):
    river_up = []
    for i, row in df.iterrows():
        river_up.append(max(row.b_ema, row.s_ema))
    df['river_up'] = river_up
    
def compute_correlation(df):
    cor = [0, 0]
    for i in range(2, len(df.index)):
      cor.append(pearsonr(df.iloc[0 : i].river_up.tolist(), df.iloc[0 : i].closeness_sma.tolist())[0])
    df['cor'] = cor
    df.cor = df.cor.fillna(0)
    df.cor = df.cor * 100
    
def compute_rolling_correlation(df, t=60):
    rolling_correlation = []
    l = len(df.index)
    for i in range(t):
        rolling_correlation.append(0)
    c = 0
    while (c + t) < l:
        rolling_correlation.append(pearsonr(df.iloc[c : (c + t)].river_up.tolist(), df.iloc[c : (c + t)].closeness_sma.tolist())[0])
        c += 1
    df['rolling_correlation'] = rolling_correlation
    df.rolling_correlation = df.rolling_correlation * 100
    df['rolling_corr_gradients'] = np.tanh(np.gradient(df.rolling_correlation))
    df.rolling_corr_gradients = (df.rolling_corr_gradients) * 100

def compute_rate(values):
    return((values[1] - values[0]) / values[0])

def define_rates(df):
    df['open_rate'] = df.open.rolling(window=(2)).apply(compute_rate, raw=True).fillna(0)
    df['high_rate'] = df.high.rolling(window=(2)).apply(compute_rate, raw=True).fillna(0)
    df['low_rate'] = df.low.rolling(window=(2)).apply(compute_rate, raw=True).fillna(0)
    df['close_rate'] = df.close.rolling(window=(2)).apply(compute_rate, raw=True).fillna(0)
    df['volume_rate'] = df.volume.rolling(window=(2)).apply(compute_rate, raw=True).fillna(0)

def compute_momentums_and_derivatives(df, power = 1, ratio = 0.96):
    define_rates(df)
    df['spread'] = df.close - df.open
    df['spread_rate'] = df.close_rate - df.open_rate
    s = []
    b = []
    closeness = []
    seller, buyer = 0, 0
    for index, row in df.iterrows():
        spread = row['spread']
        # spread = row['spread_rate']
        if spread > 0:
            buyer = buyer * ratio + (1-ratio) * (spread ** power)
        else:
            spread = -spread
            seller = seller * ratio + (1-ratio) * (spread ** power)
        s.append(seller)
        b.append(buyer)
        closeness.append(abs((buyer - seller)))
    # Note here SMA introduces delay.
    t = 5
    df['s'] = s
    df['s_ema'] = df.s.rolling(window=(t)).apply(exponential_ma, args=(t,), raw=True).fillna(0)
    df['b'] = b
    df['b_ema'] = df.b.rolling(window=(t)).apply(exponential_ma, args=(t,), raw=True).fillna(0)
    df['closeness'] = closeness
    df['closeness_sma'] = df.closeness.rolling(window=(t)).mean().fillna(0)
    # compute_closeness_avg(df)
    eta = df.b_ema.max() + df.s_ema.max()
    df.b_ema = (df.b_ema / eta) * 100
    df.s_ema = (df.s_ema / eta) * 100
    df.closeness_sma = (df.closeness_sma / eta) * 100
    # df.closeness_sma = df.closeness_sma.fillna(0)
    compute_river(df)
    # compute_correlation(df)
    compute_rolling_correlation(df, t=40)
    df['0'] = [0] * len(df.date)
    df['50'] = [50] * len(df.date)
    df['-50'] = [-50] * len(df.date)


