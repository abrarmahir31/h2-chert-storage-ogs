"""Storage schedule shared by all models: one cushion-filling period, then
n cycles of (inject, rest, withdraw, rest). Times in seconds."""

DAY = 86400.0


def build(P, rate_flux):
    """Return dict with injection/withdrawal windows, the piecewise-linear
    injection curve (coords, values) scaled to `rate_flux`, switch times, t_end."""
    t, sw = 0.0, [0.0]
    inj, wd = [], []
    t_c = P["t_cushion"] * DAY
    inj.append((0.0, t_c)); t = t_c; sw.append(t)
    t += P["t_rest"] * DAY; sw.append(t)
    for _ in range(int(P["n_cycles"])):
        inj.append((t, t + P["t_inj"] * DAY)); t += P["t_inj"] * DAY; sw.append(t)
        t += P["t_rest"] * DAY; sw.append(t)
        wd.append((t, t + P["t_wd"] * DAY)); t += P["t_wd"] * DAY; sw.append(t)
        t += P["t_rest"] * DAY; sw.append(t)
    eps = 1.0  # 1-second ramps keep the curve single-valued
    coords, values = [0.0], [rate_flux]
    for k, (t0, t1) in enumerate(inj):
        if k > 0:
            coords += [t0, t0 + eps]
            values += [0.0, rate_flux]
        coords += [t1, t1 + eps]
        values += [rate_flux, 0.0]
    coords.append(t + 1e6)
    values.append(0.0)
    return dict(inj=inj, wd=wd, switch=sw, t_end=t, coords=coords, values=values)


def output_times(s, every_days=10):
    n = int(s["t_end"] / (every_days * DAY))
    ts = set(s["switch"]) | {k * every_days * DAY for k in range(1, n + 1)}
    return sorted(x for x in ts if 0 < x <= s["t_end"])


def dirichlet_windows_xml(s, mesh, parameter):
    return "".join(f"""
                <boundary_condition><mesh>{mesh}</mesh><type>DirichletWithinTimeInterval</type>
                    <parameter>{parameter}</parameter>
                    <time_interval><start>{t0:.1f}</start><end>{t1:.1f}</end></time_interval>
                </boundary_condition>""" for t0, t1 in s["wd"])
